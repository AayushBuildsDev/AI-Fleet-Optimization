from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Trip


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