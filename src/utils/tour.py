def rotate_tour_to_start(tour: List[str], start_station: str) -> List[str]:
    """
    Rotate a TSP tour (cycle) so that it starts at the specified station.

    Args:
        tour: List of station IDs representing the tour (cycle)
        start_station: Station ID to rotate the tour to start from

    Returns:
        Rotated tour list starting at start_station (if present), else original tour
    """
    if not tour:
        return tour
    try:
        idx = tour.index(start_station)
        return tour[idx:] + tour[:idx]
    except ValueError:
        # start_station not in tour; return as is
        return tour
"""Utility functions for TSP tour manipulation and evaluation."""

import networkx as nx
from typing import List, Tuple


def calculate_tour_cost(tour: List[str], graph: nx.Graph) -> float:
    """
    Calculate the total cost (travel time) of a tour.

    Args:
        tour: List of station IDs representing the tour order
        graph: NetworkX graph with edge weights

    Returns:
        Total travel time in minutes for the complete tour

    Raises:
        ValueError: If tour is invalid or edges don't exist
    """
    if not tour:
        raise ValueError("Tour cannot be empty")

    if len(tour) < 2:
        raise ValueError("Tour must have at least 2 stations")

    total_cost = 0.0

    # Calculate cost for each consecutive pair
    for i in range(len(tour)):
        current = tour[i]
        next_station = tour[(i + 1) % len(tour)]  # Wrap around to form cycle

        # Check if edge exists
        if not graph.has_edge(current, next_station):
            raise ValueError(
                f"No connection exists between {current} and {next_station}"
            )

        # Get edge weight (travel time)
        edge_data = graph[current][next_station]
        weight = edge_data.get('weight')

        if weight is None:
            raise ValueError(
                f"Edge ({current}, {next_station}) has no weight attribute"
            )

        total_cost += weight

    return total_cost


def validate_tour(tour: List[str], graph: nx.Graph, require_complete: bool = True) -> None:
    """
    Validate that a tour is valid for the given graph.

    Args:
        tour: List of station IDs representing the tour
        graph: NetworkX graph
        require_complete: Whether tour must visit all nodes in graph

    Raises:
        ValueError: If tour is invalid
    """
    if not tour:
        raise ValueError("Tour cannot be empty")

    # Check for duplicate stations
    if len(tour) != len(set(tour)):
        duplicates = [s for s in tour if tour.count(s) > 1]
        raise ValueError(f"Tour contains duplicate stations: {set(duplicates)}")

    # Check that all stations exist in graph
    tour_nodes = set(tour)
    graph_nodes = set(graph.nodes())

    invalid_stations = tour_nodes - graph_nodes
    if invalid_stations:
        raise ValueError(f"Tour contains invalid stations: {invalid_stations}")

    # Check if tour visits all stations (for complete TSP solution)
    if require_complete:
        missing_stations = graph_nodes - tour_nodes
        if missing_stations:
            raise ValueError(
                f"Tour incomplete: missing {len(missing_stations)} stations"
            )

    # Check that all edges exist
    for i in range(len(tour)):
        current = tour[i]
        next_station = tour[(i + 1) % len(tour)]

        if not graph.has_edge(current, next_station):
            raise ValueError(
                f"No connection exists between {current} and {next_station}"
            )


def reverse_segment(tour: List[str], i: int, j: int) -> List[str]:
    """
    Reverse a segment of the tour between indices i and j (inclusive).

    This is the core operation in 2-opt: reversing a segment of the tour
    to potentially improve the solution.

    Args:
        tour: Original tour
        i: Start index of segment to reverse
        j: End index of segment to reverse

    Returns:
        New tour with reversed segment

    Example:
        >>> tour = ['A', 'B', 'C', 'D', 'E']
        >>> reverse_segment(tour, 1, 3)
        ['A', 'D', 'C', 'B', 'E']
    """
    if i < 0 or j >= len(tour) or i >= j:
        raise ValueError(f"Invalid indices: i={i}, j={j} for tour of length {len(tour)}")

    # Create new tour with reversed segment
    new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
    return new_tour


def calculate_swap_delta(
    tour: List[str],
    graph: nx.Graph,
    i: int,
    j: int
) -> float:
    """
    Calculate the change in tour cost from reversing segment [i, j].

    This is an optimized version that only recalculates affected edges
    rather than the entire tour cost.

    Args:
        tour: Current tour
        graph: NetworkX graph with edge weights
        i: Start index of segment
        j: End index of segment

    Returns:
        Delta (change in cost): negative means improvement
    """
    n = len(tour)

    if i < 0 or j >= n or i >= j:
        raise ValueError(f"Invalid indices: i={i}, j={j} for tour of length {n}")

    # Get the four affected edges:
    # Before: (i-1)-->(i) and (j)-->(j+1)
    # After:  (i-1)-->(j) and (i)-->(j+1)

    # Nodes involved
    prev_i = tour[(i - 1) % n]
    node_i = tour[i]
    node_j = tour[j]
    next_j = tour[(j + 1) % n]

    # Special case: if reversing entire tour, no change
    if (j - i + 1) == n:
        return 0.0

    # Get current edge weights
    try:
        old_cost = (
            graph[prev_i][node_i]['weight'] +
            graph[node_j][next_j]['weight']
        )

        # Get new edge weights after reversal
        new_cost = (
            graph[prev_i][node_j]['weight'] +
            graph[node_i][next_j]['weight']
        )

        return new_cost - old_cost

    except KeyError as e:
        raise ValueError(f"Missing edge in graph: {e}")
