import json
from datetime import date, datetime, timedelta, timezone

import pytest

from scripts.health import build, crypto, garmin
from scripts.health.config import HealthConfig
from scripts.health.schema import validate
from scripts.health.tests.raw_fixtures import POISON, FakeGarmin

NOW = datetime(2026, 11, 10, 13, 23, tzinfo=timezone.utc)  # cutoff: 8 Nov
THROUGH = date(2026, 11, 8)
FIRST = date(2026, 6, 1)
PASS = "test passphrase words"


@pytest.fixture(autouse=True)
def fast_kdf(monkeypatch):
    monkeypatch.setattr(crypto, "ITERATIONS", 1_000)
    monkeypatch.setattr(crypto.encrypt, "__kwdefaults__", {"salt": None, "iterations": 1_000})


def config(visibility="private", **overrides):
    return HealthConfig(visibility=visibility, since=FIRST, **overrides)


def client(session):
    return garmin.GarminClient(
        "k", session=session, min_interval=0, max_retries=0, on_token=None, sleep=lambda s: None,
        allowed=build.BUILD_ENDPOINTS,
    )


def go(tmp_path, *, session=None, cfg=None, now=NOW, passphrase=PASS, **kwargs):
    session = session or FakeGarmin(FIRST)
    lines: list[str] = []
    code = build.run(
        client=client(session), config=cfg or config(), now=now, out_path=tmp_path / "health.json",
        passphrase=passphrase, log=lines.append, **kwargs,
    )
    return code, lines, session


def read(tmp_path, passphrase=PASS):
    stored = json.loads((tmp_path / "health.json").read_text())
    if crypto.is_envelope(stored):
        return json.loads(crypto.decrypt(stored, passphrase)), stored
    return stored, None


def test_private_build_writes_an_encrypted_valid_payload(tmp_path):
    code, lines, session = go(tmp_path)
    assert code == build.EXIT_OK
    payload, envelope = read(tmp_path)
    assert envelope is not None
    validate(payload, max_through=THROUGH)
    assert payload["through"] == "2026-11-08"
    assert payload["sources"] == dict.fromkeys(("sleep", "hrv", "rhr", "body_battery", "activities"), "2026-11-08")
    assert payload["days"][-1]["sleep_min"] == 450
    assert payload["summary"]["d30"]["workouts"] == 15
    # only the four build endpoints were called, and dailies only once for two metrics
    assert set(session.calls) == {"token", "sleep-summaries", "hrv-range", "daily-summaries", "activities"}
    assert session.calls.count("daily-summaries") == 1


def test_public_build_writes_plain_json(tmp_path):
    code, _, _ = go(tmp_path, cfg=config("public"), passphrase=None)
    assert code == build.EXIT_OK
    payload, envelope = read(tmp_path)
    assert envelope is None and payload["schema"] == 1


def test_nothing_personal_reaches_the_file_or_the_logs(tmp_path):
    _, lines, _ = go(tmp_path, cfg=config("public"), passphrase=None)
    text = (tmp_path / "health.json").read_text() + "\n".join(lines)
    for secret in POISON:
        assert secret not in text, secret
    assert all("07:" not in line for line in lines)


def test_private_without_passphrase_refuses_before_calling_garmin(tmp_path):
    code, lines, session = go(tmp_path, passphrase=None)
    assert code == build.EXIT_FATAL
    assert session.calls == []
    assert not (tmp_path / "health.json").exists()
    assert "refusing to write unencrypted data" in lines[0]


def test_unchanged_data_is_not_rewritten(tmp_path):
    go(tmp_path)
    first_bytes = (tmp_path / "health.json").read_bytes()
    code, lines, _ = go(tmp_path)
    assert code == build.EXIT_OK
    assert "no changes; nothing written" in lines
    assert (tmp_path / "health.json").read_bytes() == first_bytes


def test_salt_is_kept_and_iv_changes_between_writes(tmp_path):
    go(tmp_path)
    _, first = read(tmp_path)
    go(tmp_path, now=NOW + timedelta(days=1))
    payload, second = read(tmp_path)
    assert payload["through"] == "2026-11-09"
    assert second["salt"] == first["salt"]
    assert second["iv"] != first["iv"]


def test_failed_metric_keeps_previous_values_and_asks_for_attention(tmp_path):
    go(tmp_path)
    before, _ = read(tmp_path)
    code, lines, _ = go(tmp_path, session=FakeGarmin(FIRST, fail={"hrv-range"}), now=NOW + timedelta(days=1))
    after, _ = read(tmp_path)

    assert code == build.EXIT_ATTENTION
    assert any(line.startswith("hrv: failed (hrv-range: HTTP 503)") for line in lines)
    assert after["sources"]["hrv"] == "2026-11-08"  # still the last good build
    assert after["sources"]["sleep"] == "2026-11-09"
    old = {row["d"]: row["hrv"] for row in before["days"]}
    for row in after["days"]:
        assert row["hrv"] == old.get(row["d"])  # carried over; the new day is unknown
    assert after["days"][-1]["hrv"] is None
    assert after["days"][-1]["sleep_min"] is not None
    assert after["summary"]["d30"]["hrv"] == before["summary"]["d30"]["hrv"]


