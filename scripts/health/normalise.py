"""Turn raw Garmin responses into minimal per-day numbers.

Every value is read from an exact, allowlisted path (see the field map in
README.md). Nothing else in a response is looked at: no names, places,
coordinates, IDs, elevation, or the "minutes after midnight" bedtime fields.
Timestamps are read in exactly one place, `startTimeLocal`, and only its
date is kept.

Out-of-range values become None rather than being published.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from .categories import group_for

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_ACTIVITY_SECONDS = 7 * 86400
MAX_ACTIVITY_METERS = 2_000_000

# Garmin's fastest split within a run, per distance: (key, field, fastest
# plausible, slowest kept) in seconds. Anything quicker than the world
# record is a GPS glitch and is dropped.
BEST_SPLITS = (
    ("1k", "fastestSplit_1000", 132, 1200),
    ("mile", "fastestSplit_1609", 223, 1930),
    ("5k", "fastestSplit_5000", 755, 6000),
    ("10k", "fastestSplit_10000", 1571, 12000),
)
BEST_KEYS = tuple(key for key, *_ in BEST_SPLITS)

DayValues = dict[date, dict[str, int | None]]


class NormaliseError(ValueError):
    """A response didn't have the expected shape. Carries a label only."""


@dataclass(frozen=True)
class Activity:
    """One workout, reduced to what the page needs. Lives in memory only."""

    day: date
    group: str
    km: float
    seconds: float
    moving_seconds: float
    load: float | None
    zones: tuple[float, float, float, float, float] | None = None  # seconds in HR zones 1-5
    bests: tuple[tuple[str, float], ...] = ()  # (BEST_KEYS key, seconds), runs only


def records(response: Any, key: str | None, label: str) -> list[dict]:
    """The list of records in a response: the top-level list, or the list under `key`."""
    if response is None:
        return []
    if key is None:
        items = response
    elif isinstance(response, dict):
        items = response.get(key) or []
    else:
        raise NormaliseError(f"{label}: unexpected response shape")
    if not isinstance(items, list):
        raise NormaliseError(f"{label}: unexpected response shape")
    return [item for item in items if isinstance(item, dict)]


def sleep_days(items: list[dict]) -> DayValues:
    """Per night, dated by the morning you wake (Garmin's calendarDate)."""
    out: DayValues = {}
    for item in items:
        day = _day(item.get("calendarDate"))
        seconds = _number(item.get("sleepTimeSeconds"), 1, 86400)
        if day is None or seconds is None:
            continue
        out[day] = {
            "sleep_min": round(seconds / 60),
            "sleep_score": _int(_get(item, "sleepScores", "overall", "value"), 0, 100),
            "deep_min": _minutes(item.get("deepSleepSeconds")),
            "light_min": _minutes(item.get("lightSleepSeconds")),
            "rem_min": _minutes(item.get("remSleepSeconds")),
            "awake_min": _minutes(item.get("awakeSleepSeconds")),
        }
    return out


def hrv_days(items: list[dict]) -> DayValues:
    out: DayValues = {}
    for item in items:
        day = _day(item.get("calendarDate"))
        value = _int(item.get("lastNightAvg"), 1, 300)
        if day is None or value is None:
            continue
        out[day] = {
            "hrv": value,
            "hrv_lo": _int(_get(item, "baseline", "balancedLow"), 1, 300),
            "hrv_hi": _int(_get(item, "baseline", "balancedUpper"), 1, 300),
        }
    return out


def rhr_days(items: list[dict]) -> DayValues:
    out: DayValues = {}
    for item in items:
        day = _day(item.get("calendarDate"))
        value = _int(_get(item, "heartRate", "restingValue"), 20, 150)
        if day is not None and value is not None:
            out[day] = {"rhr": value}
    return out


def body_battery_days(items: list[dict]) -> DayValues:
    out: DayValues = {}
    for item in items:
        day = _day(item.get("calendarDate"))
        value = _int(_get(item, "bodyBattery", "maxValue"), 0, 100)
        if day is not None and value is not None:
            out[day] = {"bb": value}
    return out


def movement_days(items: list[dict]) -> DayValues:
    """Steps, floors climbed and intensity minutes, from the daily summaries.

    A day with no steps means the watch wasn't worn, so it's left out.
    """
    out: DayValues = {}
    for item in items:
        day = _day(item.get("calendarDate"))
        steps = _int(_get(item, "movement", "steps", "value"), 1, 200_000)
        if day is None or steps is None:
            continue
        out[day] = {
            "steps": steps,
            "floors": _int(_get(item, "movement", "floorsAscended", "value"), 0, 2_000),
            "im_mod": _int(_get(item, "intensityMinutes", "moderate"), 0, 1_440),
            "im_vig": _int(_get(item, "intensityMinutes", "vigorous"), 0, 1_440),
            "im_goal": _int(_get(item, "intensityMinutes", "goal"), 1, 10_080),
        }
    return out


def activities(items: list[dict]) -> list[Activity]:
    out: list[Activity] = []
    for item in items:
        start = item.get("startTimeLocal")
        # The only timestamp read anywhere: keep the date, drop the time.
        day = _day(start[:10]) if isinstance(start, str) else None
        if day is None:
            continue
        seconds = _number(item.get("duration"), 0, MAX_ACTIVITY_SECONDS) or 0.0
        moving = _number(item.get("movingDuration"), 0, MAX_ACTIVITY_SECONDS) or seconds
        meters = _number(item.get("distance"), 0, MAX_ACTIVITY_METERS) or 0.0
        group = group_for(_get(item, "activityType", "typeKey"))
        zone_seconds = [_number(item.get(f"hrTimeInZone_{z}"), 0, MAX_ACTIVITY_SECONDS) for z in range(1, 6)]
        zones = tuple(float(s or 0.0) for s in zone_seconds) if any(s is not None for s in zone_seconds) else None
        bests: tuple[tuple[str, float], ...] = ()
        if group == "run":
            bests = tuple(
                (key, float(value))
                for key, field, fastest, slowest in BEST_SPLITS
                if (value := _number(item.get(field), fastest, slowest)) is not None
            )
        out.append(
            Activity(
                day=day,
                group=group,
                km=meters / 1000,
                seconds=float(seconds),
                moving_seconds=float(moving),
                load=_number(item.get("activityTrainingLoad"), 0, 10_000),
                zones=zones,
                bests=bests,
            )
        )
    return out


# -- helpers ------------------------------------------------------------------

def _get(item: Any, *path: str) -> Any:
    for key in path:
        if not isinstance(item, dict):
            return None
        item = item.get(key)
    return item


def _day(value: Any) -> date | None:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _number(value: Any, lo: float, hi: float) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value) or not lo <= value <= hi:
        return None
    return value


def _int(value: Any, lo: int, hi: int) -> int | None:
    number = _number(value, lo, hi)
    return None if number is None else round(number)


def _minutes(value: Any) -> int | None:
    seconds = _number(value, 0, 86400)
    return None if seconds is None else round(seconds / 60)
