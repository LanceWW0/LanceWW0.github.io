"""Synthetic Garmin responses shaped like the real ones from the probe report.

They are deliberately full of things that must never reach the payload:
place names, coordinates, times of day, bedtime "minutes", names and IDs.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse

from scripts.health import garmin
from scripts.health.tests.fakes import FakeResponse

# Distinctive values that must never appear in any output or log line.
POISON = [
    "London", "Hyde Park", "Laurence Wayne", "lance_runs", "51.50735", "-0.12775",
    "07:12", "23:41", "4321.98", "987654321", "abc-123-uuid", "1379", "You slept",
]


def _epoch_ms(day: date, hour: int, minute: int) -> int:
    return int(datetime(day.year, day.month, day.day, hour, minute, tzinfo=timezone.utc).timestamp() * 1000)


def raw_sleep(day: date, seconds: int = 27_000) -> dict:
    return {
        "calendarDate": day.isoformat(),
        "sleepTimeSeconds": seconds,
        "sleepStartTimestampLocal": _epoch_ms(day - timedelta(days=1), 23, 41),
        "sleepEndTimestampLocal": _epoch_ms(day, 7, 12),
        "sleepEndTimestampGMT": _epoch_ms(day, 7, 12),
        "sleepScores": {"overall": {"value": 81, "qualifierKey": "GOOD"}, "deepPercentage": {"value": 18}},
        "deepSleepSeconds": 5_400,
        "lightSleepSeconds": 15_000,
        "remSleepSeconds": 6_600,
        "awakeSleepSeconds": 1_200,
        "sleepNeed": {"recommendedBedtimeStartMins": 1379, "timestampGmt": f"{day}T07:12:00.0"},
        "sleepAlignment": {"lastSleepMidpointMins": 1379, "userId": 987654321},
        "sleepScorePersonalizedInsight": "You slept well near Hyde Park",
        "userProfilePK": 987654321,
        "id": _epoch_ms(day, 7, 12),
    }


def raw_hrv(day: date) -> dict:
    return {
        "calendarDate": day.isoformat(),
        "lastNightAvg": 58 + day.day % 5,
        "weeklyAvg": 60,
        "lastNight5MinHigh": 91,
        "baseline": {"balancedLow": 50, "balancedUpper": 70, "lowUpper": 45, "markerValue": 0.4},
        "createTimeStamp": f"{day}T07:12:33.0",
        "status": "BALANCED",
        "feedbackPhrase": "HRV_BALANCED_1",
    }


def raw_daily(day: date) -> dict:
    return {
        "calendarDate": day.isoformat(),
        "uuid": "abc-123-uuid",
        "userProfilePk": 987654321,
        "heartRate": {"restingValue": 47 + day.day % 3, "maxValue": 171, "minValue": 44},
        "bodyBattery": {
            "maxValue": 80 + day.day % 10,
            "minValue": 20,
            "latestValue": 33,
            "activityEvents": [{"eventStartTimeLocal": f"{day}T07:12:00.0", "deviceId": 987654321}],
        },
        "pulseOx": {"avgAltitudeInMeters": 4321.98, "latestTimestampLocal": f"{day}T23:41:00.0"},
        "wellnessChronology": {"startTimestampLocal": f"{day}T00:00:00.0", "endTimestampLocal": f"{day}T23:41:00.0"},
    }


def raw_activity(day: date, index: int, type_key: str = "running", km: float = 8.0) -> dict:
    return {
        "activityId": 123_456_789_000 + index,
        "activityUUID": "abc-123-uuid",
        "activityName": "London Running",
        "locationName": "London",
        "description": "Loop of Hyde Park",
        "ownerFullName": "Laurence Wayne",
        "ownerDisplayName": "lance_runs",
        "ownerId": 987654321,
        "startLatitude": 51.5073509,
        "startLongitude": -0.1277583,
        "endLatitude": 51.5073509,
        "endLongitude": -0.1277583,
        "avgElevation": 4321.98,
        "startTimeLocal": f"{day} 07:12:33",
        "startTimeGMT": f"{day} 07:12:33",
        "beginTimestamp": _epoch_ms(day, 7, 12),
        "activityType": {"typeKey": type_key, "typeId": 1, "parentTypeId": 17},
        "distance": km * 1000,
        "duration": km * 330,
        "movingDuration": km * 320,
        "elapsedDuration": km * 340,
        "activityTrainingLoad": 40 + index % 7 * 15,
    }


class FakeGarmin:
    """A session for GarminClient that answers like the Personal API.

    `first` is the first day with data. `fail` holds endpoint labels that
    return HTTP 503. `sleep_every` keeps only every Nth night (to simulate
    a sudden data drop).
    """

    def __init__(self, first: date, *, fail=(), token_status: int = 200, sleep_every: int = 1,
                 activity_types=("running", "walking", "hiking", "cycling", "strength_training")):
        self.first = first
        self.fail = set(fail)
        self.token_status = token_status
        self.sleep_every = sleep_every
        self.activity_types = activity_types
        self.calls: list[str] = []

    def request(self, method, url, headers=None, params=None, timeout=None):
        path = urlparse(url).path
        params = dict(params or {})
        if method == "POST":
            self.calls.append("token")
            return FakeResponse(self.token_status, text="aaa.bbb.ccc" if self.token_status == 200 else "denied")
        label = garmin.endpoint_label(path)
        self.calls.append(label)
        if label in self.fail:
            return FakeResponse(503, text="Service unavailable for London")

        if label == "hrv-range":
            start, end = (date.fromisoformat(p) for p in path.rsplit("/", 2)[-2:])
        else:
            start, end = date.fromisoformat(params["startDate"]), date.fromisoformat(params["endDate"])
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        days = [d for d in days if d >= self.first]

        if label == "sleep-summaries":
            body = [raw_sleep(d) for d in days if d.toordinal() % self.sleep_every == 0]
        elif label == "hrv-range":
            body = {"userProfilePk": 987654321, "hrvSummaries": [raw_hrv(d) for d in days]} if days else None
        elif label == "daily-summaries":
            body = {"data": [raw_daily(d) for d in days]}
        elif label == "activities":
            everything = [
                raw_activity(d, i, self.activity_types[i % len(self.activity_types)])
                for i, d in enumerate(d for d in days if d.toordinal() % 2 == 0)
            ]
            offset, limit = int(params["start"]), int(params["limit"])
            body = everything[offset:offset + limit]
        else:
            raise AssertionError(f"unexpected endpoint {label}")
        return FakeResponse(204) if body is None else FakeResponse(200, json_body=body)
