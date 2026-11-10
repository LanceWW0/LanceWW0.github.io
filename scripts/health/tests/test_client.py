from datetime import date

import pytest
import requests

from scripts.health import garmin
from scripts.health.garmin import GarminAuthError, GarminClient, GarminHTTPError
from scripts.health.tests.fakes import FakeResponse, FakeSession, token_response

KEY = "test-api-key-123"
TOKEN = "aaa.bbb.ccc"
DAILIES = garmin.DAILY_SUMMARIES_PATH


def make_client(*responses, **overrides):
    session = FakeSession(list(responses))
    sleeps: list[float] = []
    options = dict(
        session=session,
        min_interval=0,
        on_token=None,
        sleep=sleeps.append,
        clock=lambda: 0.0,
        jitter=lambda: 0.0,
    )
    options.update(overrides)
    return GarminClient(KEY, **options), session, sleeps


def test_exchanges_key_then_sends_bearer_token():
    client, session, _ = make_client(token_response(TOKEN), FakeResponse(200, json_body=[{"x": 1}]))

    assert client.get(DAILIES, params={"startDate": "2026-11-01"}) == [{"x": 1}]

    token_call, data_call = session.calls
    assert token_call.method == "POST"
    assert token_call.url == garmin.BASE_URL + garmin.TOKEN_PATH
    assert token_call.headers["Authorization"] == f"ApiKey {KEY}"
    assert data_call.method == "GET"
    assert data_call.headers["Authorization"] == f"Bearer {TOKEN}"
    assert data_call.params == {"startDate": "2026-11-01"}


def test_reuses_token_across_requests():
    client, session, _ = make_client(token_response(), FakeResponse(200, json_body=[]), FakeResponse(200, json_body=[]))
    client.get(DAILIES)
    client.get(DAILIES)
    assert [c.method for c in session.calls] == ["POST", "GET", "GET"]


@pytest.mark.parametrize(
    "body",
    ['{"access_token": "aaa.bbb.ccc"}', '{"accessToken": "aaa.bbb.ccc"}', '"aaa.bbb.ccc"', "aaa.bbb.ccc\n"],
)
def test_token_accepted_as_text_or_json(body):
    client, session, _ = make_client(FakeResponse(200, text=body), FakeResponse(204))
    client.get(DAILIES)
    assert session.calls[1].headers["Authorization"] == "Bearer aaa.bbb.ccc"


@pytest.mark.parametrize("body", ["", "<html>error</html>", '{"error": "nope"}', "two words"])
def test_unusable_token_body_is_an_auth_error(body):
    client, _, _ = make_client(FakeResponse(200, text=body))
    with pytest.raises(GarminAuthError):
        client.get(DAILIES)


@pytest.mark.parametrize("response", [FakeResponse(204), FakeResponse(200, text=""), FakeResponse(200, text="  ")])
def test_no_content_means_no_data(response):
    client, _, _ = make_client(token_response(), response)
    assert client.get(DAILIES) is None


def test_429_waits_for_retry_after_then_succeeds():
    client, session, sleeps = make_client(
        token_response(),
        FakeResponse(429, headers={"Retry-After": "7"}),
        FakeResponse(200, json_body={"ok": True}),
    )
    assert client.get(DAILIES) == {"ok": True}
    assert sleeps == [7.0]
    assert len(session.calls) == 3


def test_retry_after_is_capped():
    client, _, sleeps = make_client(
        token_response(), FakeResponse(503, headers={"Retry-After": "9999"}), FakeResponse(204)
    )
    client.get(DAILIES)
    assert sleeps == [garmin.MAX_RETRY_AFTER_SECONDS]


def test_server_errors_back_off_exponentially_then_give_up_without_leaking_body():
    failures = [FakeResponse(503, text="SECRET-BODY lat=51.5") for _ in range(5)]
    client, session, sleeps = make_client(token_response(), *failures, max_retries=4)

    with pytest.raises(GarminHTTPError) as excinfo:
        client.get(DAILIES)

    assert sleeps == [1.0, 2.0, 4.0, 8.0]
    assert len(session.calls) == 6
    message = str(excinfo.value)
    assert message == "daily-summaries: HTTP 503"
    assert "SECRET" not in message and "51.5" not in message


def test_network_errors_are_retried_and_wrapped():
    client, _, sleeps = make_client(
        token_response(), requests.ConnectionError("boom http://x?token=abc"), FakeResponse(200, json_body=[])
    )
    assert client.get(DAILIES) == []
    assert sleeps == [1.0]


def test_network_error_after_retries_hides_underlying_exception():
    client, _, _ = make_client(token_response(), *[requests.Timeout("t") for _ in range(3)], max_retries=2)
    with pytest.raises(GarminHTTPError) as excinfo:
        client.get(DAILIES)
    assert str(excinfo.value) == "daily-summaries: no response (network error)"
    assert excinfo.value.__cause__ is None
    assert excinfo.value.__suppress_context__


