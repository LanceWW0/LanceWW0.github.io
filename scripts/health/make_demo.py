"""Synthetic demo data for building and testing the /health page.

    .venv/bin/python -m scripts.health.make_demo

Writes assets/health/demo.json (plain) and demo.enc.json (encrypted with the
passphrase "demo"). Every number is invented from a fixed seed, so reruns give
the same plain file. The data goes through the same aggregation and schema
check as the real thing.
"""
from __future__ import annotations

import math
import random
import sys
from datetime import date, timedelta

from . import crypto
from .aggregate import Inputs, build_payload
from .config import METRICS, REPO_ROOT
from .normalise import Activity
from .schema import canonical, validate

DEMO_THROUGH = date(2026, 11, 8)
DEMO_START = date(2023, 3, 6)
DEMO_PASSPHRASE = "demo"
OUT_DIR = REPO_ROOT / "assets" / "health"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def synthetic_inputs(through: date = DEMO_THROUGH, start: date = DEMO_START, seed: int = 7) -> Inputs:
    rng = random.Random(seed)
    sleep, hrv, rhr, bb, movement = {}, {}, {}, {}, {}
    acts: list[Activity] = []

    def add(day: date, group: str, km: float, pace_s: float, load: float, minutes: float | None = None) -> float:
        """Invent one workout; returns its moving minutes."""
        moving = km * pace_s if km else (minutes or 45) * 60
        # Time in HR zones 1-5: runs sit mostly in zones 2-3, walks in 1-2.
        weights = {"run": (0.08, 0.42, 0.32, 0.15, 0.03), "walk": (0.55, 0.38, 0.07, 0, 0),
                   "ride": (0.15, 0.45, 0.28, 0.1, 0.02), "climb": (0.3, 0.4, 0.2, 0.1, 0),
                   "strength": (0.4, 0.35, 0.2, 0.05, 0)}[group]
        zones = tuple(round(moving * w * rng.uniform(0.85, 1.15)) for w in weights)
        bests: tuple = ()
        if group == "run":
            splits = [("1k", 1, 0.9), ("mile", 1.609, 0.93)]
            if km >= 5:
                splits.append(("5k", 5, 0.97))
            if km >= 10:
                splits.append(("10k", 10, 0.99))
            bests = tuple((key, round(pace_s * dist * factor * rng.uniform(0.97, 1.03))) for key, dist, factor in splits)
        acts.append(Activity(day, group, round(km, 2), moving * rng.uniform(1.01, 1.08), moving, round(load, 1),
                             zones=zones, bests=bests))
        return moving / 60

    day = start
    while day <= through:
        t = (day - start).days
        fitness = 1 - math.exp(-t / 420)          # slowly getting fitter
        season = math.sin(2 * math.pi * (t + 40) / 365)

        score = 70
        if rng.random() > 0.04:                   # ~4% of nights not worn
            asleep = _clamp(rng.gauss(448 + 12 * season, 36), 300, 560)
            awake, deep, rem = rng.uniform(0.03, 0.08), rng.uniform(0.15, 0.22), rng.uniform(0.19, 0.26)
            in_bed = asleep / (1 - awake)
            score = round(_clamp(58 + (asleep - 360) / 4.5 + rng.gauss(0, 6), 38, 97))
            sleep[day] = {
                "sleep_min": round(asleep), "sleep_score": score,
                "deep_min": round(in_bed * deep), "rem_min": round(in_bed * rem),
                "light_min": round(in_bed * (1 - awake - deep - rem)), "awake_min": round(in_bed * awake),
            }
        base = 47 + 11 * fitness
        hrv[day] = {"hrv": round(rng.gauss(base + 3 * season, 5.5)), "hrv_lo": round(base - 7), "hrv_hi": round(base + 10)}
        rhr[day] = {"rhr": round(rng.gauss(55 - 6 * fitness - season, 1.6))}
        bb[day] = {"bb": round(_clamp(rng.gauss(76 + (score - 70) / 2.5, 7), 25, 100))}

        weekday = day.weekday()
        easy_pace = 345 - 30 * fitness
        run_min = walk_min = other_min = 0.0
        walk_km = run_km = 0.0
        if weekday in (1, 3) and rng.random() < 0.85:
            km = rng.uniform(6, 9.5)
            run_km += km
            run_min += add(day, "run", km, easy_pace + rng.gauss(0, 10), km * rng.uniform(9, 13))
        if weekday == 6 and rng.random() < 0.8:
            km = rng.uniform(12, 19 + 4 * fitness)
            run_km += km
            run_min += add(day, "run", km, easy_pace + 15 + rng.gauss(0, 10), km * rng.uniform(10, 14))
        if weekday == 5 and rng.random() < 0.45 + 0.2 * season:
            km = rng.uniform(8, 18)
            walk_km += km
            walk_min += add(day, "walk", km, rng.uniform(780, 1000), km * rng.uniform(5, 8))
        if weekday in (0, 2, 4) and rng.random() < 0.3:
            km = rng.uniform(3, 5.5)
            walk_km += km
            walk_min += add(day, "walk", km, rng.uniform(660, 760), km * 3)
        if weekday == 2 and rng.random() < 0.2:
            km = rng.uniform(25, 50)
            other_min += add(day, "ride", km, rng.uniform(130, 170), km * 2.2)
        if weekday == 4 and rng.random() < 0.25:
            other_min += add(day, "climb", 0, 0, rng.uniform(30, 60), minutes=rng.uniform(70, 110))
        if weekday == 0 and rng.random() < 0.2:
            other_min += add(day, "strength", 0, 0, rng.uniform(20, 40), minutes=rng.uniform(35, 50))

        if rng.random() > 0.03:                   # ~3% of days not worn
            steps = rng.gauss(7200 + 900 * season, 1800) + run_km * 1250 + walk_km * 1350
            movement[day] = {
                "steps": round(_clamp(steps, 900, 40000)),
                "floors": round(_clamp(rng.gauss(9 + walk_km * 1.5, 4), 0, 80)),
                "im_mod": round(rng.uniform(0, 12) + walk_min * 0.7 + other_min * 0.5),
                "im_vig": round(run_min * 0.75 + other_min * 0.2),
                "im_goal": 150,
            }
        day += timedelta(days=1)

    return Inputs(sleep=sleep, hrv=hrv, rhr=rhr, body_battery=bb, movement=movement, activities=acts)


def demo_payload() -> dict:
    payload = build_payload(synthetic_inputs(), DEMO_THROUGH, {m: DEMO_THROUGH.isoformat() for m in METRICS})
    validate(payload, max_through=DEMO_THROUGH)
    return payload


def main() -> int:
    body = canonical(demo_payload())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "demo.json").write_text(body + "\n", encoding="utf-8")
    envelope = crypto.encrypt(body.encode("utf-8"), DEMO_PASSPHRASE)
    (OUT_DIR / "demo.enc.json").write_text(canonical(envelope) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DIR / 'demo.json'} ({len(body)} bytes) and demo.enc.json (passphrase: {DEMO_PASSPHRASE})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
