import logging
from datetime import date, datetime, timedelta, timezone

import pytest

from scripts.health import garmin
from scripts.health.dates import chunk_range, publish_cutoff

UTC = timezone.utc


# -- API key discovery -------------------------------------------------------

def test_env_var_wins_over_key_file(tmp_path):
    key_file = tmp_path / "key"
    key_file.write_text("from-file")
    assert garmin.load_api_key({garmin.API_KEY_ENV: " from-env \n"}, key_file) == "from-env"


def test_key_file_used_when_env_unset(tmp_path):
    key_file = tmp_path / "key"
    key_file.write_text("  from-file\n")
    key_file.chmod(0o600)
    assert garmin.load_api_key({}, key_file) == "from-file"


def test_missing_key_is_a_config_error(tmp_path):
    with pytest.raises(garmin.GarminConfigError, match="no API key"):
        garmin.load_api_key({}, tmp_path / "absent")


def test_empty_key_file_is_a_config_error(tmp_path):
    key_file = tmp_path / "key"
    key_file.write_text("\n")
    key_file.chmod(0o600)
    with pytest.raises(garmin.GarminConfigError, match="empty"):
        garmin.load_api_key({}, key_file)


def test_world_readable_key_file_warns(tmp_path, caplog):
    key_file = tmp_path / "key"
    key_file.write_text("SUPER-SECRET-VALUE")
    key_file.chmod(0o644)
    with caplog.at_level(logging.WARNING):
        garmin.load_api_key({}, key_file)
    assert "chmod 600" in caplog.text
    assert "SUPER-SECRET-VALUE" not in caplog.text  # the key itself is never logged


# -- publish cutoff ----------------------------------------------------------

def day_end_in_last_zone(d: date) -> datetime:
    """When calendar day `d` finishes in UTC−12, expressed in UTC."""
    return datetime(d.year, d.month, d.day, tzinfo=UTC) + timedelta(days=1, hours=12)


def test_cutoff_example_from_the_plan():
    # Cron at 13:23 UTC on 12 Nov publishes up to 10 Nov.
    assert publish_cutoff(datetime(2026, 11, 12, 13, 23, tzinfo=UTC)) == date(2026, 11, 10)


def test_cutoff_is_always_at_least_delay_after_the_day_ends_everywhere():
    start = datetime(2026, 3, 25, tzinfo=UTC)  # spans the UK clock change
    for hours in range(0, 24 * 10):
        now = start + timedelta(hours=hours, minutes=17)
        for delay in (0, 24, 36):
            cutoff = publish_cutoff(now, delay)
            # The published day is old enough...
            assert day_end_in_last_zone(cutoff) + timedelta(hours=delay) <= now
            # ...and it is the newest such day (no needless extra delay).
            assert day_end_in_last_zone(cutoff + timedelta(days=1)) + timedelta(hours=delay) > now


def test_travelling_west_never_publishes_the_current_local_day():
    # 23:00 on 11 Nov in UTC−8 is 07:00 on 12 Nov UTC. A London-based
    # "yesterday" rule would publish 11 Nov here: the day still in progress.
    now = datetime(2026, 11, 12, 7, 0, tzinfo=UTC)
    assert publish_cutoff(now) <= date(2026, 11, 9)


def test_cutoff_accepts_other_timezones_and_rejects_naive():
    tokyo = timezone(timedelta(hours=9))
    assert publish_cutoff(datetime(2026, 11, 12, 22, 23, tzinfo=tokyo)) == date(2026, 11, 10)
    with pytest.raises(ValueError):
        publish_cutoff(datetime(2026, 11, 12, 13, 0))
    with pytest.raises(ValueError):
        publish_cutoff(datetime(2026, 11, 12, tzinfo=UTC), -1)


# -- chunking ----------------------------------------------------------------

def test_chunks_cover_range_inclusively_without_overlap():
    chunks = list(chunk_range(date(2026, 1, 1), date(2026, 3, 5), 31))
    assert chunks == [
        (date(2026, 1, 1), date(2026, 1, 31)),
        (date(2026, 2, 1), date(2026, 3, 3)),
        (date(2026, 3, 4), date(2026, 3, 5)),
    ]
    for start, end in chunks:
        assert (end - start).days + 1 <= 31


def test_single_day_and_empty_ranges():
    assert list(chunk_range(date(2026, 1, 1), date(2026, 1, 1), 31)) == [(date(2026, 1, 1), date(2026, 1, 1))]
    assert list(chunk_range(date(2026, 1, 2), date(2026, 1, 1), 31)) == []
    with pytest.raises(ValueError):
        list(chunk_range(date(2026, 1, 1), date(2026, 1, 2), 0))
