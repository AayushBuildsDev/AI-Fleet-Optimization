from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.optimization.road_route import get_road_route
from app.optimization.depot import DEPOT_LATITUDE, DEPOT_LONGITUDE
from app.database.connection import get_db
from app.database.models import Truck, Driver, Order, Trip
from datetime import date, datetime, timedelta
from app.optimization.load_optimizer import optimize_loads
from app.optimization.load_optimizer_v2 import optimize_loads_v2
from app.optimization.load_optimizer_v3 import optimize_loads_v3
from app.optimization.load_optimizer_v4 import optimize_loads_v4
from app.optimization.route_optimizer import optimize_route
from app.optimization.fleet_route_optimizer import optimize_fleet_routes
from app.optimization.distance_matrix import build_distance_matrix
from math import isfinite

router = APIRouter(
    prefix="/optimization",
    tags=["Optimization"]
)



def parse_order_deadline(deadline_value):
    """Return (deadline, is_date_only)."""
    if not deadline_value:
        return None, None

    deadline_string = str(deadline_value).strip()

    # ISO date-only format: 2026-10-30
    try:
        deadline_date = date.fromisoformat(deadline_string)
        return deadline_date, True
    except ValueError:
        pass

    # Legacy date-only formats.
    for date_format in ("%d-%m-%y", "%d-%m-%Y"):
        try:
            deadline_date = datetime.strptime(
                deadline_string, date_format
            ).date()
            return deadline_date, True
        except ValueError:
            continue

    # ISO date-time format.
    try:
        deadline_datetime = datetime.fromisoformat(
            deadline_string.replace("Z", "+00:00")
        )
        return deadline_datetime, False
    except ValueError as exc:
        raise ValueError(
            f"Unsupported deadline format: {deadline_string}"
        ) from exc


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
    all_pending_orders = (
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
    orders = []

    for order in all_pending_orders:
        try:
            weight = float(order.weight)
            latitude = float(order.delivery_latitude)
            longitude = float(order.delivery_longitude)
        except (TypeError, ValueError):
            continue

        if (
            weight > 0
            and weight <= truck.capacity
            and -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            orders.append(order)

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


    if driver.company_id != truck.company_id:
        return {
            "status": "assignment_not_allowed",
            "message": (
                "The selected truck and driver "
                "must belong to the same company."
            ),
            "truck_id": truck.id,
            "driver_id": driver.id
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

        if truck.fuel_efficiency and truck.fuel_efficiency > 0:
            order_fuel_liters = (
                order_distance / truck.fuel_efficiency
            )

        order_fuel_cost = (
            order_fuel_liters * fuel_price
        )

        road_route = get_road_route(
            DEPOT_LATITUDE,
            DEPOT_LONGITUDE,
            float(order.delivery_latitude),
            float(order.delivery_longitude)
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
            status="planned",
            planned_route={
                "coordinates": road_route["coordinates"],
                "distance_km": road_route["distance_km"],
                "duration_minutes": road_route["duration_minutes"]
            }
        )

        db.add(trip)
        order.status = "assigned"
        truck.status = "assigned"
        driver.status = "busy"

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

        # Keep only trucks that have an available driver
    # from the same company.
    compatible_trucks = [
        truck
        for truck in trucks
        if any(
            driver.company_id == truck.company_id
            for driver in drivers
        )
    ]

    if not compatible_trucks:
        return {
            "status": "fleet_not_feasible",
            "message": (
                "No available truck has a compatible "
                "available driver from the same company."
            )
        }

    trucks = compatible_trucks


    # Exclude orders that cannot be safely routed or assigned.
    max_capacity = max(
        (float(truck.capacity or 0) for truck in trucks),
        default=0
    )

    eligible_orders = []
    excluded_order_details = []


    # Exclude orders that already have active trips.
    active_order_ids = {
        order_id
        for (order_id,) in (
            db.query(Trip.order_id)
            .filter(
                Trip.status.in_(["planned", "in_progress"])
            )
            .all()
        )
        if order_id is not None
    }

    # for order in orders:
    #     if order.id in active_order_ids:
    #         excluded_order_details.append({
    #             "order_id": order.id,
    #             "reason": (
    #                 "Order already has a planned or in-progress trip"
    #             )
    #         })
    #         continue

    #     try:
    #         weight = float(order.weight)
    #         latitude = float(order.delivery_latitude)
    #         longitude = float(order.delivery_longitude)
    #     except (TypeError, ValueError):
    #         excluded_order_details.append({
    #             "order_id": order.id,
    #             "reason": "Missing or invalid weight/coordinates"
    #         })
    #         continue



    for order in orders:
        if order.id in active_order_ids:
            excluded_order_details.append({
                "order_id": order.id,
                "reason": (
                    "Order already has a planned or in-progress trip"
                )
            })
            continue

        try:
            weight = float(order.weight)
            latitude = float(order.delivery_latitude)
            longitude = float(order.delivery_longitude)
        except (TypeError, ValueError):
            excluded_order_details.append({
                "order_id": order.id,
                "reason": "Missing or invalid weight/coordinates"
            })
            continue
        if not all(isfinite(value) for value in (weight, latitude, longitude)):
            excluded_order_details.append({
                "order_id": order.id,
                "reason": "Weight or coordinates must be finite numbers"
            })
            continue
        if not (-90 <= latitude <= 90):
            excluded_order_details.append({
                "order_id": order.id,
                "reason": "Invalid delivery latitude"
            })
            continue

        if not (-180 <= longitude <= 180):
            excluded_order_details.append({
                "order_id": order.id,
                "reason": "Invalid delivery longitude"
            })
            continue

        if weight <= 0 or weight > max_capacity:
            excluded_order_details.append({
                "order_id": order.id,
                "reason": "Invalid weight or exceeds available capacity"
            })
            continue

        eligible_orders.append(order)


    if not eligible_orders:
        return {
            "status": "route_not_feasible",
            "message": "No pending orders fit the available trucks.",
            "excluded_orders": excluded_order_details
        }

    distance_matrix = build_distance_matrix(eligible_orders)

    result = optimize_fleet_routes(
     distance_matrix,
     eligible_orders,
     trucks,
     drivers
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
    late_orders = []
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


        # Select a compatible, unused driver who has enough working hours.
        assigned_driver_ids = {
            route["driver"].id
            for route in validated_routes
        }

        # Convert optimizer route distance to estimated driving hours.
        total_distance = route_data["total_distance"]
        estimated_driving_hours = (
            total_distance / average_speed_kmh
        )

        driver = next(
            (
                candidate
                for candidate in drivers
                if candidate.company_id == truck.company_id
                and candidate.id not in assigned_driver_ids
                and candidate.working_hours is not None
                and candidate.working_hours >= estimated_driving_hours
            ),
            None
        )

        if driver is None:
            return {
                "status": "fleet_not_feasible",
                "message": (
                    "No unused compatible driver has enough "
                    "working hours for this route."
                ),
                "truck_id": truck.id,
                "estimated_driving_hours": round(
                    estimated_driving_hours, 2
                )
            }

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

        # total_distance = route_data["total_distance"]
        # estimated_driving_hours = (
        #     total_distance / average_speed_kmh
        # )
        print("Truck ID:", truck.id)
        print("Route distance in km:", total_distance)
        print("Driver ID:", driver.id)
        print("Total distance:", total_distance)
        print("Estimated driving hours:", estimated_driving_hours)
        print("Driver working hours:", driver.working_hours)

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



        # Check each selected order's deadline before assignment.
        late_route_orders = []

        for order in route_orders:
            if not order.deadline:
                continue

            try:
                deadline, is_date_only = parse_order_deadline(
                    order.deadline
                )
            except ValueError:
                return {
                    "status": "invalid_order_deadline",
                    "message": "Invalid deadline format.",
                    "order_id": order.id,
                    "deadline": order.deadline
                }

            # Use the OSRM duration for this order's delivery.
            road_route = get_road_route(
                DEPOT_LATITUDE,
                DEPOT_LONGITUDE,
                float(order.delivery_latitude),
                float(order.delivery_longitude)
            )

            estimated_delivery_time = (
                datetime.now()
                + timedelta(
                    minutes=road_route["duration_minutes"]
                )
            )

            if is_date_only:
                is_late = (
                    estimated_delivery_time.date() > deadline
                )
            else:
                if deadline.tzinfo is not None:
                    estimated_delivery_time = (
                        estimated_delivery_time.astimezone(
                            deadline.tzinfo
                        )
                    )

                is_late = (
                    estimated_delivery_time > deadline
                )

            if is_late:
                late_route_orders.append({
                    "order_id": order.id,
                    "deadline": order.deadline,
                    "estimated_delivery_time":
                        estimated_delivery_time.isoformat()
                })

        if late_route_orders:
            late_orders.extend(late_route_orders)
            continue

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


                # Get the planned road route for this delivery.
                road_route = get_road_route(
                    DEPOT_LATITUDE,
                    DEPOT_LONGITUDE,
                    float(order.delivery_latitude),
                    float(order.delivery_longitude)
                )

                trip = Trip(
                    truck_id=truck.id,
                    driver_id=driver.id,
                    order_id=order.id,
                    distance=order_distance,
                    estimated_time=int(order_time_hours * 60),
                    fuel_cost=int(order_fuel_liters * fuel_price),
                    status="planned",
                    planned_route={
                        "coordinates": road_route["coordinates"],
                        "distance_km": road_route["distance_km"],
                        "duration_minutes": road_route["duration_minutes"]
                    }
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
        "unassigned_order_ids": result.get(
            "unassigned_order_ids", []
        ),
        "late_orders": late_orders,

        "excluded_orders": excluded_order_details

    }
