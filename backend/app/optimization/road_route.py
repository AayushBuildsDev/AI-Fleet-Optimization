
import math
import requests
from fastapi import HTTPException


def get_road_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
):
    """
    Retrieve road-route geometry from OSRM.
    Coordinates returned are [longitude, latitude].
    """

    # Validate input coordinates.
    if not (
        -90 <= start_lat <= 90
        and -90 <= end_lat <= 90
        and -180 <= start_lon <= 180
        and -180 <= end_lon <= 180
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid start or destination coordinates",
        )

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
    )

    try:
        response = requests.get(
            url,
            params={
                "overview": "full",
                "geometries": "geojson",
                "steps": "false",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Road-routing service is unavailable or returned invalid data",
        ) from exc

    routes = data.get("routes", [])

    if data.get("code") != "Ok" or not routes:
        raise HTTPException(
            status_code=502,
            detail="No road route could be found",
        )

    route = routes[0]
    geometry = route.get("geometry") or {}
    coordinates = geometry.get("coordinates", [])

    if not isinstance(coordinates, list) or not coordinates:
        raise HTTPException(
            status_code=502,
            detail="Road route geometry is unavailable",
        )

    # Validate the GeoJSON coordinate pairs.
    for point in coordinates:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            raise HTTPException(
                status_code=502,
                detail="Invalid road route geometry",
            )

        try:
            lon = float(point[0])
            lat = float(point[1])
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=502,
                detail="Invalid road route coordinates",
            )

        if not (
            math.isfinite(lon)
            and math.isfinite(lat)
            and -180 <= lon <= 180
            and -90 <= lat <= 90
        ):
            raise HTTPException(
                status_code=502,
                detail="Road route contains invalid coordinates",
            )

    try:
        distance_km = float(route["distance"]) / 1000
        duration_minutes = float(route["duration"]) / 60
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Road route distance or duration is missing",
        )

    if (
        not math.isfinite(distance_km)
        or not math.isfinite(duration_minutes)
        or distance_km < 0
        or duration_minutes < 0
    ):
        raise HTTPException(
            status_code=502,
            detail="Road route distance or duration is invalid",
        )

    return {
        "distance_km": distance_km,
        "duration_minutes": duration_minutes,
        "coordinates": coordinates,
    }
