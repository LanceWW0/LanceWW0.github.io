"""Settings for the /health job, read from the `health:` block in _config.yml.

Fails closed: a missing or unrecognised visibility means private, and the
delay can't be configured below 24 hours.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "_config.yml"

METRICS = ("sleep", "hrv", "rhr", "body_battery", "movement", "activities")
MIN_DELAY_HOURS = 24
DEFAULT_SINCE = date(2023, 1, 1)


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class HealthConfig:
    visibility: str = "private"
    delay_hours: int = MIN_DELAY_HOURS
    since: date = DEFAULT_SINCE
    metrics: tuple[str, ...] = METRICS

    @property
    def private(self) -> bool:
        return self.visibility != "public"


def parse_config(raw: Any) -> HealthConfig:
    block = raw.get("health") if isinstance(raw, dict) else None
    if not isinstance(block, dict):
        block = {}

    visibility = "public" if block.get("visibility") == "public" else "private"

    delay = block.get("delay_hours", MIN_DELAY_HOURS)
    if isinstance(delay, bool) or not isinstance(delay, int) or delay < MIN_DELAY_HOURS:
        raise ConfigError(f"health.delay_hours must be a whole number of at least {MIN_DELAY_HOURS}")

    since = block.get("since", DEFAULT_SINCE)
    if isinstance(since, datetime):
        since = since.date()
    elif isinstance(since, str):
        try:
            since = date.fromisoformat(since)
        except ValueError:
            raise ConfigError("health.since must be a date like 2023-01-01") from None
    if not isinstance(since, date):
        raise ConfigError("health.since must be a date like 2023-01-01")

    metrics = block.get("metrics", list(METRICS))
    if not isinstance(metrics, list) or not metrics or any(m not in METRICS for m in metrics):
        raise ConfigError(f"health.metrics must be a non-empty list drawn from: {', '.join(METRICS)}")

    return HealthConfig(visibility, delay, since, tuple(m for m in METRICS if m in metrics))


def load_config(path: Path = CONFIG_PATH) -> HealthConfig:
    with open(path, encoding="utf-8") as handle:
        try:
            raw = yaml.safe_load(handle)
        except yaml.YAMLError:
            raise ConfigError(f"{path.name} is not valid YAML") from None
    return parse_config(raw)
