from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def optimize_route(distance_matrix):
    """
    Optimize the visiting order of locations.

    distance_matrix:
        2D list where distance_matrix[i][j]
        represents the distance from location i to j.
    """

    # Create routing manager
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        1,
        0
    )

    # Create routing model
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(
        distance_callback
    )

    routing.SetArcCostEvaluatorOfAllVehicles(
        transit_callback_index
    )

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
            "status": "No route found",
            "route": [],
            "total_distance": 0
        }

    # Build route
    route = []
    total_distance = 0

    index = routing.Start(0)

    while not routing.IsEnd(index):

        node_index = manager.IndexToNode(index)
        route.append(node_index)

        previous_index = index

        index = solution.Value(
            routing.NextVar(index)
        )

        total_distance += routing.GetArcCostForVehicle(
            previous_index,
            index,
            0
        )

    # Add final destination
    route.append(
        manager.IndexToNode(index)
    )

    return {
        "status": "optimal",
        "route": route,
        "total_distance": total_distance
    }

