from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20))

    users = relationship("User", back_populates="company")
    trucks = relationship("Truck", back_populates="company")
    drivers = relationship("Driver", back_populates="company")
    orders = relationship("Order", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)

    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="users")


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    fuel_type = Column(String(30), nullable=False)
    fuel_efficiency = Column(Integer)
    status = Column(String(30), default="available")

    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="trucks")
    trips = relationship("Trip", back_populates="truck")
    maintenance_records = relationship(
        "Maintenance",
        back_populates="truck"
    )
    gps_records = relationship(
        "GPSTracking",
        back_populates="truck"
    )


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    license_category = Column(String(50), nullable=False)
    experience_years = Column(Integer, default=0)
    working_hours = Column(Integer, default=0)
    rest_hours = Column(Integer, default=0)
    status = Column(String(30), default="available")

    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="drivers")
    trips = relationship("Trip", back_populates="driver")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    pickup_location = Column(String(255), nullable=False)
    delivery_location = Column(String(255), nullable=False)
    weight = Column(Integer, nullable=False)
    deadline = Column(String(50), nullable=False)
    status = Column(String(30), default="pending")

    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="orders")
    trips = relationship("Trip", back_populates="order")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)

    truck_id = Column(Integer, ForeignKey("trucks.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))

    distance = Column(Integer)
    estimated_time = Column(Integer)
    fuel_cost = Column(Integer)
    status = Column(String(30), default="planned")

    truck = relationship("Truck", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    order = relationship("Order", back_populates="trips")


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)

    truck_id = Column(Integer, ForeignKey("trucks.id"))

    service_date = Column(String(50), nullable=False)
    maintenance_type = Column(String(100), nullable=False)
    odometer = Column(Integer)
    engine_hours = Column(Integer)
    cost = Column(Integer)
    status = Column(String(30), default="completed")

    truck = relationship(
        "Truck",
        back_populates="maintenance_records"
    )


class GPSTracking(Base):
    __tablename__ = "gps_tracking"

    id = Column(Integer, primary_key=True, index=True)

    truck_id = Column(Integer, ForeignKey("trucks.id"))

    latitude = Column(String(50), nullable=False)
    longitude = Column(String(50), nullable=False)
    speed = Column(Integer, default=0)
    timestamp = Column(String(50), nullable=False)

    truck = relationship(
        "Truck",
        back_populates="gps_records"
    )