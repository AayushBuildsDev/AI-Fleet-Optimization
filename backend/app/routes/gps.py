from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import GPSTracking, Trip, Order
from math import radians, sin, cos, sqrt, atan2


router = APIRouter(
    prefix="/gps",
    tags=["GPS Tracking"]
)


@router.post("/")
def create_gps_record(
    truck_id: int,
    latitude: str,
    longitude: str,
    speed: int = 0,
    timestamp: str = "",
    db: Session = Depends(get_db)
):
    gps_record = GPSTracking(
        truck_id=truck_id,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        timestamp=timestamp
    )

    db.add(gps_record)
    db.commit()
    db.refresh(gps_record)

    return {
        "message": "GPS record created successfully",
        "gps": {
            "id": gps_record.id,
            "truck_id": gps_record.truck_id,
            "latitude": gps_record.latitude,
            "longitude": gps_record.longitude,
            "speed": gps_record.speed,
            "timestamp": gps_record.timestamp
        }
    }


@router.get("/")
def get_gps_records(
    db: Session = Depends(get_db)
):
    records = db.query(GPSTracking).all()

    return records


@router.get("/{truck_id}")
def get_truck_location(
    truck_id: int,
    db: Session = Depends(get_db)
):
    record = (
        db.query(GPSTracking)
        .filter(GPSTracking.truck_id == truck_id)
        .order_by(GPSTracking.id.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="GPS record not found for this truck"
        )

    return {
        "truck_id": record.truck_id,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "speed": record.speed,
        "timestamp": record.timestamp
    }

@router.get("/{truck_id}/active-trip")
def get_truck_active_trip(
    truck_id: int,
    db: Session = Depends(get_db)
):
    gps_record = (
        db.query(GPSTracking)
        .filter(GPSTracking.truck_id == truck_id)
        .order_by(GPSTracking.id.desc())
        .first()
    )

    if not gps_record:
        raise HTTPException(
            status_code=404,
            detail="GPS record not found for this truck"
        )

    trip = (
        db.query(Trip)
        .filter(
            Trip.truck_id == truck_id,
            Trip.status == "in_progress"
        )
        .order_by(Trip.id.desc())
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="No active trip found for this truck"
        )

    return {
        "truck_id": truck_id,
        "trip_id": trip.id,
        "order_id": trip.order_id,
        "latitude": gps_record.latitude,
        "longitude": gps_record.longitude,
        "speed": gps_record.speed,
        "timestamp": gps_record.timestamp,
        "trip_status": trip.status
    }

@router.get("/{truck_id}/eta")
def get_truck_eta(
    truck_id: int,
    db: Session = Depends(get_db)
):
    # Get latest GPS location
    gps_record = (
        db.query(GPSTracking)
        .filter(GPSTracking.truck_id == truck_id)
        .order_by(GPSTracking.id.desc())
        .first()
    )

    if not gps_record:
        raise HTTPException(
            status_code=404,
            detail="GPS record not found for this truck"
        )

    # Get active trip
    trip = (
        db.query(Trip)
        .filter(
            Trip.truck_id == truck_id,
            Trip.status == "in_progress"
        )
        .order_by(Trip.id.desc())
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="No active trip found for this truck"
        )

    # Get order
    order = (
        db.query(Order)
        .filter(Order.id == trip.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found for this trip"
        )

    if (
        order.delivery_latitude is None
        or order.delivery_longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Delivery coordinates are missing"
        )

    # Convert coordinates
    lat1 = radians(float(gps_record.latitude))
    lon1 = radians(float(gps_record.longitude))

    lat2 = radians(float(order.delivery_latitude))
    lon2 = radians(float(order.delivery_longitude))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
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

    earth_radius = 6371.0

    remaining_distance = earth_radius * c

    # Use current GPS speed
    speed = gps_record.speed

    if speed <= 0:
        speed = 50

    estimated_hours = remaining_distance / speed

    estimated_minutes = estimated_hours * 60

    return {
        "truck_id": truck_id,
        "trip_id": trip.id,
        "order_id": order.id,
        "current_speed_kmh": speed,
        "remaining_distance_km": round(
            remaining_distance,
            2
        ),
        "estimated_time_minutes": round(
            estimated_minutes
        ),
        "estimated_time_hours": round(
            estimated_hours,
            2
        )
    }

@router.get("/{truck_id}/route-deviation")
def check_route_deviation(
    truck_id: int,
    db: Session = Depends(get_db)
):
    gps_record = (
        db.query(GPSTracking)
        .filter(GPSTracking.truck_id == truck_id)
        .order_by(GPSTracking.id.desc())
        .first()
    )

    if not gps_record:
        raise HTTPException(
            status_code=404,
            detail="GPS record not found for this truck"
        )

    trip = (
        db.query(Trip)
        .filter(
            Trip.truck_id == truck_id,
            Trip.status == "in_progress"
        )
        .order_by(Trip.id.desc())
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="No active trip found for this truck"
        )

    order = (
        db.query(Order)
        .filter(Order.id == trip.order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if (
        order.delivery_latitude is None
        or order.delivery_longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Delivery coordinates are missing"
        )

    depot_lat = 19.0760
    depot_lon = 72.8777

    current_lat = float(gps_record.latitude)
    current_lon = float(gps_record.longitude)

    delivery_lat = float(order.delivery_latitude)
    delivery_lon = float(order.delivery_longitude)

    # Distance from current GPS position to the delivery location
    lat1 = radians(current_lat)
    lon1 = radians(current_lon)
    lat2 = radians(delivery_lat)
    lon2 = radians(delivery_lon)

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

    earth_radius = 6371.0

    remaining_distance = earth_radius * c

    # Simple V1 deviation rule
    deviation_limit_km = 50

    # Compare current position with the direct
    # depot-to-delivery distance.
    depot_lat_r = radians(depot_lat)
    depot_lon_r = radians(depot_lon)

    dlat_depot = lat2 - depot_lat_r
    dlon_depot = lon2 - depot_lon_r

    a_depot = (
        sin(dlat_depot / 2) ** 2
        + cos(depot_lat_r)
        * cos(lat2)
        * sin(dlon_depot / 2) ** 2
    )

    c_depot = 2 * atan2(
        sqrt(a_depot),
        sqrt(1 - a_depot)
    )

    route_distance = earth_radius * c_depot

    current_from_depot_lat = radians(current_lat)
    current_from_depot_lon = radians(current_lon)

    dlat_current = current_from_depot_lat - depot_lat_r
    dlon_current = current_from_depot_lon - depot_lon_r

    a_current = (
        sin(dlat_current / 2) ** 2
        + cos(depot_lat_r)
        * cos(current_from_depot_lat)
        * sin(dlon_current / 2) ** 2
    )

    c_current = 2 * atan2(
        sqrt(a_current),
        sqrt(1 - a_current)
    )

    distance_from_depot = earth_radius * c_current

    deviation_distance = abs(
        route_distance
        - (
            distance_from_depot
            + remaining_distance
        )
    )

    is_deviated = deviation_distance > deviation_limit_km

    return {
        "truck_id": truck_id,
        "trip_id": trip.id,
        "order_id": order.id,
        "deviation_distance_km": round(
            deviation_distance,
            2
        ),
        "deviation_limit_km": deviation_limit_km,
        "status": (
            "deviated"
            if is_deviated
            else "on_route"
        )
    }