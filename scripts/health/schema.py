"""Strict check of the payload before anything is written.

The payload may contain only known keys, numbers inside plausible ranges,
ISO dates and months (never after `through`), and sport-group names. There
is no free text anywhere, so names, places and timestamps can't slip in.
The range limits also reject epoch numbers and coordinates, even under a
valid key.

Error messages give the location and the problem, never the value: they end
up in public CI logs.
"""
from __future__ import annotations

import json
import math
import re
from datetime import date, timedelta
from typing import Any

from .categories import GROUPS
from .config import METRICS

SCHEMA_VERSION = 1
MAX_BYTES = 100_000
MAX_DAYS, MAX_CALENDAR, MAX_WEEKS, MAX_MONTHS = 90, 366, 26, 1200

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

# field -> (min, max, decimal places)
Spec = tuple[float, float, int]
_SLEEP_MIN: Spec = (0, 1440, 0)
_SCORE: Spec = (0, 100, 0)
_HRV: Spec = (1, 300, 0)
_RHR: Spec = (20, 150, 0)
_BB: Spec = (0, 100, 0)

DAY: dict[str, Spec] = {
    "sleep_min": _SLEEP_MIN, "sleep_score": _SCORE,
    "hrv": _HRV, "hrv7": _HRV, "hrv_lo": _HRV, "hrv_hi": _HRV,
    "rhr": _RHR, "rhr7": _RHR, "bb": _BB, "bb7": _BB,
}
WEEK: dict[str, Spec] = {"workouts": (0, 100, 0), "hours": (0, 168, 1), "run_km": (0, 2000, 1), "pace_s": (120, 1200, 0)}
MONTH: dict[str, Spec] = {
    "workouts": (0, 500, 0), "hours": (0, 744, 1), "run_km": (0, 10_000, 1),
    "sleep_min": _SLEEP_MIN, "sleep_score": _SCORE, "hrv": _HRV, "rhr": _RHR, "bb": _BB,
}
D30: dict[str, Spec] = {
    "nights": (0, 30, 0), "sleep_min": _SLEEP_MIN, "sleep_score": _SCORE, "hrv": _HRV, "rhr": _RHR, "bb": _BB,
    "workouts": (0, 500, 0), "hours": (0, 720, 1),
}
TOTAL: dict[str, Spec] = {"workouts": (0, 100_000, 0), "hours": (0, 100_000, 1), "run_km": (0, 1_000_000, 1)}
STAGE: Spec = (0, 100, 0)
TYPE_COUNT: Spec = (1, 500, 0)
LEVEL: Spec = (0, 4, 0)


class SchemaError(ValueError):
    def __init__(self, path: str, problem: str):
        self.path = path
        super().__init__(f"{path}: {problem}")


def canonical(payload: Any) -> str:
    """The exact text that gets written (before any encryption)."""
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def validate(payload: Any, *, max_through: date) -> None:
    """Raise SchemaError unless `payload` is exactly what the page may receive."""
    _keys(payload, "payload", {"schema", "through", "sources", "summary", "days", "calendar", "weeks", "months"})
    if type(payload["schema"]) is not int or payload["schema"] != SCHEMA_VERSION:
        raise SchemaError("schema", "unsupported version")
    through = _date(payload["through"], "through", latest=max_through)

    sources = payload["sources"]
    if not isinstance(sources, dict):
        raise SchemaError("sources", "expected an object")
    if set(sources) - set(METRICS):
        raise SchemaError("sources", f"{len(set(sources) - set(METRICS))} unexpected key(s)")
    for metric, value in sources.items():
        _date(value, f"sources.{metric}", latest=through)

    summary = payload["summary"]
    _keys(summary, "summary", {"d30", "stages30", "totals"})
    _fields(summary["d30"], "summary.d30", D30)
    if summary["stages30"] is not None:
        _fields(summary["stages30"], "summary.stages30", dict.fromkeys(("deep", "light", "rem", "awake"), STAGE), nullable=False)
    if summary["totals"] is not None:
        _keys(summary["totals"], "summary.totals", {"y1", "all"})
        for period in ("y1", "all"):
            _fields(summary["totals"][period], f"summary.totals.{period}", TOTAL, nullable=False)

    _days(payload["days"], through)
    _calendar(payload["calendar"], through)
    _weeks(payload["weeks"], through)
    _months(payload["months"], through)

    if len(canonical(payload)) > MAX_BYTES:
        raise SchemaError("payload", f"larger than {MAX_BYTES} bytes")


# -- sections -----------------------------------------------------------------

def _days(rows: Any, through: date) -> None:
    _list(rows, "days", 1, MAX_DAYS)
    for i, row in enumerate(rows):
        path = f"days[{i}]"
        _keys(row, path, {"d", *DAY})
        day = _date(row["d"], f"{path}.d", latest=through)
        expected = through - timedelta(days=len(rows) - 1 - i)
        if day != expected:
            raise SchemaError(f"{path}.d", "days must be consecutive and end at `through`")
        for field, spec in DAY.items():
            _number(row[field], f"{path}.{field}", spec)


