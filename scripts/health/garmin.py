"""Minimal read-only client for the Garmin Connect Personal API.

Rules this module enforces (see scripts/health/README.md):

- The API key is exchanged for a 24-hour bearer token on every run. Garmin
  has no refresh tokens, so "refreshing" is just exchanging the key again.
  Neither the key nor the token is ever written to disk or put in an error.
- Only allowlisted read endpoints can be called. Activity downloads (FIT/ZIP
  files, which contain GPS tracks) and activity details are deliberately
  not on the list.
- Errors carry an endpoint label and HTTP status only, never response
  bodies: GitHub Actions logs on a public repo are public.
"""
from __future__ import annotations

import json
import logging
import os
import random
import re
import stat
import time
from collections.abc import Callable, Iterator, Mapping
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
API_KEY_ENV = "GARMIN_PERSONAL_API_KEY"
DEFAULT_KEY_FILE = Path("~/.config/garmin/connect-personal-api-key")

_DATE = r"\d{4}-\d{2}-\d{2}"

# label -> path pattern. Anything not matched here is refused before a
# request is made.
ENDPOINTS: dict[str, re.Pattern[str]] = {
    "sleep-summaries": re.compile(r"/sleep-service/sleep/dailySleepSummariesByDate"),
    "sleep-day": re.compile(r"/sleep-service/sleep/dailySleep"),
    "hrv-range": re.compile(rf"/hrv-service/hrv/daily/{_DATE}/{_DATE}"),
    "hrv-day": re.compile(rf"/hrv-service/hrv/{_DATE}"),
    "daily-summaries": re.compile(r"/usersummary-service/v2/dailysummaries"),
    "body-battery": re.compile(r"/wellness-service/wellness/bodyBattery/reports/daily"),
    "activities": re.compile(r"/activitylist-service/activities/search/activities"),
}

SLEEP_SUMMARIES_PATH = "/sleep-service/sleep/dailySleepSummariesByDate"
SLEEP_DAY_PATH = "/sleep-service/sleep/dailySleep"
DAILY_SUMMARIES_PATH = "/usersummary-service/v2/dailysummaries"
BODY_BATTERY_PATH = "/wellness-service/wellness/bodyBattery/reports/daily"
ACTIVITIES_PATH = "/activitylist-service/activities/search/activities"


def hrv_range_path(start: date, end: date) -> str:
    return f"/hrv-service/hrv/daily/{start.isoformat()}/{end.isoformat()}"


def hrv_day_path(day: date) -> str:
    return f"/hrv-service/hrv/{day.isoformat()}"


RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_RETRY_AFTER_SECONDS = 120.0
MAX_ACTIVITY_PAGES = 1000


class GarminError(Exception):
    """Base class. Messages never contain secrets or response bodies."""


class GarminConfigError(GarminError):
    """Missing or unusable local configuration (e.g. no API key)."""


class GarminHTTPError(GarminError):
    def __init__(self, label: str, status: int | None, detail: str | None = None):
        self.label = label
        self.status = status
        self.detail = detail
        where = f"HTTP {status}" if status is not None else "no response"
        super().__init__(f"{label}: {where}" + (f" ({detail})" if detail else ""))


class GarminAuthError(GarminHTTPError):
    """The key or token was rejected (expired, revoked or wrong)."""


def endpoint_label(path: str) -> str:
    """Return the allowlist label for `path`, or raise ValueError."""
    for label, pattern in ENDPOINTS.items():
        if pattern.fullmatch(path):
            return label
    raise ValueError("endpoint is not on the allowlist")


def load_api_key(env: Mapping[str, str] | None = None, key_file: Path | None = None) -> str:
    """Find the Personal API key: env var first, then the local key file.

    Mirrors Garmin's own client so the same key file works for both.
    """
    env = os.environ if env is None else env
    value = env.get(API_KEY_ENV, "").strip()
    if value:
        return value

    path = (key_file or DEFAULT_KEY_FILE).expanduser()
    if not path.is_file():
        raise GarminConfigError(f"no API key: set {API_KEY_ENV} or create {path} (chmod 600)")
    if os.name == "posix" and path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        log.warning("%s is readable by other users; run: chmod 600 %s", path, path)
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise GarminConfigError(f"{path} is empty")
    return value


