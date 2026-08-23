from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Company


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.post("/")
def create_company(
    name: str,
    email: str,
    phone: str = None,
    db: Session = Depends(get_db)
):
    existing_company = (
        db.query(Company)
        .filter(Company.email == email)
        .first()
    )

    if existing_company:
        raise HTTPException(
            status_code=400,
            detail="Company with this email already exists"
        )

    company = Company(
        name=name,
        email=email,
        phone=phone
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return {
        "message": "Company created successfully",
        "company": {
            "id": company.id,
            "name": company.name,
            "email": company.email,
            "phone": company.phone
        }
    }


@router.get("/")
def get_companies(
    db: Session = Depends(get_db)
):
    companies = db.query(Company).all()

    return companies


@router.get("/{company_id}")
def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return company