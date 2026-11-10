"""The probe must describe data shapes without ever printing personal values.

Fixtures are synthetic and deliberately stuffed with things that must not
leak: coordinates, place names, free text, times and IDs.
"""
from datetime import date
from urllib.parse import urlparse

import pytest

from scripts.health import garmin, probe
from scripts.health.tests.fakes import FakeResponse

CUTOFF = date(2026, 11, 8)

SECRETS = [
    "London",
    "Hyde Park",
    "51.5073",
    "-0.1277",
    "07:12",
    "23:41",
    "987654321",
    "123456789012",
    "Forerunner",
    "27123",
]


def sleep_record(day: int) -> dict:
    return {
        "calendarDate": f"2026-11-{day:02d}",
        "sleepTimeSeconds": 27123,
        # 23:41 the night before → 07:12 on calendarDate, as local-epoch ms
        "sleepStartTimestampLocal": int((date(2026, 11, day).toordinal() - 719163) * 86400e3 - 18e5 - 1.14e6),
        "sleepEndTimestampLocal": int((date(2026, 11, day).toordinal() - 719163) * 86400e3 + 25920e3),
        "sleepScores": {"overall": {"value": 84}},
        "deepSleepSeconds": 5400,
        "deviceName": "Forerunner 965",
    }


def activity(i: int) -> dict:
    return {
        "activityId": 123456789012 + i,
        "activityName": "London Running",
        "description": "Loop of Hyde Park",
        "locationName": "London",
        "startLatitude": 51.5073509,
        "startLongitude": -0.1277583,
        "startTimeLocal": "2026-11-07 07:12:33",
        "activityType": {"typeKey": "running" if i % 2 else "strength_training"},
        "distance": 10234.5,
        "duration": 3120.4,
        "movingDuration": 3001.0,
        "ownerId": 987654321,
    }


def route(path: str, params: dict):
    if path == garmin.SLEEP_SUMMARIES_PATH:
        return [sleep_record(d) for d in range(1, 9)]
    if path == garmin.SLEEP_DAY_PATH:
        return {"dailySleepDTO": sleep_record(8)}
    if path.startswith("/hrv-service/hrv/daily/"):
        return {
            "userProfilePk": 987654321,
            "hrvSummaries": [{"calendarDate": "2026-11-08", "lastNightAvg": 62, "weeklyAvg": 60, "status": "BALANCED"}],
        }
    if path.startswith("/hrv-service/hrv/"):
        return None  # 204 for a single day
    if path == garmin.DAILY_SUMMARIES_PATH:
        return [{"calendarDate": "2026-11-08", "restingHeartRate": 48, "bodyBatteryHighestValue": 87}]
    if path == garmin.BODY_BATTERY_PATH:
        return [{"date": "2026-11-08", "charged": 60, "bodyBatteryValuesArray": [[1762590000000, 87]]}]
    if path == garmin.ACTIVITIES_PATH:
        if params.get("startDate", "").startswith("2023"):
            return []
        start, limit = int(params["start"]), int(params["limit"])
        items = [activity(i) for i in range(50)]
        return items[start:start + limit]
    raise AssertionError(f"unexpected path {path}")


class RoutingSession:
    def __init__(self):
        self.paths = []

    def request(self, method, url, headers=None, params=None, timeout=None):
        path = urlparse(url).path
        self.paths.append(path)
        if method == "POST":
            return FakeResponse(200, text="eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjg2NDAwLCJpYXQiOjAsInNjb3BlIjoiUEVSU09OQUxfQVBJX1dFTExORVNTX1JFQUQiLCJzdWIiOiI5ODc2NTQzMjEifQ.sig")
        body = route(path, dict(params or {}))
        return FakeResponse(204) if body is None else FakeResponse(200, json_body=body)


def make_client():
    session = RoutingSession()
    client = garmin.GarminClient("k", session=session, min_interval=0, on_token=None, sleep=lambda s: None)
    return client, session


def run(capsys, **kwargs):
    client, session = make_client()
    report = probe.Report()
    code = probe.run_probe(client, CUTOFF, kwargs.get("days", 8), kwargs.get("history", True), None, report)
    out = capsys.readouterr().out
    assert out == report.text()
    return code, out, session


def test_report_never_contains_personal_values(capsys):
    code, out, _ = run(capsys)
    assert code == 0
    for secret in SECRETS:
        assert secret not in out, f"leaked {secret!r}"


