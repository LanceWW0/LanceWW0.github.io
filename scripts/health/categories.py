"""Coarse sport groups for published workout breakdowns.

Garmin's own type keys can hint at where you were (open-water swimming,
resort skiing, surfing...). Only these broad groups are ever published, and
anything not listed below becomes "other".
"""
from __future__ import annotations

GROUPS = ("run", "ride", "swim", "strength", "walk", "climb", "paddle", "other")

_GROUP_TYPES: dict[str, tuple[str, ...]] = {
    "run": (
        "running", "trail_running", "treadmill_running", "track_running", "indoor_running",
        "street_running", "ultra_run", "virtual_run", "obstacle_run",
    ),
    "ride": (
        "cycling", "road_biking", "mountain_biking", "gravel_cycling", "indoor_cycling",
        "virtual_ride", "cyclocross", "track_cycling", "recumbent_cycling", "e_bike_fitness",
        "e_bike_mountain", "bmx", "downhill_biking", "hand_cycling",
    ),
    "swim": ("lap_swimming", "open_water_swimming", "swimming"),
    "strength": ("strength_training",),
    "walk": ("walking", "casual_walking", "speed_walking", "hiking", "mountaineering"),
    "climb": ("indoor_climbing", "bouldering", "rock_climbing", "climbing"),
    "paddle": (
        "kayaking", "whitewater_kayaking", "stand_up_paddleboarding", "canoeing", "rowing",
        "paddling",
    ),
}

TYPE_TO_GROUP = {type_key: group for group, keys in _GROUP_TYPES.items() for type_key in keys}


def group_for(type_key: object) -> str:
    """Map a Garmin activity typeKey to a published group."""
    return TYPE_TO_GROUP.get(type_key, "other") if isinstance(type_key, str) else "other"
