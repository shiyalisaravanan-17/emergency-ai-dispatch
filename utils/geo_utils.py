import math


def euclidean_distance(loc1: dict, loc2: dict) -> float:
    """
    Calculate simple Euclidean distance between two lat/lng points.
    Good enough for relative proximity in a demo — no real GPS math needed.
    """
    return math.sqrt((loc1["lat"] - loc2["lat"]) ** 2 + (loc1["lng"] - loc2["lng"]) ** 2)


def estimated_arrival_minutes(distance: float) -> int:
    """Convert distance to a rough estimated arrival time in minutes."""
    # 1 degree lat/lng ≈ ~111 km. Assume average speed 60 km/h in city.
    km = distance * 111
    minutes = (km / 60) * 60
    return max(1, round(minutes))
