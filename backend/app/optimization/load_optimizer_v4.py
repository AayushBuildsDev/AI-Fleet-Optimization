import math
from ortools.linear_solver import pywraplp
from app.optimization.multi_day_scheduler import (
    schedule_multi_day_trip,
)
def optimize_loads_v4(trucks, drivers, orders, fuel_price=90):
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        raise RuntimeError(
            "OR-Tools SCIP solver could not be created."
        )

    # -----------------------------------------------
    # Prepare and validate input data
    # -----------------------------------------------
    if not trucks:
        return {
            "status": "No available trucks",
            "assignments": [],
            "unassigned_orders": [
                {"order_id": o.id, "reason": "No available trucks"}
                for o in orders
            ]
        }

    if not drivers:
        return {
            "status": "No available drivers",
            "assignments": [],
            "unassigned_orders": [
                {"order_id": o.id, "reason": "No available drivers"}
                for o in orders
            ]
        }

    valid_orders = []
    unassigned_orders = []

    max_capacity = max(
        float(t.capacity or 0) for t in trucks
    )
    max_working_hours = max(
        float(d.working_hours or 0) for d in drivers
    )

    for order in orders:
        try:
            weight = float(order.weight)
            distance = float(order.distance_km)
        except (TypeError, ValueError):
            unassigned_orders.append({
                "order_id": order.id,
                "reason": "Invalid order weight or distance"
            })
            continue

        if weight <= 0 or distance < 0:
            unassigned_orders.append({
                "order_id": order.id,
                "reason": "Invalid order weight or distance"
            })
            continue

        if weight > max_capacity:
            unassigned_orders.append({
                "order_id": order.id,
                "reason": "Order exceeds every available truck's capacity",
                "weight": weight,
                "largest_truck_capacity": max_capacity
            })
            continue

        # if distance / 50 > max_working_hours:
        #     unassigned_orders.append({
        #         "order_id": order.id,
        #         "reason": "Order exceeds every available driver's working hours",
        #         "estimated_driving_hours": round(distance / 50, 2),
        #         "maximum_driver_working_hours": max_working_hours
        #     })
        #     continue

        valid_orders.append(order)

    if not valid_orders:
        return {
            "status": "No feasible orders",
            "assignments": [],
            "unassigned_orders": unassigned_orders
        }

    # -----------------------------------------------
    # Decision variables
    #
    # x[t,d,o] = order o assigned to truck t and driver d
    # y[t,d]   = driver d assigned to truck t
    # -----------------------------------------------
    x = {}
    y = {}

    for truck in trucks:
        for driver in drivers:
            y[truck.id, driver.id] = solver.BoolVar(
                f"y_{truck.id}_{driver.id}"
            )

            for order in valid_orders:
                x[truck.id, driver.id, order.id] = (
                    solver.BoolVar(
                        f"x_{truck.id}_{driver.id}_{order.id}"
                    )
                )

    # Each truck has at most one assigned driver.
    for truck in trucks:
        solver.Add(
            sum(y[truck.id, driver.id] for driver in drivers) <= 1
        )

    # Each driver can be assigned to at most one truck.
    for driver in drivers:
        solver.Add(
            sum(y[truck.id, driver.id] for truck in trucks) <= 1
        )

    # An order can only be assigned to a truck-driver pair
    # when that driver is assigned to that truck.
    for truck in trucks:
        for driver in drivers:
            for order in valid_orders:
                solver.Add(
                    x[truck.id, driver.id, order.id]
                    <= y[truck.id, driver.id]
                )

    # Each order can be assigned at most once.
    for order in valid_orders:
        solver.Add(
            sum(
                x[truck.id, driver.id, order.id]
                for truck in trucks
                for driver in drivers
            ) <= 1
        )

    # Truck capacity constraint.
    for truck in trucks:
        solver.Add(
            sum(
                float(order.weight)
                * x[truck.id, driver.id, order.id]
                for driver in drivers
                for order in valid_orders
            ) <= float(truck.capacity or 0)
        )


