"""Simulated Annealing solver for TSP optimization."""

import networkx as nx
import random
import math
from typing import List, Tuple, Optional, Callable
from ..utils.tour import calculate_tour_cost, validate_tour, reverse_segment


def linear_cooling(initial_temp: float, current_iteration: int, max_iterations: int) -> float:
    """
    Linear cooling schedule.

    Args:
        initial_temp: Starting temperature
        current_iteration: Current iteration number
        max_iterations: Total number of iterations

    Returns:
        Current temperature
    """
    return initial_temp * (1 - current_iteration / max_iterations)


def exponential_cooling(initial_temp: float, current_iteration: int, alpha: float = 0.95) -> float:
    """
    Exponential cooling schedule.

    Args:
        initial_temp: Starting temperature
        current_iteration: Current iteration number
        alpha: Cooling rate (0 < alpha < 1)

    Returns:
        Current temperature
    """
    return initial_temp * (alpha ** current_iteration)


def logarithmic_cooling(initial_temp: float, current_iteration: int) -> float:
    """
    Logarithmic cooling schedule.

    Args:
        initial_temp: Starting temperature
        current_iteration: Current iteration number

    Returns:
        Current temperature
    """
    return initial_temp / (1 + math.log(1 + current_iteration))


def generate_neighbor_2opt(tour: List[str]) -> Tuple[List[str], int, int]:
    """
    Generate a random neighbor using a single 2-opt swap.

    Args:
        tour: Current tour

    Returns:
        Tuple of (neighbor_tour, i, j) where i and j are the swap indices
    """
    n = len(tour)

    # Randomly select two positions
    i = random.randint(0, n - 2)
    j = random.randint(i + 1, n - 1)

    # Reverse segment between i and j
    neighbor = reverse_segment(tour, i, j)

    return neighbor, i, j


def simulated_annealing_tsp(
    graph: nx.Graph,
    initial_tour: Optional[List[str]] = None,
    initial_temp: float = 100.0,
    max_iterations: int = 10000,
    cooling_schedule: str = 'exponential',
    cooling_alpha: float = 0.95,
    random_seed: Optional[int] = None,
    verbose: bool = False
) -> Tuple[List[str], float, List[float]]:
    """
    Solve TSP using Simulated Annealing.

    Simulated Annealing is a probabilistic optimization technique that:
    1. Starts with an initial solution (tour)
    2. Iteratively generates random neighbors
    3. Accepts improving moves always
    4. Accepts worsening moves with probability based on temperature
    5. Gradually decreases temperature (cooling) to converge

    This allows the algorithm to escape local optima and explore the solution
    space more thoroughly than greedy methods like 2-opt.

    Args:
        graph: NetworkX graph with edge weights
        initial_tour: Starting tour. If None, generates random tour.
        initial_temp: Starting temperature (higher = more exploration)
        max_iterations: Number of iterations to run
        cooling_schedule: 'linear', 'exponential', or 'logarithmic'
        cooling_alpha: Cooling rate for exponential schedule (0 < alpha < 1)
        random_seed: Random seed for reproducibility
        verbose: Print progress information

    Returns:
        Tuple of (best_tour, best_cost, cost_history)
        - best_tour: Best tour found
        - best_cost: Cost of best tour
        - cost_history: List of costs at each iteration

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=1.0)
        >>> G.add_edge('B', 'C', weight=1.0)
        >>> G.add_edge('C', 'A', weight=1.0)
        >>> tour, cost, history = simulated_annealing_tsp(G)
        >>> len(tour) == 3
        True
    """
    # Set random seed for reproducibility
    if random_seed is not None:
        random.seed(random_seed)

    # Generate initial tour if not provided
    if initial_tour is None:
        # Create random tour
        nodes = list(graph.nodes())
        random.shuffle(nodes)
        current_tour = nodes
    else:
        current_tour = initial_tour.copy()

    # Validate initial tour
    validate_tour(current_tour, graph, require_complete=False)

    # Calculate initial cost
    current_cost = calculate_tour_cost(current_tour, graph)

    # Track best solution
    best_tour = current_tour.copy()
    best_cost = current_cost

    # Track cost history
    cost_history = [current_cost]

    if verbose:
        print(f"Simulated Annealing Starting:")
        print(f"  Initial cost: {current_cost:.2f} minutes")
        print(f"  Initial temperature: {initial_temp:.2f}")
        print(f"  Max iterations: {max_iterations}")
        print(f"  Cooling schedule: {cooling_schedule}")

    # Simulated Annealing main loop
    accepted = 0
    rejected = 0

    for iteration in range(max_iterations):
        # Calculate current temperature
        if cooling_schedule == 'linear':
            temp = linear_cooling(initial_temp, iteration, max_iterations)
        elif cooling_schedule == 'exponential':
            temp = exponential_cooling(initial_temp, iteration, cooling_alpha)
        elif cooling_schedule == 'logarithmic':
            temp = logarithmic_cooling(initial_temp, iteration)
        else:
            raise ValueError(f"Unknown cooling schedule: {cooling_schedule}")

        # Prevent temperature from going to zero (can cause division issues)
        temp = max(temp, 0.01)

        # Generate random neighbor
        neighbor_tour, i, j = generate_neighbor_2opt(current_tour)
        neighbor_cost = calculate_tour_cost(neighbor_tour, graph)

        # Calculate cost difference
        delta = neighbor_cost - current_cost

        # Decide whether to accept the neighbor
        if delta < 0:
            # Improvement: always accept
            current_tour = neighbor_tour
            current_cost = neighbor_cost
            accepted += 1

            # Update best if improved
            if current_cost < best_cost:
                best_tour = current_tour.copy()
                best_cost = current_cost

                if verbose and iteration % 1000 == 0:
                    print(f"  Iter {iteration}: New best = {best_cost:.2f} min (T={temp:.2f})")
        else:
            # Worsening move: accept with probability
            acceptance_prob = math.exp(-delta / temp)

            if random.random() < acceptance_prob:
                # Accept worsening move
                current_tour = neighbor_tour
                current_cost = neighbor_cost
                accepted += 1
            else:
                rejected += 1

        # Record cost history
        cost_history.append(current_cost)

    if verbose:
        print(f"\nSimulated Annealing Complete:")
        print(f"  Best cost: {best_cost:.2f} minutes")
        print(f"  Final current cost: {current_cost:.2f} minutes")
        print(f"  Moves accepted: {accepted} ({100*accepted/(accepted+rejected):.1f}%)")
        print(f"  Moves rejected: {rejected} ({100*rejected/(accepted+rejected):.1f}%)")

    return best_tour, best_cost, cost_history


