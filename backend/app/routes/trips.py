from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Trip, Order, Driver, Truck


router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
)


@router.post("/")
def create_trip(
    truck_id: int,
    driver_id: int,
    order_id: int,
    distance: int = 0,
    estimated_time: int = 0,
    fuel_cost: int = 0,
    db: Session = Depends(get_db)
):
    trip = Trip(
        truck_id=truck_id,
        driver_id=driver_id,
        order_id=order_id,
        distance=distance,
        estimated_time=estimated_time,
        fuel_cost=fuel_cost
    )

    db.add(trip)
    db.commit()
    db.refresh(trip)

    return {
        "message": "Trip created successfully",
        "trip": {
            "id": trip.id,
            "truck_id": trip.truck_id,
            "driver_id": trip.driver_id,
            "order_id": trip.order_id,
            "distance": trip.distance,
            "estimated_time": trip.estimated_time,
            "fuel_cost": trip.fuel_cost,
            "status": trip.status
        }
    }


@router.get("/")
def get_trips(
    db: Session = Depends(get_db)
):
    trips = db.query(Trip).all()

    return trips


@router.get("/{trip_id}")
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id)
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return trip

@router.get("/")
def get_all_trips(
    db: Session = Depends(get_db)
):
    trips = (
        db.query(Trip)
        .all()
    )

    return trips

@router.get("/truck/{truck_id}")
def get_trips_by_truck(
    truck_id: int,
    db: Session = Depends(get_db)
):
    truck = (
        db.query(Truck)
        .filter(Truck.id == truck_id)
        .first()
    )

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    trips = (
        db.query(Trip)
        .filter(Trip.truck_id == truck_id)
        .all()
    )

    return trips

@router.get("/driver/{driver_id}")
def get_trips_by_driver(
    driver_id: int,
    db: Session = Depends(get_db)
):
    driver = (
        db.query(Driver)
        .filter(Driver.id == driver_id)
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    trips = (
        db.query(Trip)
        .filter(Trip.driver_id == driver_id)
        .all()
    )

    return trips

@router.get("/order/{order_id}")
def get_trips_by_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    trips = (
        db.query(Trip)
        .filter(Trip.order_id == order_id)
        .all()
    )

    return trips

@router.get("/{trip_id}")
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id)
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return trip

@router.put("/{trip_id}/status")
def update_trip_status(
    trip_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id)
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    allowed_statuses = [
        "planned",
        "in_progress",
        "completed"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid trip status"
        )

    trip.status = status

    driver = (
    db.query(Driver)
    .filter(Driver.id == trip.driver_id)
    .first()
)
    if driver:
        if status == "in_progress":
            driver.status = "busy"

        elif status == "completed":
            driver.status = "available"

    truck = (
        db.query(Truck)
        .filter(Truck.id == trip.truck_id)
        .first()
    )

    if truck:
        if status == "in_progress":
            truck.status = "assigned"

        elif status == "completed":
            truck.status = "available"

    # Find the order associated with this trip
    order = (
        db.query(Order)
        .filter(Order.id == trip.order_id)
        .first()
    )

    # Synchronize order status with trip status
    if order:
        if status == "in_progress":
            order.status = "in_progress"

        elif status == "completed":
            order.status = "completed"

    db.commit()
    db.refresh(trip)

    return {
        "message": "Trip status updated successfully",
        "trip_id": trip.id,
        "order_id": trip.order_id,
        "trip_status": trip.status,
        "order_status": order.status if order else None
    }