# Multi-day driver-hours constraint.

    AVERAGE_SPEED_KMH = 50
    PLANNING_HORIZON_DAYS = 7

    for driver in drivers:
        daily_hours = float(driver.working_hours or 0)

        solver.Add(
            sum(
                (float(order.distance_km) / AVERAGE_SPEED_KMH)
                * x[truck.id, driver.id, order.id]
                for truck in trucks
                for order in valid_orders
            )
            <= daily_hours * PLANNING_HORIZON_DAYS
        )

    # -----------------------------------------------
    # Stage 1: Maximize the number of assigned orders.
    # -----------------------------------------------
    assigned_count = sum(
        x[truck.id, driver.id, order.id]
        for truck in trucks
        for driver in drivers
        for order in valid_orders
    )

    solver.Maximize(assigned_count)
    status = solver.Solve()

    if status not in (
        pywraplp.Solver.OPTIMAL,
        pywraplp.Solver.FEASIBLE
    ):
        return {
            "status": "No feasible solution found",
            "assignments": [],
            "unassigned_orders": unassigned_orders,
            "message": "The allocation constraints could not be satisfied."
        }

    best_count = round(assigned_count.solution_value())

    # -----------------------------------------------
    # Stage 2: Minimize fuel cost while retaining the
    # maximum number of assigned orders.
    # -----------------------------------------------
    solver.Add(assigned_count == best_count)

    objective = solver.Objective()

    for truck in trucks:
        efficiency = float(truck.fuel_efficiency or 0)

        for driver in drivers:
            for order in valid_orders:
                if efficiency > 0:
                    cost = (
                        float(order.distance_km)
                        / efficiency
                        * fuel_price
                    )
                else:
                    # Avoid assigning orders to trucks with
                    # unknown fuel efficiency when alternatives
                    # have valid efficiency.
                    cost = 1_000_000

                objective.SetCoefficient(
                    x[truck.id, driver.id, order.id],
                    cost
                )

    objective.SetMinimization()
    status = solver.Solve()

    if status not in (
        pywraplp.Solver.OPTIMAL,
        pywraplp.Solver.FEASIBLE
    ):
        return {
            "status": "No feasible solution found",
            "assignments": [],
            "unassigned_orders": unassigned_orders,
            "message": "Fuel-cost optimization failed."
        }

    # -----------------------------------------------
    # Build results
    # -----------------------------------------------
    assignments = []
    assigned_order_ids = set()

    for truck in trucks:
        for driver in drivers:
            if y[truck.id, driver.id].solution_value() < 0.5:
                continue

            assigned_orders = []

            for order in valid_orders:
                if x[
                    truck.id, driver.id, order.id
                ].solution_value() < 0.5:
                    continue

                distance = float(order.distance_km)
                efficiency = float(truck.fuel_efficiency or 0)

                fuel_used = (
                    distance / efficiency
                    if efficiency > 0
                    else 0
                )
                fuel_cost = fuel_used * fuel_price
                trip_schedule = schedule_multi_day_trip(
                distance_km=distance,
                daily_working_hours=float(driver.working_hours or 0),
               )


                assigned_orders.append({
                    "order_id": order.id,
                    "weight": float(order.weight),
                    "distance_km": distance,
                    "estimated_driving_hours": round(
                        distance / 50, 2
                    ),
                    "estimated_days": trip_schedule["estimated_days"],
                    "daily_schedule": trip_schedule["daily_schedule"],
                    "fuel_used_liters": round(fuel_used, 2),
                    "fuel_cost": round(fuel_cost, 2),
                })


                assigned_order_ids.add(order.id)

            if not assigned_orders:
                continue

            total_weight = sum(
                item["weight"] for item in assigned_orders
            )
            total_distance = sum(
                item["distance_km"] for item in assigned_orders
            )
            total_hours = sum(
                item["estimated_driving_hours"]
                for item in assigned_orders
            )
            total_fuel_cost = sum(
                item["fuel_cost"] for item in assigned_orders
            )

            capacity = float(truck.capacity or 0)

            assignments.append({
                "truck_id": truck.id,
                "truck_registration": truck.registration_number,
                "driver_id": driver.id,
                "driver_name": driver.name,
                "truck_capacity": capacity,
                "total_weight": total_weight,
                "utilization_percentage": round(
                    total_weight / capacity * 100, 2
                ) if capacity > 0 else 0,
                "driver_working_hours": driver.working_hours,
                "total_driving_hours": round(total_hours, 2),
                "total_distance_km": round(total_distance, 2),
                "total_fuel_cost": round(total_fuel_cost, 2),
                "orders": assigned_orders

                
            })

#             trip_schedule = schedule_multi_day_trip(
#             distance_km=distance,
#             daily_working_hours=float(driver.working_hours or 0),
# )

    # Include eligible orders that could not be assigned
    # because of combined resource constraints.
    for order in valid_orders:
        if order.id not in assigned_order_ids:
            unassigned_orders.append({
                "order_id": order.id,
                "reason": (
                    "Could not be allocated within the remaining "
                    "truck-capacity and driver-hours constraints"
                )
            })

    return {
        "status": "optimal",
        "fuel_price_per_liter": fuel_price,
        "average_speed_kmh": 50,
        "assignments": assignments,
        "unassigned_orders": unassigned_orders
    }
