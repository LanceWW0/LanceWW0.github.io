"""Date helpers shared by the probe and the build.

Everything published is dated by calendar day. The only time-of-day logic in
the whole job is the publish cutoff below, which works from "now".
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Iterator

# UTC−12 is the last zone on Earth to finish any given calendar day.
_LAST_ZONE_TO_END_A_DAY = timedelta(hours=12)


def publish_cutoff(now_utc: datetime, delay_hours: int = 24) -> date:
    """Return the newest date that may be published at `now_utc`.

    A date is publishable only once it has been over for at least
    `delay_hours` in every time zone. Measuring from UTC−12, where each day
    ends last, means travelling can never shorten the delay.

    Day D ends in UTC−12 at (D+1) 12:00 UTC, so D is publishable when
    (D+1) 12:00 UTC + delay <= now, i.e. D <= date(now − 12h − delay) − 1.
    """
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be timezone-aware")
    if delay_hours < 0:
        raise ValueError("delay_hours must not be negative")
    reference = now_utc.astimezone(timezone.utc) - _LAST_ZONE_TO_END_A_DAY - timedelta(hours=delay_hours)
    return reference.date() - timedelta(days=1)


def chunk_range(start: date, end: date, max_days: int) -> Iterator[tuple[date, date]]:
    """Split the inclusive range start..end into chunks of at most `max_days` days."""
    if max_days < 1:
        raise ValueError("max_days must be at least 1")
    if end < start:
        return
    cursor = start
    step = timedelta(days=max_days - 1)
    while cursor <= end:
        chunk_end = min(cursor + step, end)
        yield cursor, chunk_end
        cursor = chunk_end + timedelta(days=1)