def mask_in_github_actions(secret: str) -> None:
    """Ask the Actions runner to redact `secret` from all later log output."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::add-mask::{secret}", flush=True)


class GarminClient:
    """Read-only client. Every request goes through the allowlist and throttle."""

    def __init__(
        self,
        api_key: str,
        *,
        session: Any = None,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        min_interval: float = 1.0,
        max_retries: int = 4,
        on_token: Callable[[str], None] | None = mask_in_github_actions,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        jitter: Callable[[], float] = random.random,
    ):
        if not api_key:
            raise GarminConfigError("empty API key")
        self._api_key = api_key
        self._session = session if session is not None else requests.Session()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._min_interval = min_interval
        self._max_retries = max_retries
        self._on_token = on_token
        self._sleep = sleep
        self._clock = clock
        self._jitter = jitter
        self._token: str | None = None
        self._last_request_at: float | None = None
        self.request_count = 0

    def __repr__(self) -> str:  # never show the key or token
        return f"GarminClient(base_url={self._base_url!r}, requests={self.request_count})"

    # -- public API -------------------------------------------------------

    def authenticate(self) -> None:
        """Exchange the API key for a fresh bearer token."""
        response = self._request_with_retries(
            "POST", TOKEN_PATH, "token", headers={"Authorization": f"ApiKey {self._api_key}"}
        )
        if response.status_code in (401, 403):
            raise GarminAuthError("token", response.status_code, "key rejected: expired, revoked or wrong")
        if not 200 <= response.status_code < 300:
            raise GarminHTTPError("token", response.status_code)
        token = _extract_token(response)
        if not token:
            raise GarminAuthError("token", response.status_code, "no token in response")
        self._token = token
        if self._on_token:
            self._on_token(token)

    @property
    def token(self) -> str | None:
        return self._token

    def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        """GET an allowlisted endpoint. Returns parsed JSON, or None for no data."""
        label = endpoint_label(path)
        if self._token is None:
            self.authenticate()
        reauthenticated = False
        while True:
            response = self._request_with_retries(
                "GET",
                path,
                label,
                params=params,
                headers={"Authorization": f"Bearer {self._token}", "Accept": "application/json"},
            )
            if response.status_code == 401 and not reauthenticated:
                reauthenticated = True
                self.authenticate()
                continue
            return _parse(label, response)

    def iter_activities(self, start: date, end: date, page_size: int = 45) -> Iterator[dict]:
        """Yield activity summaries between two dates (inclusive), page by page."""
        offset = 0
        for _ in range(MAX_ACTIVITY_PAGES):
            page = self.get(
                ACTIVITIES_PATH,
                params={
                    "start": offset,
                    "limit": page_size,
                    "startDate": start.isoformat(),
                    "endDate": end.isoformat(),
                },
            )
            if not page:
                return
            if not isinstance(page, list):
                raise GarminHTTPError("activities", 200, "unexpected response shape")
            yield from page
            if len(page) < page_size:
                return
            offset += page_size
        raise GarminHTTPError("activities", None, "too many pages")

    # -- internals --------------------------------------------------------

    def _request_with_retries(self, method, path, label, *, headers, params=None):
        attempt = 0
        while True:
            try:
                response = self._send(method, path, headers=headers, params=params)
            except (requests.ConnectionError, requests.Timeout):
                if attempt >= self._max_retries:
                    raise GarminHTTPError(label, None, "network error") from None
                self._sleep(self._backoff(attempt, None))
                attempt += 1
                continue
            if response.status_code in RETRY_STATUSES and attempt < self._max_retries:
                self._sleep(self._backoff(attempt, response))
                attempt += 1
                continue
            return response

    def _send(self, method, path, *, headers, params):
        if self._last_request_at is not None and self._min_interval > 0:
            wait = self._min_interval - (self._clock() - self._last_request_at)
            if wait > 0:
                self._sleep(wait)
        self._last_request_at = self._clock()
        self.request_count += 1
        return self._session.request(
            method, self._base_url + path, headers=headers, params=params, timeout=self._timeout
        )

    def _backoff(self, attempt: int, response) -> float:
        if response is not None:
            retry_after = _retry_after_seconds(response.headers.get("Retry-After"))
            if retry_after is not None:
                return min(retry_after, MAX_RETRY_AFTER_SECONDS)
        return min(60.0, 2.0 ** attempt) + self._jitter()


def _parse(label: str, response) -> Any:
    status = response.status_code
    if status == 204:
        return None
    if 200 <= status < 300:
        if not (response.content or b"").strip():
            return None
        try:
            return response.json()
        except ValueError:
            raise GarminHTTPError(label, status, "response was not JSON") from None
    if status in (401, 403):
        raise GarminAuthError(label, status)
    raise GarminHTTPError(label, status)


def _extract_token(response) -> str | None:
    """The token endpoint is documented to return the JWT as raw text; accept JSON too."""
    text = (response.text or "").strip()
    if not text:
        return None
    if text[0] in "{\"":
        try:
            body = json.loads(text)
        except ValueError:
            return None
        if isinstance(body, str):
            text = body.strip()
        elif isinstance(body, dict):
            for key in ("access_token", "accessToken", "token"):
                if isinstance(body.get(key), str):
                    text = body[key].strip()
                    break
            else:
                return None
        else:
            return None
    if not text or any(ch.isspace() for ch in text) or "<" in text:
        return None
    return text


def _retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        return None
    return max(0.0, (when - datetime.now(when.tzinfo)).total_seconds())
