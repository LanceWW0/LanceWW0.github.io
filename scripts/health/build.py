"""Daily build: Garmin → privacy-safe aggregates → _data/health.json.

    .venv/bin/python -m scripts.health.build --dry-run        # fetch and check, write nothing
    .venv/bin/python -m scripts.health.build --out .garmin-probe/health.json

Every run rebuilds all history from Garmin (about 75 calls), so late watch
syncs, edits and deletions fix themselves. The previous file is used only
as a fallback. If a metric fails, or suddenly returns far less data than
last time, its previous values are kept and the run exits with code 2, so
GitHub emails you.

Exit codes: 0 ok · 1 nothing written · 2 written, but needs attention.
Logs show counts and status codes only, never values: CI logs are public.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from . import crypto, garmin, normalise
from .aggregate import Inputs, build_payload
from .config import METRICS, REPO_ROOT, ConfigError, HealthConfig, load_config
from .dates import chunk_range, publish_cutoff
from .schema import SchemaError, canonical, validate

DEFAULT_OUT = REPO_ROOT / "_data" / "health.json"
PASSPHRASE_ENV = "HEALTH_PAGE_PASSPHRASE"
KEY_EXPIRES_ENV = "GARMIN_KEY_EXPIRES"
KEY_WARNING_DAYS = 7

# The only endpoints the build may call (the probe needed a few more).
BUILD_ENDPOINTS = frozenset({"sleep-summaries", "hrv-range", "daily-summaries", "activities"})
CHUNK_DAYS = {"sleep-summaries": 31, "hrv-range": 90, "daily-summaries": 366}
ACTIVITY_PAGE_SIZE = 100

DROP_RATIO, DROP_MIN = 0.7, 10
EXIT_OK, EXIT_FATAL, EXIT_ATTENTION = 0, 1, 2

# Which payload fields each metric owns, for carrying previous values over.
OWNED: dict[str, dict[str, tuple[str, ...]]] = {
    "sleep": {"days": ("sleep_min", "sleep_score"), "months": ("sleep_min", "sleep_score"),
              "d30": ("nights", "sleep_min", "sleep_score"), "summary": ("stages30",)},
    "hrv": {"days": ("hrv", "hrv7", "hrv_lo", "hrv_hi"), "months": ("hrv",), "d30": ("hrv",)},
    "rhr": {"days": ("rhr", "rhr7"), "months": ("rhr",), "d30": ("rhr",)},
    "body_battery": {"days": ("bb", "bb7"), "months": ("bb",), "d30": ("bb",)},
    "activities": {"weeks": ("workouts", "hours", "run_km", "pace_s"),
                   "months": ("workouts", "hours", "types", "run_km"),
                   "d30": ("workouts", "hours"), "summary": ("totals",), "top": ("calendar",)},
}
ROW_KEYS = {"days": "d", "weeks": "w", "months": "m"}
DROP_FIELD = {"sleep": "sleep_min", "hrv": "hrv", "rhr": "rhr", "body_battery": "bb", "activities": "workouts"}

Log = Callable[[str], None]


@dataclass(frozen=True)
class Previous:
    payload: dict
    body: str
    encrypted: bool
    salt: bytes | None


# -- fetching -----------------------------------------------------------------

def _ranged(client, label: str, key: str | None, start: date, end: date, request) -> list[dict]:
    items: list[dict] = []
    for chunk_start, chunk_end in chunk_range(start, end, CHUNK_DAYS[label]):
        path, params = request(chunk_start, chunk_end)
        items += normalise.records(client.get(path, params), key, label)
    return items


def _span(start: date, end: date) -> dict[str, str]:
    return {"startDate": start.isoformat(), "endDate": end.isoformat()}


def fetch_sleep(client, start: date, end: date) -> list[dict]:
    return _ranged(client, "sleep-summaries", None, start, end,
                   lambda a, b: (garmin.SLEEP_SUMMARIES_PATH, _span(a, b)))


def fetch_hrv(client, start: date, end: date) -> list[dict]:
    return _ranged(client, "hrv-range", "hrvSummaries", start, end,
                   lambda a, b: (garmin.hrv_range_path(a, b), None))


def fetch_dailies(client, start: date, end: date) -> list[dict]:
    return _ranged(client, "daily-summaries", "data", start, end,
                   lambda a, b: (garmin.DAILY_SUMMARIES_PATH, _span(a, b)))


def fetch_activities(client, start: date, end: date) -> list[dict]:
    return list(client.iter_activities(start, end, page_size=ACTIVITY_PAGE_SIZE))


def collect(client, config: HealthConfig, through: date, log: Log) -> tuple[dict[str, Any], dict[str, str]]:
    """Fetch and normalise every enabled metric. Returns (values, failures).

    An auth error stops everything (the key is the problem); any other error
    only fails that metric.
    """
    start = config.since
    cache: dict[str, Any] = {}

    def dailies() -> list[dict]:
        if "dailies" not in cache:
            try:
                cache["dailies"] = fetch_dailies(client, start, through)
            except (garmin.GarminError, normalise.NormaliseError) as exc:
                cache["dailies"] = exc
        if isinstance(cache["dailies"], Exception):
            raise cache["dailies"]
        return cache["dailies"]

    steps: dict[str, Callable[[], Any]] = {
        "sleep": lambda: normalise.sleep_days(fetch_sleep(client, start, through)),
        "hrv": lambda: normalise.hrv_days(fetch_hrv(client, start, through)),
        "rhr": lambda: normalise.rhr_days(dailies()),
        "body_battery": lambda: normalise.body_battery_days(dailies()),
        "activities": lambda: normalise.activities(fetch_activities(client, start, through)),
    }
    values: dict[str, Any] = {}
    failures: dict[str, str] = {}
    for metric in config.metrics:
        try:
            values[metric] = steps[metric]()
        except garmin.GarminAuthError:
            raise
        except (garmin.GarminError, normalise.NormaliseError) as exc:
            failures[metric] = str(exc)
            log(f"{metric}: failed ({exc})")
            continue
        unit = "workouts" if metric == "activities" else "days"
        log(f"{metric}: ok ({len(values[metric])} {unit})")
    return values, failures


# -- previous file, fallback and checks ---------------------------------------

def read_previous(path: Path, passphrase: str | None, log: Log) -> Previous | None:
    if not path.exists():
        return None
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        log("previous file unreadable; building without a fallback")
        return None
    encrypted = crypto.is_envelope(stored)
    salt = None
    if encrypted:
        if not passphrase:
            log("previous file is encrypted and no passphrase is set; building without a fallback")
            return None
        try:
            payload = json.loads(crypto.decrypt(stored, passphrase))
            salt = crypto.salt_of(stored)
        except crypto.CryptoError:
            log("previous file can't be decrypted (passphrase changed?); building without a fallback")
            return None
        except ValueError:
            log("previous file unreadable; building without a fallback")
            return None
    else:
        payload = stored
    try:
        validate(payload, max_through=date.max)
    except SchemaError:
        log("previous file doesn't match the current schema; building without a fallback")
        return None
    return Previous(payload, canonical(payload), encrypted, salt)


def dropped(payload: dict, previous: dict | None, metric: str) -> bool:
    """True if `metric` returned far less data than last time, over the same dates."""
    if previous is None:
        return False
    field = DROP_FIELD[metric]
    new = old = 0
    sections = ("months",) if metric == "activities" else ("months", "days")
    for section in sections:
        key = ROW_KEYS[section]
        before = {row[key]: row for row in previous[section]}
        for row in payload[section]:
            if row[key] not in before or before[row[key]][field] is None:
                continue
            if metric == "activities":
                new += row[field] or 0
                old += before[row[key]][field]
            else:
                new += row[field] is not None
                old += 1
    return old >= DROP_MIN and new < DROP_RATIO * old


def carry_over(payload: dict, previous: dict | None, metric: str) -> None:
    """Copy `metric`'s fields from the previous payload, matching rows by date."""
    if previous is None:
        return
    owned = OWNED[metric]
    for section, key in ROW_KEYS.items():
        fields = owned.get(section, ())
        if not fields:
            continue
        before = {row[key]: row for row in previous[section]}
        for row in payload[section]:
            if row[key] in before:
                for field in fields:
                    row[field] = before[row[key]][field]
    for field in owned.get("d30", ()):
        payload["summary"]["d30"][field] = previous["summary"]["d30"][field]
    for field in owned.get("summary", ()):
        payload["summary"][field] = previous["summary"][field]
    for field in owned.get("top", ()):
        payload[field] = previous[field]


