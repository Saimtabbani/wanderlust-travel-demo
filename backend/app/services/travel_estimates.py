"""Transparent, non-routing travel estimates based on great-circle geometry."""
import math
from typing import Optional

EARTH_RADIUS_KM = 6371.0088
CRUISE_SPEED_KMH = 800.0
AIRPORT_AND_CONNECTION_HOURS = 2.0


def haversine_km(origin_lat: float, origin_lon: float, destination_lat: float, destination_lon: float) -> int:
    """Return rounded great-circle distance in kilometres."""
    lat1, lon1, lat2, lon2 = map(math.radians, (origin_lat, origin_lon, destination_lat, destination_lon))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return round(EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a)))


def flight_planning_estimate(
    origin_lat: float, origin_lon: float, destination_lat: Optional[float], destination_lon: Optional[float]
) -> Optional[dict]:
    """Estimate elapsed air travel time; never represents a live flight itinerary."""
    if destination_lat is None or destination_lon is None:
        return None
    distance = haversine_km(origin_lat, origin_lon, destination_lat, destination_lon)
    hours = round(distance / CRUISE_SPEED_KMH + AIRPORT_AND_CONNECTION_HOURS, 1)
    return {
        "distance_km": distance,
        "estimated_flight_hours": hours,
        "assumptions": "Great-circle distance; 800 km/h cruise plus 2 hours for airport and connection time. Not a live route, fare, or schedule.",
    }
