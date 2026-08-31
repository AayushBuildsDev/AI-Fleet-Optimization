from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Truck, Driver, Order, Trip


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    total_trucks = (
        db.query(Truck)
        .count()
    )

    available_trucks = (
        db.query(Truck)
        .filter(Truck.status == "available")
        .count()
    )

    assigned_trucks = (
        db.query(Truck)
        .filter(Truck.status == "assigned")
        .count()
    )

    total_drivers = (
        db.query(Driver)
        .count()
    )

    available_drivers = (
        db.query(Driver)
        .filter(Driver.status == "available")
        .count()
    )

    busy_drivers = (
        db.query(Driver)
        .filter(Driver.status == "busy")
        .count()
    )

    pending_orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .count()
    )

    assigned_orders = (
        db.query(Order)
        .filter(Order.status == "assigned")
        .count()
    )

    in_progress_orders = (
        db.query(Order)
        .filter(Order.status == "in_progress")
        .count()
    )

    completed_orders = (
        db.query(Order)
        .filter(Order.status == "completed")
        .count()
    )

    active_trips = (
        db.query(Trip)
        .filter(Trip.status == "in_progress")
        .count()
    )

    return {
        "total_trucks": total_trucks,
        "available_trucks": available_trucks,
        "assigned_trucks": assigned_trucks,
        "total_drivers": total_drivers,
        "available_drivers": available_drivers,
        "busy_drivers": busy_drivers,
        "pending_orders": pending_orders,
        "assigned_orders": assigned_orders,
        "in_progress_orders": in_progress_orders,
        "completed_orders": completed_orders,
        "active_trips": active_trips
    }