from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Truck, Driver, Order, Trip

from app.optimization.load_optimizer import optimize_loads
from app.optimization.load_optimizer_v2 import optimize_loads_v2
from app.optimization.load_optimizer_v3 import optimize_loads_v3
from app.optimization.load_optimizer_v4 import optimize_loads_v4
from app.optimization.route_optimizer import optimize_route
from app.optimization.fleet_route_optimizer import optimize_fleet_routes
from app.optimization.distance_matrix import build_distance_matrix


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

#route
@router.get("/route")
def calculate_route(
    truck_id: int = 1,
    driver_id: int = 1,
    fuel_price: int = 90,
    db: Session = Depends(get_db)
):
    orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .all()
    )
    truck = (
    db.query(Truck)
    .filter(
        Truck.id == truck_id,
        Truck.status == "available"
    )
    .first()
)

    if not truck:
     return {
        "message": "Available truck not found"
    }

    if not orders:
        return {
            "message": "No pending orders found"
        }
    driver = (
    db.query(Driver)
    .filter(
        Driver.id == driver_id,
        Driver.status == "available"
    )
    .first()
)

    if not driver:
         return {
           "message": "Available driver not found"
    }

    distance_matrix = build_distance_matrix(orders)

    result = optimize_route(
    distance_matrix,
    orders,
    truck.capacity
)
    if result["status"] == "route_not_feasible":
     return {
        "status": "route_not_feasible",
        "message": "No feasible route found. Truck capacity may be exceeded.",
        "truck_id": truck.id,
        "truck_capacity": truck.capacity,
        "driver_id": driver.id
    }
    average_speed_kmh = 50

    estimated_driving_hours = (
    result["total_distance"] / average_speed_kmh
)
   

    if truck.fuel_efficiency and truck.fuel_efficiency > 0:
        fuel_used_liters = (
        result["total_distance"]
        / truck.fuel_efficiency
    )

        fuel_cost = (
        fuel_used_liters
        * fuel_price
    )
    else:
        fuel_used_liters = 0
        fuel_cost = 0

    if estimated_driving_hours > driver.working_hours:
     return {
        "status": "route_not_feasible",
        "message": "Driver does not have enough working hours",
        "driver_id": driver.id,
        "driver_working_hours": driver.working_hours,
        "estimated_driving_hours": round(
            estimated_driving_hours,
            2
        )
        
    }
    for location in result["route"]:

      if location == 0:
        continue

      order_index = location - 1

      if order_index < len(orders):
        order = orders[order_index]

        existing_trip = (
            db.query(Trip)
            .filter(
                Trip.order_id == order.id,
                Trip.status == "planned"
            )
            .first()
        )

        if existing_trip:
            continue

        order_distance = order.distance_km or 0

        order_time_hours = (
            order_distance / average_speed_kmh
        )

        order_fuel_liters = 0

        if truck.fuel_efficiency and truck.fuel_efficiency > 0:
            order_fuel_liters = (
                order_distance / truck.fuel_efficiency
            )

        order_fuel_cost = (
            order_fuel_liters * fuel_price
        )

        trip = Trip(
            truck_id=truck.id,
            driver_id=driver.id,
            order_id=order.id,
            distance=order_distance,
            estimated_time=int(
                order_time_hours * 60
            ),
            fuel_cost=int(
                order_fuel_cost
            ),
            status="planned"
        )

        db.add(trip)
        order.status = "assigned"

    db.commit()
    route_details = []

    for location in result["route"]:

     if location == 0:
        route_details.append({
            "location": "Depot"
        })
    else:
        order_index = location - 1

        if order_index < len(orders):
            order = orders[order_index]

            route_details.append({
                "location": order.delivery_location,
                "order_id": order.id,
                "pickup_location": order.pickup_location,
                "delivery_location": order.delivery_location,
                "distance_km": order.distance_km
            })

    return {
    "status": result["status"],
    "truck_id": truck.id,
    "truck_registration": truck.registration_number,
    "truck_capacity": truck.capacity,
    "driver_id": driver.id,
    "driver_name": driver.name,
    "driver_working_hours": driver.working_hours,
    "average_speed_kmh": average_speed_kmh,
    "estimated_driving_hours": round(
        estimated_driving_hours,
        2
    ),
    "fuel_price_per_liter": fuel_price,
    "fuel_used_liters": round(
      fuel_used_liters,
      2
),
    "fuel_cost": round(
      fuel_cost,
      2
),
}

#calculate fleet
@router.get("/fleet-route")
def calculate_fleet_route(
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
    if len(drivers) < len(trucks):
     return {
        "status": "fleet_not_feasible",
        "message": "Not enough available drivers for available trucks",
        "available_trucks": len(trucks),
        "available_drivers": len(drivers)
    }

    if not orders:
        return {
            "message": "No pending orders found"
        }

    distance_matrix = build_distance_matrix(orders)

    result = optimize_fleet_routes(
        distance_matrix,
        orders,
        trucks
    )

    if result["status"] == "route_not_feasible":
        return result

    routes = []

    for route_data in result["routes"]:

        truck = trucks[route_data["truck_index"]]

        driver = drivers[
            route_data["truck_index"] % len(drivers)
        ]

        routes.append({
            "truck_id": truck.id,
            "truck_registration": truck.registration_number,
            "truck_capacity": truck.capacity,
            "driver_id": driver.id,
            "driver_name": driver.name,
            "route": route_data["route"],
            "total_distance": route_data["total_distance"],
            "total_weight": route_data["total_weight"]
        })

        average_speed_kmh = 50

    estimated_driving_hours = (
    route_data["total_distance"] / average_speed_kmh
)

    if estimated_driving_hours > driver.working_hours:
     return {
        "status": "fleet_not_feasible",
        "message": "Driver does not have enough working hours",
        "truck_id": truck.id,
        "driver_id": driver.id,
        "driver_working_hours": driver.working_hours,
        "estimated_driving_hours": round(
            estimated_driving_hours,
            2
        )
    }

     # Create Trips for each optimized route
    for route_data in result["routes"]:

        truck = trucks[route_data["truck_index"]]

        driver = drivers[
    route_data["truck_index"]
]

        for location in route_data["route"]:

            if location == 0:
                continue

            order_index = location - 1

            if order_index >= len(orders):
                continue

            order = orders[order_index]

            # Prevent duplicate planned trips
            existing_trip = (
                db.query(Trip)
                .filter(
                    Trip.order_id == order.id,
                    Trip.status == "planned"
                )
                .first()
            )

            if existing_trip:
               order.status = "assigned"
               continue

            order_distance = order.distance_km or 0

            average_speed_kmh = 50

            order_time_hours = (
                order_distance / average_speed_kmh
            )

            order_fuel_liters = 0

            if (
                truck.fuel_efficiency
                and truck.fuel_efficiency > 0
            ):
                order_fuel_liters = (
                    order_distance
                    / truck.fuel_efficiency
                )

            order_fuel_cost = (
                order_fuel_liters * fuel_price
            )

            trip = Trip(
                truck_id=truck.id,
                driver_id=driver.id,
                order_id=order.id,
                distance=order_distance,
                estimated_time=int(
                    order_time_hours * 60
                ),
                fuel_cost=int(
                    order_fuel_cost
                ),
                status="planned"
            )

            db.add(trip)

            order.status = "assigned"

    db.commit()       

    return {
        "status": result["status"],
        "fuel_price_per_liter": fuel_price,
        "routes": routes
    }

   