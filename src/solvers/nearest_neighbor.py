"""Nearest Neighbor heuristic for TSP initial solution construction.

This implementation accounts for the fact that the metro network graph is
not a complete graph and generally does not admit a Hamiltonian cycle using
only the original track + walking-transfer edges (leaf branches force
revisits). For TSP heuristics we therefore operate on the metric closure of
the original graph: a complete graph whose edge weights are the shortest
path travel times between stations. The returned tour is an ordering of
stations (each exactly once) together with its total travel time under the
shortest-path metric.

NOTE: Validation and cost computation are performed against the metric
closure, not the sparse original graph. Downstream local search (e.g. 2-opt)
should likewise use the metric closure for consistency.
"""

import networkx as nx
from typing import List, Tuple, Optional, Set
from ..utils.tour import calculate_tour_cost, validate_tour
from ..utils.metric import build_metric_closure


def nearest_neighbor_tsp(
    graph: nx.Graph,
    start_station: Optional[str] = None,
    validate_result: bool = True
) -> Tuple[List[str], float]:
    """
    Construct a TSP tour using the Nearest Neighbor greedy heuristic.

    The algorithm starts at a given station and repeatedly visits the nearest
    unvisited station until all stations have been visited, then returns to
    the starting station.

    This is a constructive heuristic that quickly generates a reasonable
    (though not optimal) initial solution that can be improved with local
    search methods like 2-opt.

    Args:
        graph: NetworkX graph with edge weights (travel times)
        start_station: Starting station ID. If None, uses first node in graph.
        validate_result: Whether to validate the resulting tour

    Returns:
        Tuple of (tour, total_cost)
        - tour: Ordered list of station IDs
        - total_cost: Total travel time in minutes

    Raises:
        ValueError: If graph is empty or start_station is invalid
        ValueError: If graph is not connected (no valid tour possible)

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=1.0)
        >>> G.add_edge('B', 'C', weight=2.0)
        >>> G.add_edge('C', 'A', weight=3.0)
        >>> tour, cost = nearest_neighbor_tsp(G, start_station='A')
        >>> len(tour)
        3
        >>> set(tour) == {'A', 'B', 'C'}
        True
    """
    # Validate graph
    if graph.number_of_nodes() == 0:
        raise ValueError("Graph is empty")

    # Set starting station
    if start_station is None:
        start_station = list(graph.nodes())[0]
    elif start_station not in graph.nodes():
        raise ValueError(f"Start station '{start_station}' not in graph")

    # Check if graph is connected
    if not nx.is_connected(graph):
        raise ValueError(
            "Graph is not connected - cannot create a tour visiting all stations"
        )

    # Metric closure (complete graph of shortest-path travel times)
    closure = build_metric_closure(graph)
    nodes = list(closure.nodes())

    # Initialize tour with starting station
    tour = [start_station]
    unvisited: Set[str] = set(nodes) - {start_station}
    current_station = start_station

    # Greedily select nearest station using metric closure
    while unvisited:
        nearest_station = None
        min_distance = float('inf')

        for candidate in unvisited:
            distance = closure[current_station][candidate]['weight']
            if distance < min_distance:
                min_distance = distance
                nearest_station = candidate

        # Safety check (should never happen with closure)
        if nearest_station is None:
            raise ValueError(
                f"Unexpected: could not select next station from {current_station}."
            )

        tour.append(nearest_station)
        unvisited.remove(nearest_station)
        current_station = nearest_station

    # Calculate total tour cost using closure graph
    if len(tour) == 1:
        total_cost = 0.0
    else:
        total_cost = calculate_tour_cost(tour, closure)

    # Validate result against closure (ensures completeness & no duplicates)
    if validate_result and len(tour) > 1:
        validate_tour(tour, closure, require_complete=True)

    return tour, total_cost