def test_failed_activities_keep_calendar_and_totals(tmp_path):
    go(tmp_path)
    before, _ = read(tmp_path)
    code, _, _ = go(tmp_path, session=FakeGarmin(FIRST, fail={"activities"}), now=NOW + timedelta(days=1))
    after, _ = read(tmp_path)
    assert code == build.EXIT_ATTENTION
    assert after["calendar"] == before["calendar"]
    assert after["summary"]["totals"] == before["summary"]["totals"]
    assert after["weeks"][-1]["workouts"] == before["weeks"][-1]["workouts"]


def test_failure_on_the_first_ever_run_publishes_nulls(tmp_path):
    code, _, _ = go(tmp_path, session=FakeGarmin(FIRST, fail={"daily-summaries"}))
    payload, _ = read(tmp_path)
    assert code == build.EXIT_ATTENTION
    assert payload["days"][-1]["rhr"] is None and payload["days"][-1]["bb"] is None
    assert "rhr" not in payload["sources"] and "body_battery" not in payload["sources"]


def test_sudden_drop_in_data_is_treated_as_a_failure(tmp_path):
    go(tmp_path)
    before, _ = read(tmp_path)
    code, lines, _ = go(tmp_path, session=FakeGarmin(FIRST, sleep_every=5), now=NOW + timedelta(days=1))
    after, _ = read(tmp_path)
    assert code == build.EXIT_ATTENTION
    assert "sleep: far less data than last time; keeping the previous values" in lines
    old = {row["d"]: row["sleep_min"] for row in before["days"]}
    assert all(row["sleep_min"] == old.get(row["d"]) for row in after["days"])


@pytest.mark.parametrize("status", [401, 403])
def test_rejected_key_stops_without_touching_the_file(tmp_path, status):
    go(tmp_path)
    original = (tmp_path / "health.json").read_bytes()
    code, lines, _ = go(tmp_path, session=FakeGarmin(FIRST, token_status=status), now=NOW + timedelta(days=1))
    assert code == build.EXIT_FATAL
    assert lines[-1].startswith("stopped: token: HTTP")
    assert (tmp_path / "health.json").read_bytes() == original


def test_every_metric_failing_writes_nothing(tmp_path):
    session = FakeGarmin(FIRST, fail={"sleep-summaries", "hrv-range", "daily-summaries", "activities"})
    code, lines, _ = go(tmp_path, session=session)
    assert code == build.EXIT_FATAL
    assert lines[-1] == "stopped: every metric failed; nothing written"
    assert not (tmp_path / "health.json").exists()


def test_switching_to_public_rewrites_even_if_data_is_unchanged(tmp_path):
    go(tmp_path)
    code, lines, _ = go(tmp_path, cfg=config("public"))
    assert code == build.EXIT_OK
    payload, envelope = read(tmp_path)
    assert envelope is None and payload["through"] == "2026-11-08"
    assert "wrote health.json (plain)" in lines


def test_changed_passphrase_rebuilds_without_fallback_and_new_salt(tmp_path):
    go(tmp_path)
    _, first = read(tmp_path)
    code, lines, _ = go(tmp_path, passphrase="a different passphrase")
    _, second = read(tmp_path, "a different passphrase")
    assert code == build.EXIT_OK
    assert any("can't be decrypted" in line for line in lines)
    assert second["salt"] != first["salt"]


def test_dry_run_writes_nothing_and_prints_counts_only(tmp_path):
    code, lines, _ = go(tmp_path, dry_run=True, passphrase=None)
    assert code == build.EXIT_OK
    assert not (tmp_path / "health.json").exists()
    assert lines[-1] == "dry run; nothing written"
    summary = "\n".join(lines)
    assert "days: 90 · sleep 90 · HRV 90 · resting HR 90 · Body Battery 90" in summary
    assert "months: 5 (2026-06 to 2026-10)" in summary


@pytest.mark.parametrize(("expires", "code"), [("2026-11-30", 0), ("2026-11-17", 2), ("2026-11-01", 2), ("soon", 2)])
def test_key_expiry_warning(tmp_path, expires, code):
    result, lines, _ = go(tmp_path, key_expires=expires)
    assert result == code
    if code:
        assert "GARMIN_PERSONAL_API_KEY" in lines[-1] or "isn't a date" in lines[-1]


def test_disabled_metrics_are_not_fetched_or_published(tmp_path):
    cfg = config(metrics=("sleep", "activities"))
    code, _, session = go(tmp_path, cfg=cfg)
    payload, _ = read(tmp_path)
    assert code == build.EXIT_OK
    assert set(session.calls) == {"token", "sleep-summaries", "activities"}
    assert set(payload["sources"]) == {"sleep", "activities"}
    assert payload["days"][-1]["hrv"] is None


def test_build_client_cannot_reach_probe_only_endpoints():
    c = client(FakeGarmin(FIRST))
    with pytest.raises(ValueError):
        c.get(garmin.SLEEP_DAY_PATH, {"date": "2026-11-08"})
    with pytest.raises(ValueError):
        c.get(garmin.hrv_day_path(THROUGH))


def test_nothing_after_the_cutoff_is_requested(tmp_path):
    session = FakeGarmin(FIRST)
    seen_dates = []
    original = session.request

    def spy(method, url, headers=None, params=None, timeout=None):
        seen_dates.extend(v for v in (params or {}).values() if isinstance(v, str) and len(v) == 10)
        seen_dates.extend(url.rsplit("/", 2)[-2:] if "/hrv/daily/" in url else [])
        return original(method, url, headers=headers, params=params, timeout=timeout)

    session.request = spy
    go(tmp_path, session=session)
    assert seen_dates and max(seen_dates) == "2026-11-08"
