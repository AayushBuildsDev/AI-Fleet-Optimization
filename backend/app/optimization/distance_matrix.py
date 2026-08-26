from math import radians, sin, cos, sqrt, atan2
from app.optimization.depot import DEPOT_LATITUDE, DEPOT_LONGITUDE


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate approximate straight-line distance
    between two geographic coordinates using
    the Haversine formula.

    Returns distance in kilometers.
    """

    earth_radius = 6371.0

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return round(earth_radius * c, 2)


def build_distance_matrix(orders):
    """
    Build a geographic distance matrix.

    Location 0 = pickup/depot of the first order.
    Each following location = delivery location of an order.
    """

    if not orders:
        return [[0]]

    # Use the first order's pickup location as depot.
    depot_lat = DEPOT_LATITUDE
    depot_lon = DEPOT_LONGITUDE

    # Locations:
    # 0 = depot
    # 1...n = order delivery locations

    locations = [
        (depot_lat, depot_lon)
    ]

    for order in orders:
        locations.append(
            (
                order.delivery_latitude,
                order.delivery_longitude
            )
        )

    size = len(locations)

    matrix = [
        [0 for _ in range(size)]
        for _ in range(size)
    ]

    for i in range(size):
        for j in range(size):

            if i == j:
                matrix[i][j] = 0
                continue

            lat1, lon1 = locations[i]
            lat2, lon2 = locations[j]

            # If coordinates are missing
            if (
                lat1 is None
                or lon1 is None
                or lat2 is None
                or lon2 is None
            ):
                matrix[i][j] = 0
                continue

            matrix[i][j] = int(
                calculate_distance(
                    lat1,
                    lon1,
                    lat2,
                    lon2
                )
            )

    return matrix