"""One-off probe: what does the Garmin Personal API actually return for you?

Run it locally from the repo root (key in GARMIN_PERSONAL_API_KEY or in
~/.config/garmin/connect-personal-api-key):

    .venv/bin/python -m scripts.health.probe
    .venv/bin/python -m scripts.health.probe --out .garmin-probe/report.txt

It prints a REDACTED report: field paths, types, how often each is present,
and pattern classes (date, datetime, epoch, number, word, text). Values are
never printed, except a few harmless enums (activity type keys, HRV status,
token scopes) and counts. Fields that look like GPS, times or free text are
flagged so the real job knows never to read them.

Nothing raw is saved unless you pass --save-raw DIR with a folder OUTSIDE
this repo (your Documents folder may sync to iCloud, so prefer /tmp or an
encrypted disk, and delete it afterwards).

    --smoke   token exchange + one call, status only (used by CI)
"""
from __future__ import annotations

import argparse
import base64
import json
import logging
import math
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from . import garmin
from .dates import publish_cutoff

REPO_ROOT = Path(__file__).resolve().parents[2]
DAILY_RUN_WINDOW_DAYS = 396  # ~13 months, what the daily build will recompute

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
TIME_RE = re.compile(r"^\d{1,2}:\d{2}")
WORD_RE = re.compile(r"^[A-Za-z0-9_\-]{1,40}$")
ENUM_VALUE_RE = re.compile(r"^[A-Za-z0-9_\-]{1,40}$")
GEO_KEY_RE = re.compile(r"lat|lon|lng|gps|polyline|geo|location|coord|route|course|altitude|elevation", re.I)
TIME_KEY_RE = re.compile(r"time|timestamp|gmt|local|start|end|offset", re.I)
# Times of day that Garmin stores as plain numbers, e.g. minutes after
# midnight. Their values look harmless, so they are flagged by name.
TIME_NAME_RE = re.compile(r"Mins$|Bedtime|Midpoint|Window(Start|End)|Timestamp|Time(GMT|Gmt|Local)$")
TEXT_KEY_RE = re.compile(r"name|description|title|note|comment|owner|user|email|device|serial|uuid", re.I)
ID_KEY_RE = re.compile(r"(Id|ID|Pk|_id|Uuid|UUID)$")
TIME_CLASSES = {"datetime", "time", "epoch-ms?", "epoch-s?"}

# Only these paths may have their actual values printed: they are fixed
# vocabularies, not personal data.
ENUM_PATHS = {
    "activities": re.compile(r"(^|\.)activityType\.typeKey$"),
    "hrv-range": re.compile(r"(^|\.)status$"),
    "hrv-day": re.compile(r"(^|\.)status$"),
}


# -- shape collection ---------------------------------------------------------

@dataclass
class PathStats:
    seen: int = 0
    non_null: int = 0
    classes: Counter = field(default_factory=Counter)