def key_expiring(value: str | None, today: date, log: Log) -> bool:
    if not value:
        return False
    try:
        expires = date.fromisoformat(value.strip())
    except ValueError:
        log(f"{KEY_EXPIRES_ENV} isn't a date like 2027-11-01")
        return True
    left = (expires - today).days
    if left <= KEY_WARNING_DAYS:
        when = "has expired" if left < 0 else f"expires in {left} day(s)"
        log(f"the Garmin API key {when}: create a new key and update the GARMIN_PERSONAL_API_KEY secret")
        return True
    return False


def write(path: Path, body: str, passphrase: str | None, salt: bytes | None) -> None:
    """Write atomically: plain JSON, or the encrypted envelope when a passphrase is given."""
    if passphrase:
        content = canonical(crypto.encrypt(body.encode("utf-8"), passphrase, salt=salt))
    else:
        content = body
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content + "\n", encoding="utf-8")
    os.replace(temporary, path)


def summarise(payload: dict, log: Log) -> None:
    """Counts only, for dry runs."""
    def present(rows, field):
        return sum(row[field] is not None for row in rows)

    days, months = payload["days"], payload["months"]
    log(f"days: {len(days)} · sleep {present(days, 'sleep_min')} · HRV {present(days, 'hrv')} · "
        f"resting HR {present(days, 'rhr')} · Body Battery {present(days, 'bb')}")
    log(f"weeks: {len(payload['weeks'])} · months: {len(months)}"
        + (f" ({months[0]['m']} to {months[-1]['m']})" if months else ""))
    calendar = payload["calendar"]
    if calendar:
        log(f"calendar: {sum(1 for level in calendar['levels'] if level)} active days of {len(calendar['levels'])}")
    log(f"size: {len(canonical(payload))} bytes")