def test_401_reexchanges_key_once():
    client, session, _ = make_client(
        token_response("old.tok.en"),
        FakeResponse(401),
        token_response("new.tok.en"),
        FakeResponse(200, json_body=[1]),
    )
    assert client.get(DAILIES) == [1]
    assert [c.method for c in session.calls] == ["POST", "GET", "POST", "GET"]
    assert session.calls[3].headers["Authorization"] == "Bearer new.tok.en"


def test_second_401_is_an_auth_error():
    client, _, _ = make_client(token_response(), FakeResponse(401), token_response(), FakeResponse(401))
    with pytest.raises(GarminAuthError) as excinfo:
        client.get(DAILIES)
    assert excinfo.value.status == 401


@pytest.mark.parametrize("status", [401, 403])
def test_rejected_key_message_never_contains_key(status):
    client, _, _ = make_client(FakeResponse(status, text=f"bad key {KEY}"))
    with pytest.raises(GarminAuthError) as excinfo:
        client.get(DAILIES)
    assert KEY not in str(excinfo.value)
    assert "expired, revoked or wrong" in str(excinfo.value)


def test_invalid_json_is_an_error():
    client, _, _ = make_client(token_response(), FakeResponse(200, text="{not json"))
    with pytest.raises(GarminHTTPError, match="not JSON"):
        client.get(DAILIES)


@pytest.mark.parametrize(
    "path",
    [
        "/download-service/files/activity/123",  # FIT/ZIP with GPS tracks
        "/activity-service/activity/123",  # details can include coordinates
        "/wellness-service/wellness/dailyHeartRate",  # intraday, timestamped
        "/userprofile-service/userprofile/settings",
        "/sleep-service/sleep/dailySleepSummariesByDate/../../download-service/files/activity/1",
    ],
)
def test_endpoints_off_the_allowlist_are_refused_before_any_request(path):
    client, session, _ = make_client()
    with pytest.raises(ValueError):
        client.get(path)
    assert session.calls == []


def test_allowlisted_paths_have_labels():
    assert garmin.endpoint_label(garmin.hrv_range_path(date(2026, 1, 1), date(2026, 1, 31))) == "hrv-range"
    assert garmin.endpoint_label(garmin.hrv_day_path(date(2026, 1, 1))) == "hrv-day"
    assert garmin.endpoint_label(garmin.SLEEP_SUMMARIES_PATH) == "sleep-summaries"
    assert garmin.endpoint_label(garmin.SLEEP_DAY_PATH) == "sleep-day"
    assert garmin.endpoint_label(garmin.BODY_BATTERY_PATH) == "body-battery"
    assert garmin.endpoint_label(garmin.ACTIVITIES_PATH) == "activities"


def test_requests_are_throttled():
    now = [100.0]
    client, _, sleeps = make_client(
        token_response(), FakeResponse(204), FakeResponse(204), min_interval=1.0, clock=lambda: now[0]
    )
    client.get(DAILIES)  # token + first GET happen at the same instant
    now[0] += 0.25
    client.get(DAILIES)
    assert sleeps == [1.0, 0.75]


def test_on_token_hook_receives_each_new_token():
    seen = []
    client, _, _ = make_client(token_response("t.o.k"), FakeResponse(204), on_token=seen.append)
    client.get(DAILIES)
    assert seen == ["t.o.k"]


def test_mask_prints_only_inside_github_actions(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    garmin.mask_in_github_actions("s3cret")
    assert capsys.readouterr().out == ""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    garmin.mask_in_github_actions("s3cret")
    assert capsys.readouterr().out == "::add-mask::s3cret\n"


def test_repr_hides_secrets():
    client, _, _ = make_client(token_response(TOKEN), FakeResponse(204))
    client.get(DAILIES)
    assert KEY not in repr(client) and TOKEN not in repr(client)


def test_iter_activities_pages_until_a_short_page():
    full = [{"id": i} for i in range(3)]
    client, session, _ = make_client(
        token_response(), FakeResponse(200, json_body=full), FakeResponse(200, json_body=[{"id": 3}])
    )
    items = list(client.iter_activities(date(2026, 1, 1), date(2026, 1, 31), page_size=3))
    assert [a["id"] for a in items] == [0, 1, 2, 3]
    assert [c.params["start"] for c in session.calls[1:]] == [0, 3]
    assert session.calls[1].params["startDate"] == "2026-01-01"
    assert session.calls[1].params["endDate"] == "2026-01-31"


def test_iter_activities_stops_on_empty_response():
    client, _, _ = make_client(token_response(), FakeResponse(204))
    assert list(client.iter_activities(date(2026, 1, 1), date(2026, 1, 2))) == []


def test_iter_activities_rejects_unexpected_shape():
    client, _, _ = make_client(token_response(), FakeResponse(200, json_body={"activities": []}))
    with pytest.raises(GarminHTTPError, match="unexpected response shape"):
        list(client.iter_activities(date(2026, 1, 1), date(2026, 1, 2)))


def test_empty_key_is_refused():
    with pytest.raises(garmin.GarminConfigError):
        GarminClient("")
