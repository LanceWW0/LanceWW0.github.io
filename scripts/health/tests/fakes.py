"""Offline stand-ins for requests.Session so tests never touch the network."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


class FakeResponse:
    def __init__(self, status: int = 200, json_body: Any = None, text: str | None = None, headers=None):
        if json_body is not None:
            text = json.dumps(json_body)
        self.status_code = status
        self.text = text or ""
        self.content = self.text.encode()
        self.headers = headers or {}

    def json(self):
        return json.loads(self.text)


@dataclass
class Call:
    method: str
    url: str
    headers: dict
    params: dict


@dataclass
class FakeSession:
    """Replays queued responses (or raises queued exceptions) in order."""

    responses: list = field(default_factory=list)
    calls: list[Call] = field(default_factory=list)

    def request(self, method, url, headers=None, params=None, timeout=None):
        self.calls.append(Call(method, url, dict(headers or {}), dict(params or {})))
        if not self.responses:
            raise AssertionError(f"unexpected request: {method} {url}")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def token_response(token: str = "header.payload.signature") -> FakeResponse:
    return FakeResponse(200, text=token)
