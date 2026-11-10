"""Turn per-day numbers into the published payload (schema v1).

Pure functions, no I/O. An input of None means "unknown" (its fetch
failed): its fields come out as null rather than zeros, so the build can
carry previous values over instead of publishing a fake dip.

What gets published, and nothing finer:
- days:     the last 90 days of sleep, HRV, resting HR, Body Battery,
            steps and floors climbed
- calendar: 365 activity levels (0 = rest … 4 = hardest quartile)
- weeks:    the last 26 complete Monday–Sunday weeks of training and
            intensity minutes
- months:   every complete month: training, time in each heart-rate zone,
            and monthly averages
- summary:  30-day averages, the 30-day sleep-stage split, totals, running
            bests (time and date only) and the weekly intensity goal
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import date, timedelta

from .categories import GROUPS
from .normalise import BEST_KEYS, Activity, DayValues

SCHEMA_VERSION = 1
DAYS_SHOWN = 90
CALENDAR_DAYS = 365
WEEKS_SHOWN = 26
ROLLING_DAYS, ROLLING_MIN = 7, 4
WINDOW_DAYS, WINDOW_MIN = 30, 15
MONTH_MIN = 10
PACE_MIN_KM = 3.0
PACE_RANGE = (120, 1200)  # 2:00–20:00 per km; anything else is a recording glitch
STAGES = ("deep", "light", "rem", "awake")

# Day-level fields each health metric provides.
_DAY_FIELDS = {
    "sleep": ("sleep_min", "sleep_score"),
    "hrv": ("hrv", "hrv_lo", "hrv_hi"),
    "rhr": ("rhr",),
    "body_battery": ("bb",),
    "movement": ("steps", "floors"),
}

Series = dict[str, dict[date, int] | None]


@dataclass(frozen=True)
class Inputs:
    sleep: DayValues | None = None
    hrv: DayValues | None = None
    rhr: DayValues | None = None
    body_battery: DayValues | None = None
    movement: DayValues | None = None
    activities: list[Activity] | None = None


def build_payload(inputs: Inputs, through: date, sources: dict[str, str]) -> dict:
    inputs = _clip(inputs, through)
    series = _series(inputs)
    acts = inputs.activities
    return {
        "schema": SCHEMA_VERSION,
        "through": through.isoformat(),
        "sources": dict(sources),
        "summary": {
            "d30": _d30(series, acts, through),
            "stages30": _stages30(inputs.sleep, through),
            "totals": _totals(acts, through),
            "bests": _bests(acts, through),
            "im_goal": _im_goal(inputs.movement),
        },
        "days": _days(series, through),
        "calendar": _calendar(acts, through),
        "weeks": _weeks(acts, inputs.movement, through),
        "months": _months(series, acts, through, _first_day(inputs)),
    }


# -- sections -----------------------------------------------------------------

def _days(series: Series, through: date) -> list[dict]:
    rows = []
    for offset in range(DAYS_SHOWN - 1, -1, -1):
        day = through - timedelta(days=offset)
        rows.append({
            "d": day.isoformat(),
            "sleep_min": _on(series, "sleep_min", day),
            "sleep_score": _on(series, "sleep_score", day),
            "hrv": _on(series, "hrv", day),
            "hrv7": _rolling(series, "hrv", day),
            "hrv_lo": _on(series, "hrv_lo", day),
            "hrv_hi": _on(series, "hrv_hi", day),
            "rhr": _on(series, "rhr", day),
            "rhr7": _rolling(series, "rhr", day),
            "bb": _on(series, "bb", day),
            "bb7": _rolling(series, "bb", day),
            "steps": _on(series, "steps", day),
            "floors": _on(series, "floors", day),
        })
    return rows


def _d30(series: Series, acts: list[Activity] | None, through: date) -> dict:
    start = through - timedelta(days=WINDOW_DAYS - 1)
    sleep = _between(series, "sleep_min", start, through)
    in_window = None if acts is None else [a for a in acts if start <= a.day <= through]
    return {
        "nights": None if sleep is None else len(sleep),
        "sleep_min": _avg(sleep, WINDOW_MIN),
        "sleep_score": _avg(_between(series, "sleep_score", start, through), WINDOW_MIN),
        "hrv": _avg(_between(series, "hrv", start, through), WINDOW_MIN),
        "rhr": _avg(_between(series, "rhr", start, through), WINDOW_MIN),
        "bb": _avg(_between(series, "bb", start, through), WINDOW_MIN),
        "steps": _avg(_between(series, "steps", start, through), WINDOW_MIN),
        "floors": _avg(_between(series, "floors", start, through), WINDOW_MIN),
        "workouts": None if in_window is None else len(in_window),
        "hours": None if in_window is None else _hours(in_window),
    }


def _stages30(sleep: DayValues | None, through: date) -> dict | None:
    if sleep is None:
        return None
    start = through - timedelta(days=WINDOW_DAYS - 1)
    totals = dict.fromkeys(STAGES, 0)
    nights = 0
    for day, row in sleep.items():
        if start <= day <= through and all(row.get(f"{s}_min") is not None for s in STAGES):
            nights += 1
            for stage in STAGES:
                totals[stage] += row[f"{stage}_min"]
    total = sum(totals.values())
    if nights < WINDOW_MIN or total <= 0:
        return None
    return {stage: round(100 * totals[stage] / total) for stage in STAGES}


def _totals(acts: list[Activity] | None, through: date) -> dict | None:
    if acts is None:
        return None
    year_start = through - timedelta(days=CALENDAR_DAYS - 1)
    return {
        "y1": _activity_totals([a for a in acts if a.day >= year_start]),
        "all": _activity_totals(acts),
    }


def _calendar(acts: list[Activity] | None, through: date) -> dict | None:
    if acts is None:
        return None
    start = through - timedelta(days=CALENDAR_DAYS - 1)
    loads: dict[date, float] = {}
    for activity in acts:
        if start <= activity.day <= through:
            loads[activity.day] = loads.get(activity.day, 0.0) + (activity.load or 0.0)
    positive = sorted(v for v in loads.values() if v > 0)
    cuts = statistics.quantiles(positive, n=4) if len(positive) >= 4 else None

    levels = []
    for offset in range(CALENDAR_DAYS):
        day = start + timedelta(days=offset)
        if day not in loads:
            levels.append(0)
        elif loads[day] <= 0:
            levels.append(1)
        elif cuts is None:
            levels.append(2)
        else:
            levels.append(1 + sum(loads[day] > cut for cut in cuts))
    return {"start": start.isoformat(), "levels": levels}


def _bests(acts: list[Activity] | None, through: date) -> dict | None:
    """Fastest split per distance: last 12 months and all time, date only."""
    if acts is None:
        return None
    year_start = through - timedelta(days=CALENDAR_DAYS - 1)

    def fastest(pool: list[Activity]) -> dict:
        out: dict = {}
        for key in BEST_KEYS:
            times = [(seconds, a.day) for a in pool for k, seconds in a.bests if k == key]
            if times:
                seconds, day = min(times)
                out[key] = {"s": round(seconds), "d": day.isoformat()}
            else:
                out[key] = None
        return out

    return {"y1": fastest([a for a in acts if a.day >= year_start]), "all": fastest(acts)}


def _im_goal(movement: DayValues | None) -> int | None:
    """Garmin's weekly intensity-minutes goal, as of the latest day that has one."""
    if not movement:
        return None
    for day in sorted(movement, reverse=True):
        if movement[day].get("im_goal") is not None:
            return movement[day]["im_goal"]
    return None