# -- the run ------------------------------------------------------------------

def run(
    *,
    client,
    config: HealthConfig,
    now: datetime,
    out_path: Path,
    passphrase: str | None,
    key_expires: str | None = None,
    dry_run: bool = False,
    log: Log = print,
) -> int:
    if config.private and not passphrase and not dry_run:
        log(f"stopped: the page is private and {PASSPHRASE_ENV} is not set; refusing to write unencrypted data")
        return EXIT_FATAL
    through = publish_cutoff(now, config.delay_hours)
    if through < config.since:
        log("stopped: nothing to publish yet")
        return EXIT_FATAL
    log(f"publishing through {through.isoformat()}")

    previous = read_previous(out_path, passphrase, log)
    before = previous.payload if previous else None

    try:
        values, failures = collect(client, config, through, log)
    except garmin.GarminAuthError as exc:
        log(f"stopped: {exc}")
        return EXIT_FATAL
    if not values:
        log("stopped: every metric failed; nothing written")
        return EXIT_FATAL

    payload = build_payload(Inputs(**{m: values.get(m) for m in METRICS}), through, {})
    for metric in values:
        if dropped(payload, before, metric):
            failures[metric] = "far less data than the previous build"
            log(f"{metric}: far less data than last time; keeping the previous values")
    for metric in failures:
        carry_over(payload, before, metric)

    sources: dict[str, str] = {}
    for metric in config.metrics:
        if metric not in failures:
            sources[metric] = through.isoformat()
        elif before and metric in before["sources"]:
            sources[metric] = before["sources"][metric]
    payload["sources"] = sources

    try:
        validate(payload, max_through=through)
    except SchemaError as exc:
        log(f"stopped: the payload failed the privacy/schema check ({exc})")
        return EXIT_FATAL

    body = canonical(payload)
    if dry_run:
        summarise(payload, log)
        log("dry run; nothing written")
    elif previous and previous.body == body and previous.encrypted == config.private:
        log("no changes; nothing written")
    else:
        write(out_path, body, passphrase if config.private else None, previous.salt if previous else None)
        log(f"wrote {out_path.name} ({'encrypted' if config.private else 'plain'})")

    attention = bool(failures)
    if key_expiring(key_expires, now.date(), log):
        attention = True
    return EXIT_ATTENTION if attention else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="where to write (default _data/health.json)")
    parser.add_argument("--dry-run", action="store_true", help="fetch and check everything, write nothing")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")

    try:
        config = load_config()
    except (ConfigError, OSError) as exc:
        print(f"stopped: {exc}")
        return EXIT_FATAL
    try:
        client = garmin.GarminClient(garmin.load_api_key(), allowed=BUILD_ENDPOINTS)
    except garmin.GarminConfigError as exc:
        print(f"stopped: {exc}")
        return EXIT_FATAL
    return run(
        client=client,
        config=config,
        now=datetime.now(timezone.utc),
        out_path=args.out,
        passphrase=os.environ.get(PASSPHRASE_ENV) or None,
        key_expires=os.environ.get(KEY_EXPIRES_ENV),
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