def simulated_annealing_adaptive(
    graph: nx.Graph,
    initial_tour: Optional[List[str]] = None,
    target_time_seconds: float = 30.0,
    random_seed: Optional[int] = None,
    verbose: bool = False
) -> Tuple[List[str], float, List[float]]:
    """
    Simulated Annealing with adaptive parameters based on target time.

    Automatically adjusts iterations and initial temperature based on graph size
    and target computation time.

    Args:
        graph: NetworkX graph with edge weights
        initial_tour: Starting tour
        target_time_seconds: Target computation time
        random_seed: Random seed for reproducibility
        verbose: Print progress information

    Returns:
        Tuple of (best_tour, best_cost, cost_history)
    """
    import time

    # Adaptive parameters based on graph size
    n = graph.number_of_nodes()

    # Estimate iterations based on target time
    # Rough estimate: can do ~1000-5000 iterations per second
    max_iterations = int(target_time_seconds * 2000)

    # Initial temperature based on average edge weight
    avg_edge_weight = sum(d['weight'] for u, v, d in graph.edges(data=True)) / graph.number_of_edges()
    initial_temp = avg_edge_weight * n * 0.1  # Heuristic

    if verbose:
        print(f"Adaptive SA parameters:")
        print(f"  Graph size: {n} nodes")
        print(f"  Target time: {target_time_seconds}s")
        print(f"  Max iterations: {max_iterations}")
        print(f"  Initial temp: {initial_temp:.2f}")

    start_time = time.time()

    result = simulated_annealing_tsp(
        graph,
        initial_tour=initial_tour,
        initial_temp=initial_temp,
        max_iterations=max_iterations,
        cooling_schedule='exponential',
        random_seed=random_seed,
        verbose=verbose
    )

    elapsed = time.time() - start_time

    if verbose:
        print(f"\nActual computation time: {elapsed:.2f}s")

    return result