def _intensity(movement: DayValues | None, start: date, end: date) -> int | None:
    """Garmin-style intensity minutes for a span: vigorous minutes count double."""
    if movement is None:
        return None
    rows = [row for day, row in movement.items() if start <= day <= end]
    if not rows:
        return None
    return sum((row.get("im_mod") or 0) + 2 * (row.get("im_vig") or 0) for row in rows)


def _weeks(acts: list[Activity] | None, movement: DayValues | None, through: date) -> list[dict]:
    last_sunday = through - timedelta(days=(through.weekday() + 1) % 7)
    last_monday = last_sunday - timedelta(days=6)
    rows = []
    for back in range(WEEKS_SHOWN - 1, -1, -1):
        monday = last_monday - timedelta(weeks=back)
        sunday = monday + timedelta(days=6)
        fields = _activity_fields(acts, monday, sunday)
        rows.append({
            "w": monday.isoformat(),
            "workouts": fields["workouts"],
            "hours": fields["hours"],
            "run_km": fields["run_km"],
            "pace_s": fields["pace_s"],
            "im": _intensity(movement, monday, sunday),
        })
    return rows


def _months(series: Series, acts: list[Activity] | None, through: date, first: date | None) -> list[dict]:
    if first is None:
        return []
    month_end = through + timedelta(days=1)
    last = (through.year, through.month) if month_end.day == 1 else _previous_month(through.year, through.month)
    rows = []
    year, month = first.year, first.month
    while (year, month) <= last:
        start = date(year, month, 1)
        end = date(*_next_month(year, month), 1) - timedelta(days=1)
        fields = _activity_fields(acts, start, end)
        rows.append({
            "m": f"{year:04d}-{month:02d}",
            "workouts": fields["workouts"],
            "hours": fields["hours"],
            "types": fields["types"],
            "run_km": fields["run_km"],
            "sleep_min": _avg(_between(series, "sleep_min", start, end), MONTH_MIN),
            "sleep_score": _avg(_between(series, "sleep_score", start, end), MONTH_MIN),
            "hrv": _avg(_between(series, "hrv", start, end), MONTH_MIN),
            "rhr": _avg(_between(series, "rhr", start, end), MONTH_MIN),
            "bb": _avg(_between(series, "bb", start, end), MONTH_MIN),
            "steps": _avg(_between(series, "steps", start, end), MONTH_MIN),
            "floors": _avg(_between(series, "floors", start, end), MONTH_MIN),
            **_zone_minutes(acts, start, end),
        })
        year, month = _next_month(year, month)
    return rows


