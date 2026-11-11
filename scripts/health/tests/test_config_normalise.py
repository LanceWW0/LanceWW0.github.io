import json
from dataclasses import asdict
from datetime import date

import pytest

from scripts.health import config, normalise
from scripts.health.categories import GROUPS, group_for
from scripts.health.tests.raw_fixtures import POISON, raw_activity, raw_daily, raw_hrv, raw_sleep

DAY = date(2026, 11, 8)


# -- config -------------------------------------------------------------------

def test_repo_config_loads():
    loaded = config.load_config()
    assert loaded.visibility in ("private", "public")
    assert loaded.delay_hours >= 24
    assert loaded.since == date(2023, 1, 1)
    assert loaded.metrics == config.METRICS


@pytest.mark.parametrize("raw", [None, {}, {"health": None}, {"health": {"visibility": "Public"}},
                                 {"health": {"visibility": "yes"}}, {"health": {"visibility": True}}])
def test_visibility_fails_closed(raw):
    assert config.parse_config(raw).private


def test_public_must_be_spelled_exactly():
    assert not config.parse_config({"health": {"visibility": "public"}}).private


@pytest.mark.parametrize("delay", [0, 12, 23, "48", 24.5, True])
def test_delay_cannot_be_weakened_or_malformed(delay):
    with pytest.raises(config.ConfigError):
        config.parse_config({"health": {"delay_hours": delay}})


def test_longer_delay_allowed():
    assert config.parse_config({"health": {"delay_hours": 48}}).delay_hours == 48


@pytest.mark.parametrize("metrics", [[], ["sleep", "steps"], "sleep", None])
def test_metrics_must_be_known(metrics):
    with pytest.raises(config.ConfigError):
        config.parse_config({"health": {"metrics": metrics}})


def test_metrics_keep_canonical_order_and_since_parses():
    parsed = config.parse_config({"health": {"metrics": ["activities", "sleep"], "since": "2024-02-01"}})
    assert parsed.metrics == ("sleep", "activities")
    assert parsed.since == date(2024, 2, 1)
    with pytest.raises(config.ConfigError):
        config.parse_config({"health": {"since": "last year"}})


# -- sport groups -------------------------------------------------------------

@pytest.mark.parametrize(("type_key", "group"), [
    ("running", "run"), ("trail_running", "run"), ("road_biking", "ride"), ("cycling", "ride"),
    ("hiking", "walk"), ("walking", "walk"), ("open_water_swimming", "swim"), ("strength_training", "strength"),
    ("bouldering", "climb"), ("kayaking", "paddle"), ("multi_sport", "other"), ("resort_skiing_snowboarding_ws", "other"),
    ("surfing", "other"), (None, "other"), (42, "other"),
])
def test_sport_groups(type_key, group):
    assert group_for(type_key) == group
    assert group in GROUPS


# -- normalisers --------------------------------------------------------------

def test_sleep_keeps_only_durations_and_score():
    out = normalise.sleep_days([raw_sleep(DAY)])
    assert out == {DAY: {"sleep_min": 450, "sleep_score": 81, "deep_min": 90, "light_min": 250, "rem_min": 110, "awake_min": 20}}


def test_hrv_keeps_nightly_value_and_baseline_band():
    out = normalise.hrv_days([raw_hrv(DAY)])
    assert out == {DAY: {"hrv": 61, "hrv_lo": 50, "hrv_hi": 70}}


def test_dailies_give_resting_hr_and_body_battery_peak():
    assert normalise.rhr_days([raw_daily(DAY)]) == {DAY: {"rhr": 49}}
    assert normalise.body_battery_days([raw_daily(DAY)]) == {DAY: {"bb": 88}}


