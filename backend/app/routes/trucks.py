from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Truck


router = APIRouter(
    prefix="/trucks",
    tags=["Trucks"]
)


@router.post("/")
def create_truck(
    registration_number: str,
    capacity: int,
    fuel_type: str,
    fuel_efficiency: int = None,
    company_id: int = 1,
    db: Session = Depends(get_db)
):
    existing_truck = (
        db.query(Truck)
        .filter(Truck.registration_number == registration_number)
        .first()
    )

    if existing_truck:
        raise HTTPException(
            status_code=400,
            detail="Truck with this registration number already exists"
        )

    truck = Truck(
        registration_number=registration_number,
        capacity=capacity,
        fuel_type=fuel_type,
        fuel_efficiency=fuel_efficiency,
        company_id=company_id
    )

    db.add(truck)
    db.commit()
    db.refresh(truck)

    return {
        "message": "Truck created successfully",
        "truck": {
            "id": truck.id,
            "registration_number": truck.registration_number,
            "capacity": truck.capacity,
            "fuel_type": truck.fuel_type,
            "fuel_efficiency": truck.fuel_efficiency,
            "status": truck.status,
            "company_id": truck.company_id
        }
    }


@router.get("/")
def get_trucks(
    db: Session = Depends(get_db)
):
    trucks = db.query(Truck).all()

    return trucks


@router.get("/{truck_id}")
def get_truck(
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

    return truck