def nearest_neighbor_multi_start(
    graph: nx.Graph,
    num_starts: Optional[int] = None,
    start_stations: Optional[List[str]] = None
) -> Tuple[List[str], float, str]:
    """
    Run Nearest Neighbor from multiple starting points and return the best tour.

    This can help overcome the greedy nature of the Nearest Neighbor heuristic
    by trying different starting positions.

    Args:
        graph: NetworkX graph with edge weights
        num_starts: Number of random starting points to try.
                   Ignored if start_stations is provided.
        start_stations: Specific list of starting stations to try.
                       If None, tries num_starts random stations.

    Returns:
        Tuple of (best_tour, best_cost, best_start_station)
        - best_tour: Best tour found
        - best_cost: Cost of best tour
        - best_start_station: Starting station that produced best tour

    Raises:
        ValueError: If graph is empty or parameters are invalid

    Example:
        >>> G = nx.complete_graph(5)
        >>> for u, v in G.edges():
        ...     G[u][v]['weight'] = 1.0
        >>> tour, cost, start = nearest_neighbor_multi_start(G, num_starts=3)
        >>> len(tour) == 5
        True
    """
    if graph.number_of_nodes() == 0:
        raise ValueError("Graph is empty")

    # Determine which starting stations to try
    if start_stations is not None:
        # Use provided list
        stations_to_try = start_stations
        # Validate all stations exist
        for station in stations_to_try:
            if station not in graph.nodes():
                raise ValueError(f"Station '{station}' not in graph")
    else:
        # Use num_starts random stations
        if num_starts is None:
            num_starts = min(10, graph.number_of_nodes())

        all_stations = list(graph.nodes())
        if num_starts > len(all_stations):
            num_starts = len(all_stations)

        # Try first num_starts stations (deterministic)
        stations_to_try = all_stations[:num_starts]

    # Try each starting station
    best_tour = None
    best_cost = float('inf')
    best_start = None

    for start_station in stations_to_try:
        try:
            tour, cost = nearest_neighbor_tsp(graph, start_station=start_station)

            if cost < best_cost:
                best_cost = cost
                best_tour = tour
                best_start = start_station

        except ValueError:
            # Skip stations that don't lead to valid tours
            continue

    if best_tour is None:
        raise ValueError("Could not find any valid tour")

    return best_tour, best_cost, best_start


def nearest_neighbor_with_2opt(
    graph: nx.Graph,
    start_station: Optional[str] = None,
    max_iterations: Optional[int] = None,
    improvement_threshold: float = 0.001,
    verbose: bool = False
) -> Tuple[List[str], float, float]:
    """
    Construct a tour with Nearest Neighbor and improve it with 2-opt.

    This combines the construction heuristic with local search optimization
    to produce better solutions.

    Args:
        graph: NetworkX graph with edge weights
        start_station: Starting station for Nearest Neighbor
        max_iterations: Max 2-opt iterations
        improvement_threshold: Min improvement for 2-opt to continue
        verbose: Print progress information

    Returns:
        Tuple of (optimized_tour, initial_cost, optimized_cost)

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=1.0)
        >>> G.add_edge('B', 'C', weight=1.0)
        >>> G.add_edge('C', 'A', weight=1.0)
        >>> tour, init_cost, final_cost = nearest_neighbor_with_2opt(G)
        >>> final_cost <= init_cost
        True
    """
    from .two_opt import improve_tour_2opt

    # Generate initial solution with Nearest Neighbor
    if verbose:
        print("Generating initial tour with Nearest Neighbor...")

    initial_tour, initial_cost = nearest_neighbor_tsp(
        graph, start_station=start_station
    )

    if verbose:
        print(f"Initial tour cost: {initial_cost:.2f} minutes")
        print("Optimizing with 2-opt...")

    # Improve with 2-opt
    optimized_tour, _, optimized_cost = improve_tour_2opt(
        initial_tour,
        graph,
        max_iterations=max_iterations,
        improvement_threshold=improvement_threshold,
        verbose=verbose
    )

    if verbose:
        improvement = initial_cost - optimized_cost
        pct_improvement = (improvement / initial_cost) * 100
        print("\nFinal Results:")
        print(f"  Initial cost: {initial_cost:.2f} minutes")
        print(f"  Optimized cost: {optimized_cost:.2f} minutes")
        print(f"  Improvement: {improvement:.2f} minutes ({pct_improvement:.2f}%)")

    return optimized_tour, initial_cost, optimized_cost
