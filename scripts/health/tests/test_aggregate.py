from datetime import date, timedelta

import pytest

from scripts.health.aggregate import Inputs, build_payload
from scripts.health.normalise import Activity

THROUGH = date(2026, 11, 8)  # a Sunday


def days_back(n: int, through: date = THROUGH):
    return [through - timedelta(days=i) for i in range(n)]


def run(day: date, km: float = 10.0, pace: float = 300, load: float = 100.0) -> Activity:
    return Activity(day, "run", km, km * pace * 1.05, km * pace, load)


def walk(day: date, km: float = 4.0, load: float = 20.0) -> Activity:
    return Activity(day, "walk", km, 3600.0, 3500.0, load)


def payload(through: date = THROUGH, **inputs) -> dict:
    return build_payload(Inputs(**inputs), through, {})


def test_nothing_after_the_cutoff_is_used():
    future = THROUGH + timedelta(days=1)
    p = payload(
        sleep={future: {"sleep_min": 999}, THROUGH: {"sleep_min": 400}},
        activities=[run(future), run(THROUGH)],
    )
    assert p["through"] == "2026-11-08"
    assert p["days"][-1]["d"] == "2026-11-08"
    assert p["days"][-1]["sleep_min"] == 400
    assert p["summary"]["totals"]["all"]["workouts"] == 1
    assert len(p["calendar"]["levels"]) == 365
    assert p["calendar"]["start"] == (THROUGH - timedelta(days=364)).isoformat()


def test_days_are_90_consecutive_and_missing_nights_are_null():
    p = payload(sleep={THROUGH: {"sleep_min": 420, "sleep_score": 80}})
    assert len(p["days"]) == 90
    assert p["days"][0]["d"] == (THROUGH - timedelta(days=89)).isoformat()
    assert p["days"][-2]["sleep_min"] is None
    assert p["days"][-1]["sleep_min"] == 420


def test_rolling_average_needs_four_of_seven_days():
    three = {d: {"rhr": 50} for d in days_back(3)}
    assert payload(rhr=three)["days"][-1]["rhr7"] is None
    four = {d: {"rhr": v} for d, v in zip(days_back(4), (48, 50, 52, 54))}
    assert payload(rhr=four)["days"][-1]["rhr7"] == 51


def test_30_day_averages_need_15_values_and_report_the_count():
    p = payload(sleep={d: {"sleep_min": 400, "sleep_score": 70} for d in days_back(14)})
    assert p["summary"]["d30"]["nights"] == 14
    assert p["summary"]["d30"]["sleep_min"] is None
    p = payload(sleep={d: {"sleep_min": 400 + i, "sleep_score": 70} for i, d in enumerate(days_back(15))})
    assert p["summary"]["d30"]["nights"] == 15
    assert p["summary"]["d30"]["sleep_min"] == 407


def test_sleep_stage_split_is_percentages():
    night = {"sleep_min": 450, "deep_min": 90, "light_min": 240, "rem_min": 100, "awake_min": 20}
    p = payload(sleep={d: dict(night) for d in days_back(20)})
    assert p["summary"]["stages30"] == {"deep": 20, "light": 53, "rem": 22, "awake": 4}


def test_only_complete_weeks_labelled_by_monday():
    saturday = THROUGH - timedelta(days=1)
    p_sun = payload(THROUGH, activities=[])
    p_sat = payload(saturday, activities=[])
    assert p_sun["weeks"][-1]["w"] == "2026-11-02"  # ends on 8 Nov (Sunday): complete
    assert p_sat["weeks"][-1]["w"] == "2026-10-26"  # 2–8 Nov isn't over yet
    assert len(p_sun["weeks"]) == 26
    assert all(date.fromisoformat(w["w"]).weekday() == 0 for w in p_sun["weeks"])


def test_week_spanning_new_year_is_labelled_by_its_december_monday():
    through = date(2027, 1, 3)  # Sunday
    p = payload(through, activities=[run(date(2026, 12, 29)), run(date(2027, 1, 2))])
    assert p["weeks"][-1] == {"w": "2026-12-28", "workouts": 2, "hours": 1.8, "run_km": 20.0, "pace_s": 300}


