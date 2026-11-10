"""Turn raw Garmin responses into minimal per-day numbers.

Every value is read from an exact, allowlisted path (see the field map in
README.md). Nothing else in a response is looked at: no names, places,
coordinates, IDs, or the "minutes after midnight" bedtime fields. Timestamps
are read in exactly one place, `startTimeLocal`, and only its date is kept.

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
        out.append(
            Activity(
                day=day,
                group=group_for(_get(item, "activityType", "typeKey")),
                km=meters / 1000,
                seconds=float(seconds),
                moving_seconds=float(moving),
                load=_number(item.get("activityTrainingLoad"), 0, 10_000),
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