# -- helpers ------------------------------------------------------------------

def _clip(inputs: Inputs, through: date) -> Inputs:
    def days(values: DayValues | None) -> DayValues | None:
        return None if values is None else {d: row for d, row in values.items() if d <= through}

    return Inputs(
        sleep=days(inputs.sleep),
        hrv=days(inputs.hrv),
        rhr=days(inputs.rhr),
        body_battery=days(inputs.body_battery),
        movement=days(inputs.movement),
        activities=None if inputs.activities is None else [a for a in inputs.activities if a.day <= through],
    )


def _series(inputs: Inputs) -> Series:
    out: Series = {}
    for metric, fields in _DAY_FIELDS.items():
        values: DayValues | None = getattr(inputs, metric)
        for field in fields:
            out[field] = None if values is None else {
                day: row[field] for day, row in values.items() if row.get(field) is not None
            }
    return out


def _first_day(inputs: Inputs) -> date | None:
    days: list[date] = []
    for metric in _DAY_FIELDS:
        values = getattr(inputs, metric)
        if values:
            days.append(min(values))
    if inputs.activities:
        days.append(min(a.day for a in inputs.activities))
    return min(days) if days else None


def _on(series: Series, field: str, day: date) -> int | None:
    values = series[field]
    return None if values is None else values.get(day)


def _between(series: Series, field: str, start: date, end: date) -> list[int] | None:
    values = series[field]
    return None if values is None else [v for d, v in values.items() if start <= d <= end]


def _rolling(series: Series, field: str, day: date) -> int | None:
    values = series[field]
    if values is None:
        return None
    window = [values[d] for d in (day - timedelta(days=i) for i in range(ROLLING_DAYS)) if d in values]
    return _avg(window, ROLLING_MIN)


def _avg(values: list[int] | None, minimum: int) -> int | None:
    if values is None or len(values) < minimum:
        return None
    return round(statistics.fmean(values))


def _activity_fields(acts: list[Activity] | None, start: date, end: date) -> dict:
    if acts is None:
        return dict.fromkeys(("workouts", "hours", "types", "run_km", "pace_s"))
    chosen = [a for a in acts if start <= a.day <= end]
    runs = [a for a in chosen if a.group == "run"]
    counts = {group: sum(1 for a in chosen if a.group == group) for group in GROUPS}
    return {
        "workouts": len(chosen),
        "hours": _hours(chosen),
        "types": {group: n for group, n in counts.items() if n},
        "run_km": _km(runs),
        "pace_s": _pace(runs),
    }


def _zone_minutes(acts: list[Activity] | None, start: date, end: date) -> dict:
    """Workout minutes spent in each heart-rate zone (hrz1 easy … hrz5 max)."""
    keys = [f"hrz{z}" for z in range(1, 6)]
    if acts is None:
        return dict.fromkeys(keys)
    totals = [0.0] * 5
    for activity in acts:
        if start <= activity.day <= end and activity.zones:
            for z, seconds in enumerate(activity.zones):
                totals[z] += seconds
    return {key: round(total / 60) for key, total in zip(keys, totals)}


def _activity_totals(acts: list[Activity]) -> dict:
    return {"workouts": len(acts), "hours": _hours(acts), "run_km": _km([a for a in acts if a.group == "run"])}


def _hours(acts: list[Activity]) -> float:
    return round(sum(a.seconds for a in acts) / 3600, 1)


def _km(runs: list[Activity]) -> float:
    return round(sum(a.km for a in runs), 1)


def _pace(runs: list[Activity]) -> int | None:
    km = sum(a.km for a in runs)
    if km < PACE_MIN_KM:
        return None
    pace = round(sum(a.moving_seconds for a in runs) / km)
    return pace if PACE_RANGE[0] <= pace <= PACE_RANGE[1] else None


def _next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def _previous_month(year: int, month: int) -> tuple[int, int]:
    return (year - 1, 12) if month == 1 else (year, month - 1)
