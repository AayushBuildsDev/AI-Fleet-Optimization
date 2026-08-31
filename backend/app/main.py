from fastapi import FastAPI
from sqlalchemy import text

from app.database.connection import engine, Base
from app.database import models
from app.routes import (
    companies,
    users,
    trucks,
    drivers,
    orders,
    trips,
    maintenance,
    gps,
    optimization,
    dashboard
)

app = FastAPI(
    title="AI Fleet Optimization API",
    description="Backend API for AI-powered fleet and logistics optimization.",
    version="1.0.0"
)


# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(companies.router)
app.include_router(users.router)
app.include_router(trucks.router)
app.include_router(drivers.router)
app.include_router(orders.router)
app.include_router(trips.router)
app.include_router(maintenance.router)
app.include_router(gps.router)
app.include_router(optimization.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return {
        "message": "AI Fleet Optimization API is running"
    }


@app.get("/test-db")
def test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "message": "PostgreSQL connection successful"
        }

    except Exception as e:
        return {
            "message": "PostgreSQL connection failed",
            "error": str(e)
        }