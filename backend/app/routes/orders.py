from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Order, Trip

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/")
def create_order(
    pickup_location: str,
    delivery_location: str,
    weight: int,
    deadline: str,
    distance_km: int = 0,
    pickup_latitude: str = None,
    pickup_longitude: str = None,
    delivery_latitude: str = None,
    delivery_longitude: str = None,
    company_id: int = 1,
    db: Session = Depends(get_db)
):
    order = Order(
        pickup_location=pickup_location,
        delivery_location=delivery_location,
        weight=weight,
        deadline=deadline,
        distance_km=distance_km,
        pickup_latitude=pickup_latitude,
        pickup_longitude=pickup_longitude,
        delivery_latitude=delivery_latitude,
        delivery_longitude=delivery_longitude,
        company_id=company_id
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "message": "Order created successfully",
        "order": {
            "id": order.id,
            "pickup_location": order.pickup_location,
            "delivery_location": order.delivery_location,
            "weight": order.weight,
            "distance_km": order.distance_km,
            "pickup_latitude": order.pickup_latitude,
            "pickup_longitude": order.pickup_longitude,
            "delivery_latitude": order.delivery_latitude,
            "delivery_longitude": order.delivery_longitude,
            "deadline": order.deadline,
            "status": order.status,
            "company_id": order.company_id
        }
    }

@router.get("/")
def get_orders(
    db: Session = Depends(get_db)
):
    return db.query(Order).all()

@router.get("/{order_id}/tracking")
def get_order_tracking(
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

    trip = (
        db.query(Trip)
        .filter(Trip.order_id == order_id)
        .order_by(Trip.id.desc())
        .first()
    )

    return {
        "order_id": order.id,
        "order_status": order.status,
        "trip_id": trip.id if trip else None,
        "trip_status": trip.status if trip else None,
        "truck_id": trip.truck_id if trip else None,
        "driver_id": trip.driver_id if trip else None
    }

@router.get("/{order_id}")
def get_order(
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

    return order

@router.get("/{order_id}/trips")
def get_order_trips(
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