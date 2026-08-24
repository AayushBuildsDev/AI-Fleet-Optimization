from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Driver


router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"]
)


@router.post("/")
def create_driver(
    name: str,
    license_category: str,
    experience_years: int = 0,
    working_hours: int = 0,
    rest_hours: int = 0,
    company_id: int = 1,
    db: Session = Depends(get_db)
):
    driver = Driver(
        name=name,
        license_category=license_category,
        experience_years=experience_years,
        working_hours=working_hours,
        rest_hours=rest_hours,
        company_id=company_id
    )

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return {
        "message": "Driver created successfully",
        "driver": {
            "id": driver.id,
            "name": driver.name,
            "license_category": driver.license_category,
            "experience_years": driver.experience_years,
            "working_hours": driver.working_hours,
            "rest_hours": driver.rest_hours,
            "status": driver.status,
            "company_id": driver.company_id
        }
    }


@router.get("/")
def get_drivers(
    db: Session = Depends(get_db)
):
    drivers = db.query(Driver).all()

    return drivers


@router.get("/{driver_id}")
def get_driver(
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

    return driver