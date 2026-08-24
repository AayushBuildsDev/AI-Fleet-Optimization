from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import GPSTracking


router = APIRouter(
    prefix="/gps",
    tags=["GPS Tracking"]
)


@router.post("/")
def create_gps_record(
    truck_id: int,
    latitude: str,
    longitude: str,
    speed: int = 0,
    timestamp: str = "",
    db: Session = Depends(get_db)
):
    gps_record = GPSTracking(
        truck_id=truck_id,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        timestamp=timestamp
    )

    db.add(gps_record)
    db.commit()
    db.refresh(gps_record)

    return {
        "message": "GPS record created successfully",
        "gps": {
            "id": gps_record.id,
            "truck_id": gps_record.truck_id,
            "latitude": gps_record.latitude,
            "longitude": gps_record.longitude,
            "speed": gps_record.speed,
            "timestamp": gps_record.timestamp
        }
    }


@router.get("/")
def get_gps_records(
    db: Session = Depends(get_db)
):
    records = db.query(GPSTracking).all()

    return records


@router.get("/{truck_id}")
def get_truck_location(
    truck_id: int,
    db: Session = Depends(get_db)
):
    record = (
        db.query(GPSTracking)
        .filter(GPSTracking.truck_id == truck_id)
        .order_by(GPSTracking.id.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="GPS record not found for this truck"
        )

    return {
        "truck_id": record.truck_id,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "speed": record.speed,
        "timestamp": record.timestamp
    }