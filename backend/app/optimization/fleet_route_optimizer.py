from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
def optimize_fleet_routes(
    distance_matrix,
    orders,
    trucks,
    drivers
):
    """
    Optimize routes for multiple trucks while respecting
    each truck's capacity.
    """


    number_of_orders = len(orders)
    number_of_trucks = len(trucks)

    # if len(drivers) < number_of_trucks:
    #     return {
    #         "status": "insufficient_drivers",
    #         "message": (
    #             "Each truck needs a compatible driver "
    #             "before route optimization."
    #         ),
    #         "routes": []
    #     }

    for truck in trucks:
        if truck.capacity is None or float(truck.capacity) <= 0:
            return {
                "status": "invalid_truck_capacity",
                "message": (
                    f"Truck {truck.id} has missing or invalid capacity."
                ),
                "routes": []
            }

    for driver in drivers[:number_of_trucks]:
        if driver.working_hours is None or float(driver.working_hours) < 0:
            return {
                "status": "invalid_driver_hours",
                "message": (
                    f"Driver {driver.id} has invalid working hours."
                ),
                "routes": []
            }


    if number_of_orders == 0:
        return {
            "status": "no_orders",
            "routes": []
        }

    if number_of_trucks == 0:
        return {
            "status": "no_trucks",
            "routes": []
        }

    # Create routing manager
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        number_of_trucks,
        0
    )

    # Create routing model
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return distance_matrix[from_node][to_node]

    distance_callback_index = (
        routing.RegisterTransitCallback(
            distance_callback
        )
    )

    routing.SetArcCostEvaluatorOfAllVehicles(
        distance_callback_index
    )

    # Allow orders to remain unassigned when fleet
    # capacity is insufficient.
    penalty = 1_000_000

    for order_index in range(number_of_orders):
        index = manager.NodeToIndex(order_index + 1)
        routing.AddDisjunction([index], penalty)

    # Capacity callback
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)

        if from_node == 0:
            return 0

        order_index = from_node - 1

        if order_index < len(orders):
            return orders[order_index].weight or 0

        return 0

    demand_callback_index = (
        routing.RegisterUnaryTransitCallback(
            demand_callback
        )
    )

    # Each truck has its own capacity
    capacities = [
        truck.capacity
        for truck in trucks
    ]

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        capacities,
        True,
        "Capacity"
    )

    # # Limit each truck's route by its assigned driver's
    # # available driving hours.
    # # Distances in distance_matrix are hundredths of km.
    # def driving_distance_callback(from_index, to_index):
    #     from_node = manager.IndexToNode(from_index)
    #     to_node = manager.IndexToNode(to_index)
    #     return distance_matrix[from_node][to_node]

    # driving_callback_index = routing.RegisterTransitCallback(
    #     driving_distance_callback
    # )

    # # Each unit is 0.01 km; 50 km/h is the assumed speed.
    # max_driving_distances = [
    #     int(max(0, float(driver.working_hours or 0)) * 50 * 100)
    #     for driver in drivers
    # ]

    # routing.AddDimensionWithVehicleCapacity(
    #     driving_callback_index,
    #     0,
    #     max_driving_distances,
    #     True,
    #     "DrivingHours"
    # )


    # Search parameters
    search_parameters = (
        pywrapcp.DefaultRoutingSearchParameters()
    )

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve
    solution = routing.SolveWithParameters(
        search_parameters
    )

    if not solution:
        return {
            "status": "route_not_feasible",
            "message": (
                "No feasible fleet route found. "
                "Truck capacity may be insufficient."
            ),
            "routes": []
        }

    # Build routes
    routes = []

    for vehicle_id in range(number_of_trucks):

        index = routing.Start(vehicle_id)

        route = []
        route_distance = 0
        route_weight = 0

        while not routing.IsEnd(index):

            node_index = manager.IndexToNode(index)

            route.append(node_index)

            if node_index > 0:
                order_index = node_index - 1

                if order_index < len(orders):
                    route_weight += (
                        orders[order_index].weight or 0
                    )

            previous_index = index

            index = solution.Value(
                routing.NextVar(index)
            )

            route_distance += (
                routing.GetArcCostForVehicle(
                    previous_index,
                    index,
                    vehicle_id
                )
            )

        route.append(
            manager.IndexToNode(index)
        )

        # Only return trucks that actually received orders
        if len(route) > 2:
            routes.append({
                "truck_index": vehicle_id,
                "truck_id": trucks[vehicle_id].id,
                "route": route,
                "total_distance": route_distance / 100,
                "total_weight": route_weight
            })

    # Identify orders that were not assigned to any truck.
    assigned_order_indices = set()

    for route_data in routes:
        for location in route_data["route"]:
            if location > 0:
                assigned_order_indices.add(location - 1)

    unassigned_orders = [
        order.id
        for index, order in enumerate(orders)
        if index not in assigned_order_indices
    ]

    return {
        "status": "optimal",
        "routes": routes,
        "unassigned_order_ids": unassigned_orders
    }
