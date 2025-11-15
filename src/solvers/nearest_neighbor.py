#!/usr/bin/env python3
"""
Nearest Neighbor Heuristic for TSP (US-301)

Implements a greedy nearest neighbor algorithm to generate baseline TSP solutions.
Always visits the nearest unvisited station until all stations are visited.
"""

import time
from typing import List, Tuple, Set
import networkx as nx


def nearest_neighbor_tsp(
    graph: nx.Graph,
    start_station: str
) -> Tuple[List[str], float]:
    """
    Solve TSP using Nearest Neighbor heuristic.

    Algorithm:
    1. Start at the given station
    2. Repeatedly visit the nearest unvisited neighbor
    3. Return to starting station when all nodes are visited

    Args:
        graph: NetworkX graph with stations as nodes and 'weight' attribute on edges
        start_station: Station ID to start the tour

    Returns:
        Tuple of (tour, total_time):
        - tour: Ordered list of station IDs forming the complete tour
        - total_time: Total travel time in minutes

    Raises:
        ValueError: If start_station not in graph or graph is empty

    Time Complexity: O(n^2) where n is number of stations
    Space Complexity: O(n)
    """
    # Validate inputs
    if not graph or graph.number_of_nodes() == 0:
        raise ValueError("Graph is empty")

    if start_station not in graph:
        raise ValueError(f"Start station '{start_station}' not found in graph")

    # Initialize
    tour = [start_station]
    visited: Set[str] = {start_station}
    current_station = start_station
    total_time = 0.0

    # Greedy nearest neighbor selection
    num_stations = graph.number_of_nodes()

    while len(visited) < num_stations:
        # Find nearest unvisited neighbor
        nearest_station = None
        min_time = float('inf')

        for neighbor in graph.neighbors(current_station):
            if neighbor not in visited:
                edge_data = graph[current_station][neighbor]
                travel_time = edge_data.get('weight', 0)

                if travel_time < min_time:
                    min_time = travel_time
                    nearest_station = neighbor

        # Handle disconnected graph (shouldn't happen with validated data)
        if nearest_station is None:
            # Find any unvisited station and connect via shortest path
            unvisited = set(graph.nodes()) - visited
            if unvisited:
                # Find closest unvisited via shortest path
                min_path_length = float('inf')
                closest_unvisited = None

                for unvisited_station in unvisited:
                    try:
                        path_length = nx.shortest_path_length(
                            graph, current_station, unvisited_station, weight='weight'
                        )
                        if path_length < min_path_length:
                            min_path_length = path_length
                            closest_unvisited = unvisited_station
                    except nx.NetworkXNoPath:
                        continue

                if closest_unvisited:
                    # Add path to tour
                    path = nx.shortest_path(
                        graph, current_station, closest_unvisited, weight='weight'
                    )
                    # Add intermediate nodes
                    for i in range(1, len(path)):
                        if path[i] not in visited:
                            tour.append(path[i])
                            visited.add(path[i])
                            # Add edge weight
                            edge_data = graph[path[i-1]][path[i]]
                            total_time += edge_data.get('weight', 0)
                    current_station = closest_unvisited
                    continue
                else:
                    raise ValueError("Graph is disconnected and no path exists to unvisited stations")
            else:
                break

        # Move to nearest neighbor
        tour.append(nearest_station)
        visited.add(nearest_station)
        total_time += min_time
        current_station = nearest_station

    # Return to starting station to complete the tour
    if current_station != start_station:
        try:
            edge_data = graph[current_station][start_station]
            return_time = edge_data.get('weight', 0)
            total_time += return_time
        except KeyError:
            # If no direct edge, find shortest path back
            try:
                path_length = nx.shortest_path_length(
                    graph, current_station, start_station, weight='weight'
                )
                total_time += path_length
            except nx.NetworkXNoPath:
                pass  # Single node or disconnected, no return needed

    # Always close the loop
    tour.append(start_station)

    return tour, total_time


def nearest_neighbor_tsp_with_stats(
    graph: nx.Graph,
    start_station: str
) -> Tuple[List[str], float, dict]:
    """
    Solve TSP using Nearest Neighbor and return additional statistics.

    Args:
        graph: NetworkX graph
        start_station: Starting station ID

    Returns:
        Tuple of (tour, total_time, stats):
        - tour: Ordered list of station IDs
        - total_time: Total travel time in minutes
        - stats: Dictionary with computation_time_seconds, num_stations
    """
    start_time = time.time()
    tour, total_time = nearest_neighbor_tsp(graph, start_station)
    computation_time = time.time() - start_time

    stats = {
        'computation_time_seconds': computation_time,
        'num_stations': graph.number_of_nodes(),
        'algorithm': 'Nearest Neighbor',
        'deterministic': True
    }

    return tour, total_time, stats