def test_report_flags_fields_the_build_must_never_read(capsys):
    _, out, _ = run(capsys)
    lines = {line.split()[0]: line for line in out.splitlines() if line.startswith("   ") and line.split()}
    assert "GEO" in lines["[].startLatitude"]
    assert "GEO" in lines["[].locationName"]
    assert "TEXT" in lines["[].activityName"]
    assert "TEXT" in lines["[].description"]
    assert "TIME" in lines["[].startTimeLocal"]
    assert "TIME" in lines["[].sleepStartTimestampLocal"]
    assert "TIME" in lines["[].bodyBatteryValuesArray[][]"]
    assert "ID" in lines["[].activityId"] and "TIME" not in lines["[].activityId"]
    assert "ID" in lines["[].ownerId"]


def test_report_answers_the_gate_questions(capsys):
    _, out, _ = run(capsys)
    assert "token exchange ok · JWT · lifetime ~24.0h · scopes: PERSONAL_API_WELLNESS_READ" in out
    assert "calendarDate = wake date for 8/8 nights; = bedtime date for 0/8" in out
    assert "sleepScores.overall.value (8/8)" in out
    assert "lastNightAvg" in out
    assert "restingHeartRate (1/1)" in out
    assert "bodyBatteryHighestValue (1/1)" in out
    assert "values (enum, safe to show): BALANCED×1" in out
    assert "running×25" in out and "strength_training×25" in out
    assert "activities page limit 100: ok · 50 returned" in out
    assert "2023: activities 0" in out
    assert "total ≈" in out


def test_probe_only_uses_allowlisted_endpoints_and_stops_at_cutoff(capsys):
    _, out, session = run(capsys)
    for path in session.paths[1:]:
        garmin.endpoint_label(path)  # raises if not allowlisted
    assert "2026-11-09" not in out
    assert not any("2026-11-09" in p or "2026-11-1" in p for p in session.paths)


def test_smoke_prints_status_only(capsys):
    client, _ = make_client()
    assert probe.run_smoke(client, CUTOFF) == 0
    assert capsys.readouterr().out == "token exchange: ok\ndaily-summaries: ok · 2 requests\n"


def test_smoke_reports_rejected_key_without_details(capsys):
    class Rejecting:
        def request(self, *a, **k):
            return FakeResponse(401, text="invalid key k-123")

    client = garmin.GarminClient("k-123", session=Rejecting(), min_interval=0, on_token=None, sleep=lambda s: None)
    assert probe.run_smoke(client, CUTOFF) == 1
    out = capsys.readouterr().out
    assert "expired, revoked or wrong" in out and "k-123" not in out


def test_raw_output_refuses_folders_inside_the_repo(tmp_path):
    with pytest.raises(SystemExit):
        probe.check_raw_dir(probe.REPO_ROOT / ".garmin-probe")
    with pytest.raises(SystemExit):
        probe.check_raw_dir(probe.REPO_ROOT)
    assert probe.check_raw_dir(tmp_path / "raw") == (tmp_path / "raw").resolve()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "null"),
        (True, "bool"),
        (1762590000000, "epoch-ms?"),
        (1762590000, "int ~1e9"),
        (51.5073509, "float ~1e1"),
        (0, "int 0"),
        ("2026-11-08", "date"),
        ("2026-11-08T07:12:33.0", "datetime"),
        ("07:12", "time"),
        ("running", "word"),
        ("London Running", "text"),
    ],
)
def test_classify(value, expected):
    assert probe.classify("someKey", value) == expected


def test_epoch_seconds_detected_only_for_time_like_keys():
    assert probe.classify("startTimeGMT", 1762590000) == "epoch-s?"
    assert probe.classify("durationInSeconds", 1762590000) == "int ~1e9"


@pytest.mark.parametrize(
    ("path", "flag"),
    [
        # Real fields from the first probe run whose values look like plain numbers.
        ("[].sleepNeed.recommendedBedtimeStartMins", "TIME"),
        ("[].sleepAlignment.lastSleepMidpointMins", "TIME"),
        ("[].sleepAlignment.optimalSleepWindowEndMins", "TIME"),
        ("data[].pulseOx.avgAltitudeInMeters", "GEO"),
        ("[].maxElevation", "GEO"),
    ],
)
def test_numeric_fields_flagged_by_name(path, flag):
    assert flag in probe.flags_for(path, {"int ~1e2"})


@pytest.mark.parametrize(
    "path", ["[].sleepTimeSeconds", "[].movingDuration", "data[].stress.activityDurationInMillis", "[].distance"]
)
def test_values_the_build_needs_are_not_flagged(path):
    assert probe.flags_for(path, {"int ~1e3"}) == ""


@pytest.mark.parametrize("key", ["activityId", "ownerId", "userProfilePk", "deviceID"])
def test_identifiers_get_their_own_class(key):
    assert probe.classify(key, 123456789012) == "id"
    assert "ID" in probe.flags_for(f"[].{key}", {"id"})
