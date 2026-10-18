from datetime import datetime, timedelta
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


# V2 — Fuel-aware optimization
@router.get("/load-allocation-v2", include_in_schema=False)
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
@router.get("/load-allocation-v3", include_in_schema=False)
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
@router.get("/load-allocation-v4", include_in_schema=False)
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
@router.post("/route")
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
        truck.status = "assigned"

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


# Calculate fleet routes
@router.post("/fleet-route")
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
        return {"status": "fleet_not_feasible",
                "message": "No available trucks found"}

    if not drivers:
        return {"status": "fleet_not_feasible",
                "message": "No available drivers found"}

    if not orders:
        return {"message": "No pending orders found"}

    # Exclude orders that cannot fit any available truck.
    max_capacity = max(
        (float(truck.capacity or 0) for truck in trucks),
        default=0
    )

    eligible_orders = []

    for order in orders:
        try:
            weight = float(order.weight)
        except (TypeError, ValueError):
            continue

        if weight > 0 and weight <= max_capacity:
            eligible_orders.append(order)


    if not eligible_orders:
        return {
            "status": "route_not_feasible",
            "message": "No pending orders fit the available trucks."
        }

    distance_matrix = build_distance_matrix(eligible_orders)

    result = optimize_fleet_routes(
        distance_matrix,
        eligible_orders,
        trucks
    )

    if result.get("status") == "route_not_feasible":
        return result

    route_data_list = result.get("routes", [])

    if not route_data_list:
        return {
            "status": "route_not_feasible",
            "message": "The optimizer did not produce any routes."
        }

    # Check drivers against routes actually selected.
    if len(route_data_list) > len(drivers):
        return {
            "status": "fleet_not_feasible",
            "message": "Not enough available drivers for optimized routes.",
            "routes_found": len(route_data_list),
            "available_drivers": len(drivers)
        }

    # Validate routes before making database changes.
    routes = []
    validated_routes = []
    average_speed_kmh = 50

    for route_number, route_data in enumerate(route_data_list):
        truck_index = route_data.get("truck_index")

        if (
            not isinstance(truck_index, int)
            or truck_index < 0
            or truck_index >= len(trucks)
        ):
            return {
                "status": "fleet_not_feasible",
                "message": "Optimizer returned an invalid truck index.",
                "truck_index": truck_index
            }

        truck = trucks[truck_index]
        driver = drivers[route_number]

        # Convert optimizer route locations into actual orders.
        route_order_ids = []
        route_orders = []

        for location in route_data["route"]:
            if location == 0:
                continue

            order_index = location - 1

            if 0 <= order_index < len(eligible_orders):
                order = eligible_orders[order_index]
                route_orders.append(order)
                route_order_ids.append(order.id)

        total_weight = sum(
            order.weight or 0 for order in route_orders
        )

        if total_weight > (truck.capacity or 0):
            return {
                "status": "route_not_feasible",
                "message": "Optimized route exceeds truck capacity.",
                "truck_id": truck.id,
                "truck_capacity": truck.capacity,
                "route_total_weight": total_weight,
                "order_ids": route_order_ids
            }

        total_distance = route_data["total_distance"]
        estimated_driving_hours = (
            total_distance / average_speed_kmh
        )

        if (
            driver.working_hours is not None
            and estimated_driving_hours > driver.working_hours
        ):
            return {
                "status": "fleet_not_feasible",
                "message": "Driver does not have enough working hours.",
                "truck_id": truck.id,
                "driver_id": driver.id,
                "driver_working_hours": driver.working_hours,
                "estimated_driving_hours": round(
                    estimated_driving_hours, 2
                )
            }

        # Check fuel cost.
        if truck.fuel_efficiency and truck.fuel_efficiency > 0:
            fuel_used_liters = (
                total_distance / truck.fuel_efficiency
            )
            fuel_cost = fuel_used_liters * fuel_price
        else:
            fuel_used_liters = 0
            fuel_cost = 0

        # Check deadlines before creating any trips.
        for order in route_orders:
            if not order.deadline:
                continue

            try:
                deadline_string = order.deadline.strip()

                # Supports YYYY-MM-DD and DD-MM-YY formats.
                try:
                    deadline = datetime.fromisoformat(deadline_string)
                except ValueError:
                    deadline = datetime.strptime(
                        deadline_string, "%d-%m-%y"
                    )

            except (ValueError, AttributeError):
                return {
                    "status": "invalid_order_deadline",
                    "message": "Invalid deadline format.",
                    "order_id": order.id,
                    "deadline": order.deadline
                }

            order_distance = order.distance_km or 0
            estimated_delivery_time = (
                datetime.now()
                + timedelta(
                    hours=order_distance / average_speed_kmh
                )
            )

            # Compare calendar dates when the deadline has no time.
            if "T" not in deadline_string and " " not in deadline_string:
                is_late = (
                    estimated_delivery_time.date() > deadline.date()
                )
            else:
                is_late = estimated_delivery_time > deadline

            if is_late:
                return {
                    "status": "fleet_not_feasible",
                    "message": "Order cannot be delivered before deadline.",
                    "order_id": order.id,
                    "deadline": order.deadline,
                    "estimated_delivery_time":
                        estimated_delivery_time.isoformat()
                }

        routes.append({
            "truck_id": truck.id,
            "truck_registration": truck.registration_number,
            "truck_capacity": truck.capacity,
            "driver_id": driver.id,
            "driver_name": driver.name,
            "route": route_data["route"],
            "order_ids": route_order_ids,
            "order_count": len(route_order_ids),
            "total_distance": total_distance,
            "total_weight": total_weight,
            "estimated_driving_hours": round(
                estimated_driving_hours, 2
            ),
            "fuel_used_liters": round(fuel_used_liters, 2),
            "fuel_cost": round(fuel_cost, 2)
        })

        validated_routes.append({
            "truck": truck,
            "driver": driver,
            "orders": route_orders
        })

    # Create trips only after every route passes validation.
    try:
        for validated in validated_routes:
            truck = validated["truck"]
            driver = validated["driver"]

            for order in validated["orders"]:
                existing_trip = (
                    db.query(Trip)
                    .filter(
                        Trip.order_id == order.id,
                        Trip.status.in_(["planned", "in_progress"])
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

                if (
                    truck.fuel_efficiency
                    and truck.fuel_efficiency > 0
                ):
                    order_fuel_liters = (
                        order_distance / truck.fuel_efficiency
                    )

                trip = Trip(
                    truck_id=truck.id,
                    driver_id=driver.id,
                    order_id=order.id,
                    distance=order_distance,
                    estimated_time=int(order_time_hours * 60),
                    fuel_cost=int(order_fuel_liters * fuel_price),
                    status="planned"
                )

                db.add(trip)
                order.status = "assigned"

            truck.status = "assigned"
            driver.status = "busy"

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "status": result.get("status", "success"),
        "fuel_price_per_liter": fuel_price,
        "routes": routes,
        "excluded_orders": [
            {
                "order_id": order.id,
                "weight": order.weight,
                "reason": "Exceeds every available truck's capacity"
            }
            for order in orders
            if order not in eligible_orders
        ]
    }
