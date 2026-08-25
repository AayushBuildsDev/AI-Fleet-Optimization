from ortools.linear_solver import pywraplp


def optimize_loads_v4(trucks, drivers, orders, fuel_price=90):
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        raise RuntimeError("OR-Tools solver could not be created")

    # ------------------------------------------------
    # Decision variable:
    # x[truck, driver, order] = 1 if this combination
    # is selected
    # ------------------------------------------------

    x = {}

    for truck in trucks:
        for driver in drivers:
            for order in orders:
                x[truck.id, driver.id, order.id] = solver.IntVar(
                    0,
                    1,
                    f"x_{truck.id}_{driver.id}_{order.id}"
                )

    # ------------------------------------------------
    # 1. Every order must be assigned exactly once
    # ------------------------------------------------

    for order in orders:
        solver.Add(
            sum(
                x[truck.id, driver.id, order.id]
                for truck in trucks
                for driver in drivers
            ) == 1
        )

    # ------------------------------------------------
    # 2. Truck capacity constraint
    # ------------------------------------------------

    for truck in trucks:
        solver.Add(
            sum(
                order.weight * x[truck.id, driver.id, order.id]
                for driver in drivers
                for order in orders
            )
            <= truck.capacity
        )

    # ------------------------------------------------
    # 3. Driver working-hours constraint
    #
    # Average speed = 50 km/h
    #
    # Driving time = distance / 50
    # ------------------------------------------------

    for driver in drivers:

        total_driving_hours = sum(
            (
                order.distance_km / 50
            ) * x[truck.id, driver.id, order.id]
            for truck in trucks
            for order in orders
        )

        solver.Add(
            total_driving_hours
            <= driver.working_hours
        )

    # ------------------------------------------------
    # 4. Objective
    #
    # Minimize fuel cost
    # ------------------------------------------------

    objective_terms = []

    for truck in trucks:

        for driver in drivers:

            for order in orders:

                # Fuel calculation
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

                objective_terms.append(
                    fuel_cost
                    * x[truck.id, driver.id, order.id]
                )

    solver.Minimize(
        sum(objective_terms)
    )

    # ------------------------------------------------
    # Solve
    # ------------------------------------------------

    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        return {
            "status": "No optimal solution found",
            "assignments": []
        }

    # ------------------------------------------------
    # Build result
    # ------------------------------------------------

    assignments = []

    for truck in trucks:

        for driver in drivers:

            assigned_orders = []

            for order in orders:

                if (
                    x[
                        truck.id,
                        driver.id,
                        order.id
                    ].solution_value() > 0.5
                ):

                    driving_hours = (
                        order.distance_km / 50
                    )

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
                        "estimated_driving_hours": round(
                            driving_hours,
                            2
                        ),
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

                total_driving_hours = sum(
                    order["estimated_driving_hours"]
                    for order in assigned_orders
                )

                assignments.append({
                    "truck_id": truck.id,
                    "driver_id": driver.id,
                    "truck_capacity": truck.capacity,
                    "total_weight": total_weight,
                    "utilization_percentage": round(
                        (
                            total_weight
                            / truck.capacity
                        ) * 100,
                        2
                    ),
                    "driver_working_hours": driver.working_hours,
                    "total_driving_hours": round(
                        total_driving_hours,
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
        "average_speed_kmh": 50,
        "assignments": assignments
    }