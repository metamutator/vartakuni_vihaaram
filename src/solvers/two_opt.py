"""2-Opt local search algorithm for TSP optimization."""

import networkx as nx
from typing import List, Tuple, Optional
from ..utils.tour import calculate_tour_cost, validate_tour, reverse_segment, calculate_swap_delta
from ..utils.metric import build_metric_closure


def improve_tour_2opt(
    tour: List[str],
    graph: nx.Graph,
    max_iterations: Optional[int] = None,
    improvement_threshold: float = 0.001,
    verbose: bool = False
) -> Tuple[List[str], float, float]:
    """
    Improve a TSP tour using 2-opt local search.

    The 2-opt algorithm iteratively improves a tour by reversing segments.
    For each pair of edges in the tour, it checks if swapping them reduces
    the total cost. The algorithm continues until no improvement is found
    or iteration limits are reached.

    Args:
        tour: Initial tour (list of station IDs in visit order)
        graph: NetworkX graph with edge weights (travel times)
        max_iterations: Maximum number of iterations before stopping.
                       If None, runs until no improvement is found.
        improvement_threshold: Minimum improvement (in minutes) to continue
                              iterating. Stops if improvement < threshold.
        verbose: If True, prints progress information

    Returns:
        Tuple of (improved_tour, original_cost, improved_cost)
        - improved_tour: Optimized tour
        - original_cost: Total cost of input tour
        - improved_cost: Total cost of output tour

    Raises:
        ValueError: If tour is invalid or doesn't match graph

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=1.0)
        >>> G.add_edge('B', 'C', weight=1.0)
        >>> G.add_edge('C', 'A', weight=1.0)
        >>> tour = ['A', 'B', 'C']
        >>> improved, orig, new = improve_tour_2opt(tour, G)
        >>> new <= orig
        True
    """
    # Use metric closure for consistent TSP edge availability
    closure = build_metric_closure(graph)
    validate_tour(tour, closure, require_complete=False)
    # Report original cost using original graph if possible to keep backward compatibility
    try:
        original_cost = calculate_tour_cost(tour, graph)
    except ValueError:
        original_cost = calculate_tour_cost(tour, closure)
    current_tour = tour.copy()
    current_cost = original_cost

    iteration = 0
    total_improvement = 0.0

    if verbose:
        print(f"Initial tour cost: {original_cost:.2f} minutes")

    while True:
        improved = False
        iteration += 1

        # Check iteration limit
        if max_iterations is not None and iteration > max_iterations:
            if verbose:
                print(f"Reached iteration limit: {max_iterations}")
            break

        # Try all possible 2-opt swaps
        n = len(current_tour)

        for i in range(n - 1):
            for j in range(i + 1, n):
                # Calculate the change in cost from this swap
                delta = calculate_swap_delta(current_tour, closure, i, j)

                # If improvement found, apply it
                if delta < -improvement_threshold:
                    current_tour = reverse_segment(current_tour, i, j)
                    current_cost += delta
                    total_improvement += abs(delta)
                    improved = True

                    if verbose:
                        print(
                            f"Iteration {iteration}: Improved by {abs(delta):.2f} min "
                            f"(swap [{i}, {j}]) -> Cost: {current_cost:.2f} min"
                        )

                    # Restart search after improvement
                    break

            if improved:
                break

        # If no improvement found, we've reached local optimum
        if not improved:
            if verbose:
                print(f"No more improvements found at iteration {iteration}")
            break

    if verbose:
        print(f"\nOptimization complete:")
        print(f"  Iterations: {iteration}")
        print(f"  Original cost: {original_cost:.2f} minutes")
        print(f"  Improved cost: {current_cost:.2f} minutes")
        print(f"  Total improvement: {total_improvement:.2f} minutes")
        print(f"  Percentage improvement: {(total_improvement/original_cost)*100:.2f}%")

    return current_tour, original_cost, current_cost


def improve_tour_2opt_fast(
    tour: List[str],
    graph: nx.Graph,
    max_iterations: Optional[int] = None,
    improvement_threshold: float = 0.001
) -> Tuple[List[str], float, float]:
    """
    Fast version of 2-opt that doesn't restart after each improvement.

    This version completes a full pass through all possible swaps before
    restarting, which can be faster but may find a slightly worse local optimum.

    Args:
        tour: Initial tour (list of station IDs)
        graph: NetworkX graph with edge weights
        max_iterations: Maximum number of passes through all swaps
        improvement_threshold: Minimum improvement to continue

    Returns:
        Tuple of (improved_tour, original_cost, improved_cost)
    """
    closure = build_metric_closure(graph)
    validate_tour(tour, closure, require_complete=False)
    try:
        original_cost = calculate_tour_cost(tour, graph)
    except ValueError:
        original_cost = calculate_tour_cost(tour, closure)
    current_tour = tour.copy()
    current_cost = original_cost

    iteration = 0

    while True:
        improved = False
        iteration += 1

        # Check iteration limit
        if max_iterations is not None and iteration > max_iterations:
            break

        # Try all possible 2-opt swaps in one pass
        n = len(current_tour)
        best_delta = 0
        best_i = None
        best_j = None

        for i in range(n - 1):
            for j in range(i + 1, n):
                # Calculate the change in cost from this swap
                delta = calculate_swap_delta(current_tour, closure, i, j)

                # Track best improvement
                if delta < best_delta:
                    best_delta = delta
                    best_i = i
                    best_j = j

        # Apply best improvement if found
        if best_delta < -improvement_threshold:
            current_tour = reverse_segment(current_tour, best_i, best_j)
            current_cost += best_delta
            improved = True

        # If no improvement found, we've reached local optimum
        if not improved:
            break

    return current_tour, original_cost, current_cost
