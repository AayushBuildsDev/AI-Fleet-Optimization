from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Order


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
    company_id: int = 1,
    db: Session = Depends(get_db)
):
    order = Order(
        pickup_location=pickup_location,
        delivery_location=delivery_location,
        weight=weight,
        deadline=deadline,
        distance_km=distance_km,
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
            "deadline": order.deadline,
            "status": order.status,
            "company_id": order.company_id
        }
    }

@router.get("/")
def get_orders(
    db: Session = Depends(get_db)
):
    orders = db.query(Order).all()

    return orders


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