def classify(key: str, value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        if ID_KEY_RE.search(key):
            return "id"
        magnitude = abs(value)
        if isinstance(value, int) and 1e11 <= magnitude < 1e14:
            return "epoch-ms?"
        if isinstance(value, int) and 1e9 <= magnitude < 1e10 and TIME_KEY_RE.search(key):
            return "epoch-s?"
        kind = "int" if isinstance(value, int) else "float"
        if magnitude == 0:
            return f"{kind} 0"
        return f"{kind} ~1e{int(math.floor(math.log10(magnitude)))}"
    if isinstance(value, str):
        if DATE_RE.match(value):
            return "date"
        if DATETIME_RE.match(value):
            return "datetime"
        if TIME_RE.match(value):
            return "time"
        if WORD_RE.match(value):
            return "word"
        return "text"
    return type(value).__name__


def _list_class(items: list) -> str:
    n = len(items)
    if n == 0:
        return "list(0)"
    if n <= 10:
        return "list(1-10)"
    if n <= 100:
        return "list(11-100)"
    return "list(>100)"


def _normalise_key(key: Any) -> str:
    key = str(key)
    if DATE_RE.match(key):
        return "<date>"
    if key.isdigit():
        return "<n>"
    return key


def collect(obj: Any, stats: dict[str, PathStats], path: str = "", key: str = "") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            name = _normalise_key(k)
            collect(v, stats, f"{path}.{name}" if path else name, name)
    elif isinstance(obj, list):
        entry = stats[f"{path}[]" if path else "[]"]
        entry.seen += 1
        entry.non_null += 1
        entry.classes[_list_class(obj)] += 1
        for item in obj:
            collect(item, stats, f"{path}[]" if path else "[]", key)
    else:
        entry = stats[path or "(root)"]
        entry.seen += 1
        if obj is not None:
            entry.non_null += 1
        entry.classes[classify(key, obj)] += 1


def flags_for(path: str, classes: set[str]) -> str:
    leaf = re.sub(r"\[\]$", "", path.rsplit(".", 1)[-1])
    out = []
    if GEO_KEY_RE.search(leaf):
        out.append("GEO")
    if classes & TIME_CLASSES or TIME_NAME_RE.search(leaf):
        out.append("TIME")
    if "text" in classes or (TEXT_KEY_RE.search(leaf) and classes & {"word", "text"}):
        out.append("TEXT")
    if "id" in classes or ID_KEY_RE.search(leaf):
        out.append("ID")
    return " ".join(out)


def find_records(obj: Any) -> tuple[list[dict], str]:
    """Locate the per-day / per-activity records inside a response."""
    if isinstance(obj, list):
        return [r for r in obj if isinstance(r, dict)], "top-level list"
    if isinstance(obj, dict):
        lists = [(k, v) for k, v in obj.items() if isinstance(v, list) and v and all(isinstance(i, dict) for i in v)]
        if len(lists) == 1:
            return lists[0][1], f"list under '{lists[0][0]}'"
        return [obj], "single object"
    return [], "no records"


def flatten(record: Any, path: str = "") -> dict[str, Any]:
    """Leaf path -> value for one record (lists of dicts are skipped)."""
    out: dict[str, Any] = {}
    if isinstance(record, dict):
        for k, v in record.items():
            name = _normalise_key(k)
            child = f"{path}.{name}" if path else name
            if isinstance(v, dict):
                out.update(flatten(v, child))
            elif not isinstance(v, list):
                out[child] = v
    return out


def count_non_null(records: list[dict], pattern: re.Pattern[str]) -> int:
    count = 0
    for record in records:
        flat = flatten(record)
        if any(pattern.search(p) and v not in (None, 0, "") for p, v in flat.items()):
            count += 1
    return count


def to_date(value: Any) -> date | None:
    """Date part of a Garmin timestamp (epoch ms or ISO string), in memory only."""
    if isinstance(value, (int, float)) and value > 1e11:
        # Garmin "...Local" epochs are wall-clock times encoded as if UTC.
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date()
    if isinstance(value, str) and DATE_RE.match(value[:10]):
        return date.fromisoformat(value[:10])
    return None


# -- report -------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def __call__(self, line: str = "") -> None:
        self.lines.append(line)
        print(line, flush=True)

    def text(self) -> str:
        return "\n".join(self.lines) + "\n"


def describe_token(token: str) -> str:
    parts = token.split(".")
    if len(parts) != 3:
        return "opaque token (not a JWT)"
    try:
        padded = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
    except (ValueError, TypeError):
        return "JWT (payload not readable)"
    if not isinstance(payload, dict):
        return "JWT (payload not an object)"
    bits = ["JWT"]
    exp, iat = payload.get("exp"), payload.get("iat")
    if isinstance(exp, (int, float)) and isinstance(iat, (int, float)):
        bits.append(f"lifetime ~{(exp - iat) / 3600:.1f}h")
    raw_scopes = payload.get("scope") or payload.get("scopes") or payload.get("scp")
    if isinstance(raw_scopes, str):
        raw_scopes = raw_scopes.split()
    if isinstance(raw_scopes, list):
        scopes = sorted(s for s in raw_scopes if isinstance(s, str) and ENUM_VALUE_RE.match(s))
        bits.append("scopes: " + (", ".join(scopes) or "none"))
    bits.append("claim names: " + ", ".join(sorted(map(str, payload))))
    return " · ".join(bits)


def print_shape(report: Report, label: str, data: Any) -> list[dict]:
    records, where = find_records(data)
    report(f"   shape: {where}, {len(records)} record(s)")
    stats: dict[str, PathStats] = defaultdict(PathStats)
    collect(data, stats)
    if not stats:
        report("   (empty)")
        return records
    width = min(64, max(len(p) for p in stats))
    report(f"   {'path'.ljust(width)}  {'types'.ljust(28)} {'seen':>5} {'non-null':>8}  flags")
    for path in sorted(stats):
        entry = stats[path]
        classes = ", ".join(c for c, _ in entry.classes.most_common(3))
        flag = flags_for(path, set(entry.classes))
        report(f"   {path.ljust(width)}  {classes.ljust(28)} {entry.seen:>5} {entry.non_null:>8}  {flag}")

    enum_pattern = ENUM_PATHS.get(label)
    if enum_pattern:
        values: Counter = Counter()
        for record in records:
            for path, value in flatten(record).items():
                if enum_pattern.search(path) and isinstance(value, str) and ENUM_VALUE_RE.match(value):
                    values[value] += 1
        if values:
            report("   values (enum, safe to show): " + ", ".join(f"{v}×{n}" for v, n in values.most_common()))
    return records


# -- probe steps --------------------------------------------------------------

def fetch_range(client: garmin.GarminClient, label: str, start: date, end: date) -> Any:
    params = {"startDate": start.isoformat(), "endDate": end.isoformat()}
    if label == "sleep-summaries":
        return client.get(garmin.SLEEP_SUMMARIES_PATH, params)
    if label == "hrv-range":
        return client.get(garmin.hrv_range_path(start, end))
    if label == "daily-summaries":
        return client.get(garmin.DAILY_SUMMARIES_PATH, params)
    if label == "body-battery":
        return client.get(garmin.BODY_BATTERY_PATH, params)
    raise ValueError(label)


def attempt(fn, *args) -> tuple[Any, str]:
    """Run a request, returning (data, status text) instead of raising."""
    try:
        data = fn(*args)
    except garmin.GarminAuthError:
        raise
    except garmin.GarminHTTPError as exc:
        return None, f"failed ({exc})"
    return data, "ok" if data is not None else "ok, no data"


def check_sleep_dates(report: Report, records: list[dict]) -> None:
    wake = bed = total = 0
    for record in records:
        flat = flatten(record)
        cal = next((to_date(v) for p, v in flat.items() if p.endswith("calendarDate")), None)
        end = next((to_date(v) for p, v in flat.items() if re.search(r"sleepEnd\w*Local|EndTimestampLocal", p)), None)
        start = next((to_date(v) for p, v in flat.items() if re.search(r"sleepStart\w*Local|StartTimestampLocal", p)), None)
        if cal and end:
            total += 1
            wake += cal == end
            bed += bool(start and cal == start)
    if total:
        report(f"   check: calendarDate = wake date for {wake}/{total} nights; = bedtime date for {bed}/{total}")
    else:
        report("   check: could not find calendarDate + local end timestamp to compare")


def summarise_fields(report: Report, label: str, records: list[dict], pattern: str) -> None:
    rx = re.compile(pattern, re.I)
    paths: Counter = Counter()
    for record in records:
        for path, value in flatten(record).items():
            if rx.search(path) and value is not None:
                paths[path] += 1
    if paths:
        listed = ", ".join(f"{p} ({n}/{len(records)})" for p, n in sorted(paths.items()))
        report(f"   {label}: {listed}")
    else:
        report(f"   {label}: none found")


def run_probe(
    client: garmin.GarminClient, cutoff: date, days: int, history: bool, raw_dir: Path | None, report: Report
) -> int:
    report("Garmin Personal API probe — redacted report")
    report(f"window: {days} days ending {cutoff.isoformat()} (the publish cutoff; nothing newer is requested)")
    report()

    try:
        client.authenticate()
    except garmin.GarminError as exc:
        report(f"token exchange FAILED: {exc}")
        return 1
    report(f"1. token exchange ok · {describe_token(client.token or '')}")
    report()

    start = cutoff - timedelta(days=days - 1)
    samples: dict[str, Any] = {}

    def sample(number: str, label: str, fn, *args):
        data, status = attempt(fn, *args)
        report(f"{number} {label}: {status}")
        samples[label] = data
        records = print_shape(report, label, data) if data is not None else []
        report()
        return records

    sleep = sample("2.", "sleep-summaries", fetch_range, client, "sleep-summaries", start, cutoff)
    if sleep:
        check_sleep_dates(report, sleep)
        summarise_fields(report, "score-like fields", sleep, r"score")
        summarise_fields(report, "stage fields", sleep, r"deep|light|rem|awake")
        report()
    sleep_day = sample("3.", "sleep-day", client.get, garmin.SLEEP_DAY_PATH, {"date": cutoff.isoformat()})
    if sleep_day:
        summarise_fields(report, "score-like fields", sleep_day, r"score")
        report()
    hrv = sample("4.", "hrv-range", fetch_range, client, "hrv-range", start, cutoff)
    if hrv:
        summarise_fields(report, "HRV value fields", hrv, r"lastNight|weekly|baseline|hrv")
        report()
    sample("5.", "hrv-day", client.get, garmin.hrv_day_path(cutoff))
    dailies = sample("6.", "daily-summaries", fetch_range, client, "daily-summaries", start, cutoff)
    if dailies:
        summarise_fields(report, "resting HR fields", dailies, r"resting")
        summarise_fields(report, "Body Battery fields", dailies, r"bodyBattery")
        report()
    sample("7.", "body-battery", fetch_range, client, "body-battery", start, cutoff)

    # Activities: a full daily-run window, so the sport-type list is complete.
    act_start = cutoff - timedelta(days=DAILY_RUN_WINDOW_DAYS - 1)
    data, status = attempt(lambda: list(client.iter_activities(act_start, cutoff)))
    report(f"8. activities ({DAILY_RUN_WINDOW_DAYS} days): {status}")
    activities = data or []
    samples["activities"] = activities
    if activities:
        print_shape(report, "activities", activities)
        summarise_fields(report, "fields the build would use", activities,
                         r"(^|\.)(activityType\.typeKey|distance|duration|movingDuration|elapsedDuration|startTimeLocal)$")
    report()

    report("9. range caps (status · records)")
    caps: dict[str, int] = {}
    for label, sizes in (
        ("sleep-summaries", (31, 32)),
        ("hrv-range", (31, 32, 90)),
        ("daily-summaries", (31, 90, 91, 366)),
        ("body-battery", (31, 32)),
    ):
        results = []
        for size in sizes:
            data, status = attempt(fetch_range, client, label, cutoff - timedelta(days=size - 1), cutoff)
            n = len(find_records(data)[0]) if data is not None else 0
            results.append(f"{size}d → {status} · {n}")
            if status.startswith("ok"):
                caps[label] = max(caps.get(label, 0), size)
        report(f"   {label}: " + " | ".join(results))
    for limit in (45, 100):
        data, status = attempt(client.get, garmin.ACTIVITIES_PATH, {
            "start": 0, "limit": limit, "startDate": act_start.isoformat(), "endDate": cutoff.isoformat()})
        n = len(data) if isinstance(data, list) else 0
        report(f"   activities page limit {limit}: {status} · {n} returned")
    report()

    if history:
        report("10. history (per year: activities · sleep nights in a 31-day window · HRV nights in it)")
        empty_streak = 0
        for year in range(cutoff.year, cutoff.year - 25, -1):
            year_end = min(date(year, 12, 31), cutoff)
            window_end = min(date(year, 7, 31), cutoff)
            window_start = window_end - timedelta(days=30)
            acts, _ = attempt(client.get, garmin.ACTIVITIES_PATH, {
                "start": 0, "limit": 45, "startDate": date(year, 1, 1).isoformat(), "endDate": year_end.isoformat()})
            n_acts = len(acts) if isinstance(acts, list) else 0
            sleep_data, _ = attempt(fetch_range, client, "sleep-summaries", window_start, window_end)
            hrv_data, _ = attempt(fetch_range, client, "hrv-range", window_start, window_end)
            n_sleep = count_non_null(find_records(sleep_data)[0], re.compile(r"sleepTime|sleepSeconds|duration", re.I)) if sleep_data else 0
            n_hrv = count_non_null(find_records(hrv_data)[0], re.compile(r"lastNight", re.I)) if hrv_data else 0
            report(f"   {year}: activities {'45+' if n_acts >= 45 else n_acts} · sleep {n_sleep}/31 · HRV {n_hrv}/31")
            empty_streak = empty_streak + 1 if (n_acts == 0 and n_sleep == 0) else 0
            if empty_streak >= 2:
                break
        report()

    report("11. estimated calls for one daily run (~13 months)")
    estimate = 1  # token
    for label in ("sleep-summaries", "hrv-range", "daily-summaries", "body-battery"):
        cap = caps.get(label)
        if cap:
            calls = math.ceil(DAILY_RUN_WINDOW_DAYS / cap)
            estimate += calls
            report(f"   {label}: {calls} (cap {cap}d)")
        else:
            report(f"   {label}: no working range found")
    act_calls = max(1, math.ceil(len(activities) / 45))
    estimate += act_calls
    report(f"   activities: {act_calls} ({len(activities)} activities)")
    report(f"   total ≈ {estimate} calls; this probe made {client.request_count}")

    if raw_dir:
        save_raw(raw_dir, samples)
        report()
        report(f"raw responses saved to {raw_dir} — delete them when you're done")
    return 0


def run_smoke(client: garmin.GarminClient, cutoff: date) -> int:
    """Token exchange plus one tiny call. Prints status only (safe for public CI logs)."""
    try:
        client.authenticate()
    except garmin.GarminError as exc:
        print(f"token exchange: failed ({exc})")
        return 1
    print("token exchange: ok")
    try:
        client.get(garmin.DAILY_SUMMARIES_PATH, {"startDate": cutoff.isoformat(), "endDate": cutoff.isoformat()})
    except garmin.GarminError as exc:
        print(f"daily-summaries: failed ({exc})")
        return 1
    print(f"daily-summaries: ok · {client.request_count} requests")
    return 0


# -- raw output (opt-in, outside the repo only) -------------------------------

def check_raw_dir(raw_dir: Path) -> Path:
    resolved = raw_dir.expanduser().resolve()
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        raise SystemExit("--save-raw must point outside this repository")
    return resolved


def save_raw(raw_dir: Path, samples: dict[str, Any]) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    for label, data in samples.items():
        path = raw_dir / f"{label}.json"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)


# -- entry point --------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--smoke", action="store_true", help="token exchange + one call, status only")
    parser.add_argument("--days", type=int, default=14, help="sample window for health endpoints (default 14)")
    parser.add_argument("--no-history", action="store_true", help="skip the year-by-year history scan")
    parser.add_argument("--out", type=Path, help="also write the redacted report to this file")
    parser.add_argument("--save-raw", type=Path, help="opt-in: save raw responses to a folder OUTSIDE the repo")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    raw_dir = check_raw_dir(args.save_raw) if args.save_raw else None
    if not 1 <= args.days <= 31:
        parser.error("--days must be between 1 and 31")

    try:
        client = garmin.GarminClient(garmin.load_api_key())
    except garmin.GarminConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    cutoff = publish_cutoff(datetime.now(timezone.utc))

    if args.smoke:
        return run_smoke(client, cutoff)

    report = Report()
    try:
        code = run_probe(client, cutoff, args.days, not args.no_history, raw_dir, report)
    except garmin.GarminAuthError as exc:
        report(f"\nstopped: {exc}")
        code = 1

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report.text(), encoding="utf-8")
        print(f"\nreport written to {args.out}")
    return code


if __name__ == "__main__":
    sys.exit(main())
