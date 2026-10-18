from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.optimization.multi_day_scheduler import schedule_multi_day_trip
from app.database.connection import get_db
from app.database.models import Trip, Order, Driver, Truck

router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
)

#     # 1. Check that the truck exists
#     truck = db.query(Truck).filter(
#         Truck.id == truck_id
#     ).first()

#     if not truck:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Truck ID {truck_id} not found"
#         )

#     # 2. Check that the driver exists
#     driver = db.query(Driver).filter(
#         Driver.id == driver_id
#     ).first()

#     if not driver:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Driver ID {driver_id} not found"
#         )

#     # 3. Check that the order exists
#     order = db.query(Order).filter(
#         Order.id == order_id
#     ).first()

#     if not order:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Order ID {order_id} not found"
#         )

#     # 4. Check whether the truck has an active or planned trip
#     active_statuses = ["planned", "in_progress"]

#     truck_busy = db.query(Trip).filter(
#         Trip.truck_id == truck_id,
#         Trip.status.in_(active_statuses)
#     ).first()

#     if truck_busy:
#         raise HTTPException(
#             status_code=409,
#             detail=(
#                 f"Truck ID {truck_id} is unavailable. "
#                 f"It already has trip ID {truck_busy.id} "
#                 f"with status '{truck_busy.status}'."
#             )
#         )

#     # 5. Check whether the driver has an active or planned trip
#     driver_busy = db.query(Trip).filter(
#         Trip.driver_id == driver_id,
#         Trip.status.in_(active_statuses)
#     ).first()

#     if driver_busy:
#         raise HTTPException(
#             status_code=409,
#             detail=(
#                 f"Driver ID {driver_id} is unavailable. "
#                 f"They already have trip ID {driver_busy.id} "
#                 f"with status '{driver_busy.status}'."
#             )
#         )

#     # 6. Create the trip only if both resources are available
#     trip = Trip(
#     truck_id=truck.id,
#     driver_id=driver.id,
#     order_id=order.id,
#     distance=distance,
#     estimated_time=estimated_time,
#     fuel_cost=fuel_cost,
#     status="planned",
#     daily_schedule=daily_schedule
# )

#     try:
#         db.add(trip)
#         db.commit()
#         db.refresh(trip)
#     except Exception:
#         db.rollback()
#         raise

#     return {
#         "message": "Trip created successfully",
#         "trip": {
#             "id": trip.id,
#             "truck_id": trip.truck_id,
#             "driver_id": trip.driver_id,
#             "order_id": trip.order_id,
#             "distance": trip.distance,
#             "estimated_time": trip.estimated_time,
#             "fuel_cost": trip.fuel_cost,
#             "status": trip.status
#         }
#     }

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


# from typing import Optional
# from datetime import datetime
# from fastapi import Body
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
    active_statuses = ["planned", "in_progress"]

    # 1. Verify the order exists
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order ID {order_id} not found"
        )

    # 2. Do not allocate an order that already has a trip
    existing_trip = db.query(Trip).filter(
        Trip.order_id == order_id
    ).first()

    if existing_trip:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Order {order_id} already has trip "
                f"ID {existing_trip.id} with status "
                f"'{existing_trip.status}'."
            )
        )

    # 3. Find trucks already reserved by active trips
    busy_truck_ids = db.query(
        Trip.truck_id
    ).filter(
        Trip.status.in_(active_statuses)
    ).distinct().all()

    busy_truck_ids = {
        row[0] for row in busy_truck_ids
    }

    # 4. Find drivers already reserved by active trips
    busy_driver_ids = db.query(
        Trip.driver_id
    ).filter(
        Trip.status.in_(active_statuses)
    ).distinct().all()

    busy_driver_ids = {
        row[0] for row in busy_driver_ids
    }

    # 5. Select an available truck with enough capacity
    trucks = db.query(Truck).all()

    available_trucks = [
        truck for truck in trucks
        if truck.id not in busy_truck_ids
        and (truck.capacity or 0) >= (order.weight or 0)
    ]

    if not available_trucks:
        raise HTTPException(
            status_code=409,
            detail=(
                "No available truck has sufficient capacity "
                "for this order."
            )
        )

    # 6. Select an available driver
    drivers = db.query(Driver).all()

    available_drivers = [
        driver for driver in drivers
        if driver.id not in busy_driver_ids
    ]

    if not available_drivers:
        raise HTTPException(
            status_code=409,
            detail="No available driver found."
        )

    # 7. Allocate the first eligible truck and driver
    truck = available_trucks[0]
    driver = available_drivers[0]

        # 8. Generate the daily schedule automatically
    if estimated_time <= 0:
        raise HTTPException(
            status_code=400,
            detail="estimated_time must be greater than zero."
        )

    schedule_result = schedule_multi_day_trip(
        distance_km=distance,
        estimated_time_hours=estimated_time,
        daily_working_hours=8,
        rest_hours=9,
    )

    daily_schedule = schedule_result["daily_schedule"]

    trip = Trip(
        truck_id=truck.id,
        driver_id=driver.id,
        order_id=order.id,
        distance=distance,
        estimated_time=estimated_time,
        fuel_cost=fuel_cost,
        status="planned",
        daily_schedule=daily_schedule
    )

    try:
        db.add(trip)
        db.commit()
        db.refresh(trip)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Trip automatically allocated successfully",
        "trip": {
            "id": trip.id,
            "truck_id": trip.truck_id,
            "driver_id": trip.driver_id,
            "order_id": trip.order_id,
            "status": trip.status,
            "daily_schedule": trip.daily_schedule
        }
    }
# daily_schedule: list[dict] | None = Body(
#     default=None,
#     example=[
#         {"day": 1, "hours": 10},
#         {"day": 2, "hours": 10},
#         {"day": 3, "hours": 4}
#     ]
# ),

@router.put("/{trip_id}/status")
def update_trip_status(
    trip_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(
        Trip.id == trip_id
    ).first()

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

    valid_transitions = {
        "planned": ["in_progress"],
        "in_progress": ["completed"],
        "completed": []
    }

    if status not in valid_transitions.get(trip.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {trip.status} -> {status}"
        )

    # Update trip status
    trip.status = status

    # Find other trips reserving this truck
    active_statuses = ["planned", "in_progress"]

    other_truck_trip = db.query(Trip).filter(
        Trip.truck_id == trip.truck_id,
        Trip.id != trip.id,
        Trip.status.in_(active_statuses)
    ).first()

    # Find other trips reserving this driver
    other_driver_trip = db.query(Trip).filter(
        Trip.driver_id == trip.driver_id,
        Trip.id != trip.id,
        Trip.status.in_(active_statuses)
    ).first()

    # Update truck availability
    truck = db.query(Truck).filter(
        Truck.id == trip.truck_id
    ).first()

    if truck:
        truck.status = (
            "assigned" if other_truck_trip else "available"
        )

    # Update driver availability
    driver = db.query(Driver).filter(
        Driver.id == trip.driver_id
    ).first()

    if driver:
        driver.status = (
            "busy" if other_driver_trip else "available"
        )

    # Synchronize order status
    order = db.query(Order).filter(
        Order.id == trip.order_id
    ).first()

    if order:
        if status == "in_progress":
            order.status = "in_progress"
        elif status == "completed":
            order.status = "completed"

    try:
        db.commit()
        db.refresh(trip)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Trip status updated successfully",
        "trip_id": trip.id,
        "truck_id": trip.truck_id,
        "driver_id": trip.driver_id,
        "trip_status": trip.status,
        "truck_status": truck.status if truck else None,
        "driver_status": driver.status if driver else None,
        "order_status": order.status if order else None
    }
