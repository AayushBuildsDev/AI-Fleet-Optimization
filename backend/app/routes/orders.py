from fastapi import APIRouter, Depends
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