def test_pace_needs_three_km_and_ignores_glitches():
    monday = date(2026, 11, 2)
    assert payload(activities=[run(monday, km=2.5)])["weeks"][-1]["pace_s"] is None
    assert payload(activities=[run(monday, km=5, pace=330)])["weeks"][-1]["pace_s"] == 330
    assert payload(activities=[run(monday, km=5, pace=20)])["weeks"][-1]["pace_s"] is None


def test_walks_count_as_workouts_but_not_running_distance():
    week = payload(activities=[run(date(2026, 11, 3)), walk(date(2026, 11, 4))])["weeks"][-1]
    assert week["workouts"] == 2
    assert week["run_km"] == 10.0


def test_months_are_complete_from_first_data_and_include_type_counts():
    first = date(2026, 8, 20)
    acts = [run(date(2026, 8, 21)), walk(date(2026, 9, 2)), run(date(2026, 10, 30)), walk(date(2026, 10, 31)),
            run(date(2026, 11, 2))]
    p = payload(activities=acts, sleep={first: {"sleep_min": 400}})
    assert [m["m"] for m in p["months"]] == ["2026-08", "2026-09", "2026-10"]  # November isn't over
    october = p["months"][-1]
    assert october["types"] == {"run": 1, "walk": 1}
    assert october["workouts"] == 2
    assert october["sleep_min"] is None  # fewer than 10 nights


def test_month_ending_on_the_cutoff_is_included():
    p = payload(date(2026, 10, 31), activities=[run(date(2026, 10, 15))])
    assert p["months"][-1]["m"] == "2026-10"


def test_monthly_health_averages_need_ten_values():
    nights = {date(2026, 10, d): {"sleep_min": 400 + d} for d in range(1, 11)}
    assert payload(sleep=nights)["months"][-1]["sleep_min"] == 406


def test_calendar_levels_by_quartile_with_rest_days_zero():
    days = days_back(8)  # newest first: THROUGH gets the lightest load
    acts = [run(day, load=load) for day, load in zip(days, (10, 20, 30, 40, 50, 60, 70, 80))]
    acts.append(walk(THROUGH - timedelta(days=20), load=0))
    levels = payload(activities=acts)["calendar"]["levels"]
    assert levels[-1] == 1 and levels[-8] == 4
    assert levels[-21] == 1  # active but no recorded load
    assert levels[-9] == 0
    assert set(levels) <= {0, 1, 2, 3, 4}


def test_unknown_activities_are_null_not_zero():
    p = payload(sleep={THROUGH: {"sleep_min": 400}}, activities=None)
    assert p["calendar"] is None
    assert p["summary"]["totals"] is None
    assert p["summary"]["d30"]["workouts"] is None
    assert p["weeks"][-1]["workouts"] is None
    assert p["months"] == [] or p["months"][-1]["workouts"] is None


def test_no_activities_at_all_are_zeros():
    p = payload(activities=[])
    assert p["summary"]["totals"]["all"] == {"workouts": 0, "hours": 0.0, "run_km": 0.0}
    assert p["weeks"][-1]["workouts"] == 0
    assert set(p["calendar"]["levels"]) == {0}


def test_unknown_health_metrics_are_null():
    p = payload(activities=[run(THROUGH)])
    row = p["days"][-1]
    assert all(row[f] is None for f in ("sleep_min", "hrv", "hrv7", "rhr", "rhr7", "bb", "bb7"))
    assert p["summary"]["stages30"] is None


def test_totals_split_last_year_and_all_time():
    acts = [run(THROUGH - timedelta(days=10)), run(THROUGH - timedelta(days=400), km=5)]
    totals = payload(activities=acts)["summary"]["totals"]
    assert totals["y1"]["workouts"] == 1 and totals["y1"]["run_km"] == 10.0
    assert totals["all"]["workouts"] == 2 and totals["all"]["run_km"] == 15.0


@pytest.mark.parametrize("through", [date(2026, 3, 29), date(2026, 3, 30), date(2026, 10, 25)])
def test_clock_change_days_need_no_special_handling(through):
    # UK clocks change on these weekends; everything is dated by calendar day.
    p = payload(through, rhr={d: {"rhr": 50} for d in days_back(10, through)})
    assert p["days"][-1]["rhr7"] == 50