def test_activity_keeps_date_group_and_numbers_only():
    (activity,) = normalise.activities([raw_activity(DAY, 3)])
    assert asdict(activity) == {
        "day": DAY, "group": "run", "km": 8.0, "seconds": 2640.0, "moving_seconds": 2560.0, "load": 85,
        "zones": (300.0, 1200.0, 900.0, 180.0, 60.0),
        "bests": (("1k", 287.0), ("mile", 470.0), ("5k", 1500.0)),
    }


def test_movement_keeps_steps_floors_and_intensity_minutes():
    assert normalise.movement_days([raw_daily(DAY)]) == {
        DAY: {"steps": 8080, "floors": 12, "im_mod": 20, "im_vig": 10, "im_goal": 150}
    }


def test_day_without_steps_means_watch_not_worn():
    raw = raw_daily(DAY)
    raw["movement"]["steps"]["value"] = 0
    assert normalise.movement_days([raw]) == {}


def test_best_splits_only_for_runs_and_glitches_dropped():
    walk = raw_activity(DAY, 0, type_key="walking")
    assert normalise.activities([walk])[0].bests == ()
    glitch = raw_activity(DAY, 0)
    glitch["fastestSplit_1000"] = 95.0  # faster than the world record: a GPS glitch
    assert "1k" not in dict(normalise.activities([glitch])[0].bests)


def test_activity_without_zone_data_has_no_zones():
    raw = raw_activity(DAY, 0)
    for z in range(1, 6):
        del raw[f"hrTimeInZone_{z}"]
    assert normalise.activities([raw])[0].zones is None


def test_no_poison_survives_normalising():
    outputs = [
        normalise.sleep_days([raw_sleep(DAY)]),
        normalise.hrv_days([raw_hrv(DAY)]),
        normalise.rhr_days([raw_daily(DAY)]),
        normalise.body_battery_days([raw_daily(DAY)]),
        normalise.movement_days([raw_daily(DAY)]),
        [asdict(a) for a in normalise.activities([raw_activity(DAY, i) for i in range(5)])],
    ]
    text = repr(outputs)
    for secret in POISON:
        assert secret not in text, secret


def test_missing_or_out_of_range_values_are_dropped_not_published():
    night = raw_sleep(DAY, seconds=0)
    assert normalise.sleep_days([night]) == {}
    weird = raw_sleep(DAY)
    weird["sleepScores"]["overall"]["value"] = 1_762_590_000_000  # an epoch where a score should be
    assert normalise.sleep_days([weird])[DAY]["sleep_score"] is None
    bad_hrv = raw_hrv(DAY) | {"lastNightAvg": None}
    assert normalise.hrv_days([bad_hrv]) == {}
    bad_day = raw_daily(DAY)
    bad_day["heartRate"]["restingValue"] = 51.5073509 * 1000
    assert normalise.rhr_days([bad_day]) == {}
    assert normalise.sleep_days([raw_sleep(DAY) | {"calendarDate": "2026-13-01"}]) == {}


def test_activity_without_moving_time_falls_back_to_duration():
    raw = raw_activity(DAY, 0)
    raw["movingDuration"] = None
    (activity,) = normalise.activities([raw])
    assert activity.moving_seconds == activity.seconds


def test_activity_without_a_start_date_is_skipped():
    raw = raw_activity(DAY, 0)
    raw["startTimeLocal"] = None
    assert normalise.activities([raw]) == []


@pytest.mark.parametrize(("response", "key"), [({"oops": 1}, None), ([1, 2], "data"), ({"data": "x"}, "data")])
def test_unexpected_shapes_are_errors(response, key):
    with pytest.raises(normalise.NormaliseError) as excinfo:
        normalise.records(response, key, "daily-summaries")
    assert str(excinfo.value) == "daily-summaries: unexpected response shape"


def test_records_handles_empty_and_skips_non_objects():
    assert normalise.records(None, "data", "x") == []
    assert normalise.records({"data": None}, "data", "x") == []
    assert normalise.records([{"a": 1}, "junk", 3], None, "x") == [{"a": 1}]