def _calendar(calendar: Any, through: date) -> None:
    if calendar is None:
        return
    _keys(calendar, "calendar", {"start", "levels"})
    start = _date(calendar["start"], "calendar.start", latest=through)
    levels = calendar["levels"]
    _list(levels, "calendar.levels", 1, MAX_CALENDAR)
    if start + timedelta(days=len(levels) - 1) > through:
        raise SchemaError("calendar.levels", "runs past `through`")
    for i, level in enumerate(levels):
        _number(level, f"calendar.levels[{i}]", LEVEL, nullable=False)


def _weeks(rows: Any, through: date) -> None:
    _list(rows, "weeks", 0, MAX_WEEKS)
    previous: date | None = None
    for i, row in enumerate(rows):
        path = f"weeks[{i}]"
        _keys(row, path, {"w", *WEEK})
        monday = _date(row["w"], f"{path}.w", latest=through)
        if monday.weekday() != 0:
            raise SchemaError(f"{path}.w", "weeks must start on a Monday")
        if monday + timedelta(days=6) > through:
            raise SchemaError(f"{path}.w", "only complete weeks may be published")
        if previous is not None and monday != previous + timedelta(weeks=1):
            raise SchemaError(f"{path}.w", "weeks must be consecutive")
        previous = monday
        for field, spec in WEEK.items():
            _number(row[field], f"{path}.{field}", spec)


def _months(rows: Any, through: date) -> None:
    _list(rows, "months", 0, MAX_MONTHS)
    previous: tuple[int, int] | None = None
    for i, row in enumerate(rows):
        path = f"months[{i}]"
        _keys(row, path, {"m", "types", *MONTH})
        value = row["m"]
        if not isinstance(value, str) or not _MONTH_RE.match(value):
            raise SchemaError(f"{path}.m", "expected YYYY-MM")
        year, month = int(value[:4]), int(value[5:])
        following = (year + 1, 1) if month == 12 else (year, month + 1)
        if date(*following, 1) - timedelta(days=1) > through:
            raise SchemaError(f"{path}.m", "only complete months may be published")
        if previous is not None and (year, month) != ((previous[0] + 1, 1) if previous[1] == 12 else (previous[0], previous[1] + 1)):
            raise SchemaError(f"{path}.m", "months must be consecutive")
        previous = (year, month)
        for field, spec in MONTH.items():
            _number(row[field], f"{path}.{field}", spec)
        types = row["types"]
        if types is not None:
            if not isinstance(types, dict):
                raise SchemaError(f"{path}.types", "expected an object")
            unknown = [k for k in types if k not in GROUPS]
            if unknown:
                raise SchemaError(f"{path}.types", f"{len(unknown)} unknown sport group(s)")
            for group, count in types.items():
                _number(count, f"{path}.types.{group}", TYPE_COUNT, nullable=False)


# -- primitives ---------------------------------------------------------------

def _keys(obj: Any, path: str, expected: set[str]) -> None:
    if not isinstance(obj, dict):
        raise SchemaError(path, "expected an object")
    extra = set(obj) - expected
    if extra:
        # Key names could themselves carry data, so only count them.
        raise SchemaError(path, f"{len(extra)} unexpected key(s)")
    missing = expected - set(obj)
    if missing:
        raise SchemaError(path, f"missing key(s): {', '.join(sorted(missing))}")


def _fields(obj: Any, path: str, specs: dict[str, Spec], *, nullable: bool = True) -> None:
    _keys(obj, path, set(specs))
    for field, spec in specs.items():
        _number(obj[field], f"{path}.{field}", spec, nullable=nullable)


def _list(value: Any, path: str, shortest: int, longest: int) -> None:
    if not isinstance(value, list):
        raise SchemaError(path, "expected a list")
    if not shortest <= len(value) <= longest:
        raise SchemaError(path, f"expected {shortest}–{longest} entries")


def _number(value: Any, path: str, spec: Spec, *, nullable: bool = True) -> None:
    if value is None:
        if nullable:
            return
        raise SchemaError(path, "must not be null")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SchemaError(path, "must be a number")
    low, high, decimals = spec
    if decimals == 0 and not isinstance(value, int):
        raise SchemaError(path, "must be a whole number")
    if isinstance(value, float) and not math.isfinite(value):
        raise SchemaError(path, "must be finite")
    if not low <= value <= high:
        raise SchemaError(path, "out of range")
    if decimals and round(value, decimals) != value:
        raise SchemaError(path, f"more than {decimals} decimal place(s)")


def _date(value: Any, path: str, *, latest: date) -> date:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        raise SchemaError(path, "expected YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise SchemaError(path, "not a real date") from None
    if parsed > latest:
        raise SchemaError(path, "after the publish cutoff")
    return parsed
