from ortools.linear_solver import pywraplp
from datetime import datetime


def optimize_loads_v3(trucks, orders, fuel_price=90):

    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        raise RuntimeError("OR-Tools solver could not be created")

    x = {}

    for truck in trucks:
        for order in orders:
            x[truck.id, order.id] = solver.IntVar(
                0,
                1,
                f"x_{truck.id}_{order.id}"
            )

    truck_used = {}

    for truck in trucks:
        truck_used[truck.id] = solver.IntVar(
            0,
            1,
            f"truck_used_{truck.id}"
        )

    # ------------------------------------------------
    # 1. Every order must be assigned to one truck
    # ------------------------------------------------

    for order in orders:
        solver.Add(
            sum(
                x[truck.id, order.id]
                for truck in trucks
            ) == 1
        )

    # ------------------------------------------------
    # 2. Truck capacity constraint
    # ------------------------------------------------

    for truck in trucks:
        solver.Add(
            sum(
                order.weight * x[truck.id, order.id]
                for order in orders
            )
            <= truck.capacity * truck_used[truck.id]
        )

    # ------------------------------------------------
    # 3. Objective
    # ------------------------------------------------

    objective_terms = []

    for truck in trucks:

        # Penalty for using another truck
        objective_terms.append(
            10000 * truck_used[truck.id]
        )

        for order in orders:

            # Fuel cost
            if (
                truck.fuel_efficiency
                and truck.fuel_efficiency > 0
            ):
                fuel_cost = (
                    order.distance_km
                    / truck.fuel_efficiency
                    * fuel_price
                )
            else:
                fuel_cost = 100000

            # Deadline information
            try:
                deadline = datetime.strptime(
                    order.deadline,
                    "%Y-%m-%d %H:%M"
                )

                deadline_hour = deadline.hour

            except (ValueError, TypeError):
                deadline_hour = 23

            # Earlier deadline = higher priority
            deadline_penalty = (24 - deadline_hour) * 100

            total_cost = (
                fuel_cost
                + deadline_penalty
            )

            objective_terms.append(
                total_cost * x[truck.id, order.id]
            )

    solver.Minimize(
        sum(objective_terms)
    )

    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        return {
            "status": "No optimal solution found",
            "assignments": []
        }

    assignments = []

    for truck in trucks:

        assigned_orders = []

        for order in orders:

            if x[
                truck.id,
                order.id
            ].solution_value() > 0.5:

                if (
                    truck.fuel_efficiency
                    and truck.fuel_efficiency > 0
                ):
                    fuel_used = (
                        order.distance_km
                        / truck.fuel_efficiency
                    )
                else:
                    fuel_used = 0

                fuel_cost = (
                    fuel_used * fuel_price
                )

                assigned_orders.append({
                    "order_id": order.id,
                    "weight": order.weight,
                    "distance_km": order.distance_km,
                    "deadline": order.deadline,
                    "fuel_used_liters": round(
                        fuel_used,
                        2
                    ),
                    "fuel_cost": round(
                        fuel_cost,
                        2
                    )
                })

        if assigned_orders:

            total_weight = sum(
                order["weight"]
                for order in assigned_orders
            )

            total_fuel_cost = sum(
                order["fuel_cost"]
                for order in assigned_orders
            )

            assignments.append({
                "truck_id": truck.id,
                "truck_capacity": truck.capacity,
                "total_weight": total_weight,
                "utilization_percentage": round(
                    (
                        total_weight
                        / truck.capacity
                    ) * 100,
                    2
                ),
                "total_fuel_cost": round(
                    total_fuel_cost,
                    2
                ),
                "orders": assigned_orders
            })

    return {
        "status": "optimal",
        "fuel_price_per_liter": fuel_price,
        "assignments": assignments
    }