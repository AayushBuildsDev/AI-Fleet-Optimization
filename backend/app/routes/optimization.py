from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Truck, Driver, Order

from app.optimization.load_optimizer import optimize_loads
from app.optimization.load_optimizer_v2 import optimize_loads_v2
from app.optimization.load_optimizer_v3 import optimize_loads_v3
from app.optimization.load_optimizer_v4 import optimize_loads_v4


router = APIRouter(
    prefix="/optimization",
    tags=["Optimization"]
)


# V1
@router.get("/load-allocation")
def load_allocation(
    db: Session = Depends(get_db)
):
    trucks = (
        db.query(Truck)
        .filter(Truck.status == "available")
        .all()
    )

    orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .all()
    )

    if not trucks:
        return {
            "message": "No available trucks found"
        }

    if not orders:
        return {
            "message": "No pending orders found"
        }

    result = optimize_loads(
        trucks,
        orders
    )

    return result


# V2 — Fuel-aware optimization
@router.get("/load-allocation-v2")
def load_allocation_v2(
    fuel_price: int = 90,
    db: Session = Depends(get_db)
):
    trucks = (
        db.query(Truck)
        .filter(Truck.status == "available")
        .all()
    )

    orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .all()
    )

    if not trucks:
        return {
            "message": "No available trucks found"
        }

    if not orders:
        return {
            "message": "No pending orders found"
        }

    result = optimize_loads_v2(
        trucks,
        orders,
        fuel_price
    )

    return result

#v3
@router.get("/load-allocation-v3")
def load_allocation_v3(
    fuel_price: int = 90,
    db: Session = Depends(get_db)
):
    trucks = (
        db.query(Truck)
        .filter(Truck.status == "available")
        .all()
    )

    orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .all()
    )

    if not trucks:
        return {
            "message": "No available trucks found"
        }

    if not orders:
        return {
            "message": "No pending orders found"
        }

    result = optimize_loads_v3(
        trucks,
        orders,
        fuel_price
    )

    return result

#v4
@router.get("/load-allocation-v4")
def load_allocation_v4(
    fuel_price: int = 90,
    db: Session = Depends(get_db)
):
    trucks = (
        db.query(Truck)
        .filter(Truck.status == "available")
        .all()
    )

    drivers = (
        db.query(Driver)
        .filter(Driver.status == "available")
        .all()
    )

    orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .all()
    )

    if not trucks:
        return {
            "message": "No available trucks found"
        }

    if not drivers:
        return {
            "message": "No available drivers found"
        }

    if not orders:
        return {
            "message": "No pending orders found"
        }

    result = optimize_loads_v4(
        trucks,
        drivers,
        orders,
        fuel_price
    )

    return result