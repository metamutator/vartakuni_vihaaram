"""Genetic Algorithm solver for TSP optimization."""

import networkx as nx
import random
from typing import List, Tuple, Optional
from ..utils.tour import calculate_tour_cost, validate_tour, reverse_segment
from ..utils.metric import build_metric_closure


def order_crossover(parent1: List[str], parent2: List[str]) -> List[str]:
    """
    Order Crossover (OX) operator for TSP tours.

    Preserves relative order of cities from parents while ensuring valid tour.

    Args:
        parent1: First parent tour
        parent2: Second parent tour

    Returns:
        Child tour

    Example:
        >>> p1 = ['A', 'B', 'C', 'D', 'E']
        >>> p2 = ['C', 'D', 'A', 'E', 'B']
        >>> child = order_crossover(p1, p2)
        >>> len(child) == len(p1)
        True
        >>> set(child) == set(p1)
        True
    """
    n = len(parent1)

    # Select random substring from parent1
    start = random.randint(0, n - 2)
    end = random.randint(start + 1, n)

    # Copy substring from parent1
    child = [None] * n
    child[start:end] = parent1[start:end]

    # Fill remaining positions with cities from parent2 in order
    parent2_idx = 0
    for i in range(n):
        if child[i] is None:
            # Find next city from parent2 not already in child
            while parent2[parent2_idx] in child:
                parent2_idx += 1

            child[i] = parent2[parent2_idx]
            parent2_idx += 1

    return child


def pmx_crossover(parent1: List[str], parent2: List[str]) -> List[str]:
    """
    Partially Mapped Crossover (PMX) for TSP tours.

    Creates mapping between two parents and resolves conflicts.

    Args:
        parent1: First parent tour
        parent2: Second parent tour

    Returns:
        Child tour
    """
    n = len(parent1)

    # Select random crossover points
    cx_point1 = random.randint(0, n - 2)
    cx_point2 = random.randint(cx_point1 + 1, n)

    # Initialize child with None
    child = [None] * n

    # Copy segment from parent1
    child[cx_point1:cx_point2] = parent1[cx_point1:cx_point2]

    # Create mapping from parent2 segment
    for i in range(cx_point1, cx_point2):
        if parent2[i] not in child:
            # Find position to insert parent2[i]
            pos = i
            while child[pos] is not None:
                # Follow mapping chain
                pos = parent2.index(parent1[pos])

            child[pos] = parent2[i]

    # Fill remaining positions from parent2
    for i in range(n):
        if child[i] is None:
            child[i] = parent2[i]

    return child


def swap_mutation(tour: List[str]) -> List[str]:
    """
    Swap mutation: exchange two random cities.

    Args:
        tour: Tour to mutate

    Returns:
        Mutated tour
    """
    mutated = tour.copy()
    i, j = random.sample(range(len(tour)), 2)
    mutated[i], mutated[j] = mutated[j], mutated[i]
    return mutated


def reverse_mutation(tour: List[str]) -> List[str]:
    """
    Reverse mutation: reverse a random segment (2-opt move).

    Args:
        tour: Tour to mutate

    Returns:
        Mutated tour
    """
    n = len(tour)
    i = random.randint(0, n - 2)
    j = random.randint(i + 1, n - 1)
    return reverse_segment(tour, i, j)


def tournament_selection(
    population: List[List[str]],
    fitness: List[float],
    tournament_size: int = 3
) -> List[str]:
    """
    Tournament selection: select best individual from random subset.

    Args:
        population: List of tours
        fitness: List of fitness values (lower is better for TSP)
        tournament_size: Number of individuals in tournament

    Returns:
        Selected tour
    """
    # Select random individuals for tournament
    indices = random.sample(range(len(population)), tournament_size)

    # Find best (lowest cost) in tournament
    best_idx = min(indices, key=lambda i: fitness[i])

    return population[best_idx]


def genetic_algorithm_tsp(
    graph: nx.Graph,
    population_size: int = 100,
    generations: int = 500,
    mutation_rate: float = 0.2,
    crossover_type: str = 'order',
    mutation_type: str = 'reverse',
    elitism_count: int = 2,
    tournament_size: int = 3,
    random_seed: Optional[int] = None,
    verbose: bool = False
) -> Tuple[List[str], float, List[float]]:
    """
    Solve TSP using Genetic Algorithm.

    A Genetic Algorithm (GA) is a population-based metaheuristic that:
    1. Maintains a population of candidate solutions (tours)
    2. Evolves the population through selection, crossover, and mutation
    3. Uses natural selection principles to improve solutions
    4. Balances exploration (mutation) and exploitation (crossover)

    Args:
        graph: NetworkX graph with edge weights
        population_size: Number of individuals in population
        generations: Number of generations to evolve
        mutation_rate: Probability of mutation (0.0 to 1.0)
        crossover_type: 'order' (OX) or 'pmx' (PMX)
        mutation_type: 'swap' or 'reverse' (2-opt)
        elitism_count: Number of best individuals to preserve
        tournament_size: Tournament size for selection
        random_seed: Random seed for reproducibility
        verbose: Print progress information

    Returns:
        Tuple of (best_tour, best_cost, best_per_generation)
        - best_tour: Best tour found
        - best_cost: Cost of best tour
        - best_per_generation: Best cost in each generation

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=1.0)
        >>> G.add_edge('B', 'C', weight=1.0)
        >>> G.add_edge('C', 'A', weight=1.0)
        >>> tour, cost, history = genetic_algorithm_tsp(G, population_size=20, generations=50)
        >>> len(tour) == 3
        True
    """
    # Set random seed
    if random_seed is not None:
        random.seed(random_seed)

    # Select crossover operator
    if crossover_type == 'order':
        crossover = order_crossover
    elif crossover_type == 'pmx':
        crossover = pmx_crossover
    else:
        raise ValueError(f"Unknown crossover type: {crossover_type}")

    # Select mutation operator
    if mutation_type == 'swap':
        mutate = swap_mutation
    elif mutation_type == 'reverse':
        mutate = reverse_mutation
    else:
        raise ValueError(f"Unknown mutation type: {mutation_type}")

    # Metric closure for consistent shortest-path distances
    closure = build_metric_closure(graph)
    nodes = list(closure.nodes())
    population = []

    for _ in range(population_size):
        tour = nodes.copy()
        random.shuffle(tour)
        population.append(tour)

    # Track best solution across all generations
    best_tour = None
    best_cost = float('inf')
    best_per_generation = []

    if verbose:
        print("Genetic Algorithm Starting:")
        print(f"  Population size: {population_size}")
        print(f"  Generations: {generations}")
        print(f"  Mutation rate: {mutation_rate}")
        print(f"  Crossover: {crossover_type}")
        print(f"  Mutation: {mutation_type}")

    # Evolution loop
    for generation in range(generations):
        # Evaluate fitness (tour cost) for each individual
        fitness = [calculate_tour_cost(tour, closure) for tour in population]

        # Track best in this generation
        gen_best_idx = min(range(len(fitness)), key=lambda i: fitness[i])
        gen_best_cost = fitness[gen_best_idx]
        best_per_generation.append(gen_best_cost)

        # Update global best
        if gen_best_cost < best_cost:
            best_cost = gen_best_cost
            best_tour = population[gen_best_idx].copy()

            if verbose and generation % 50 == 0:
                print(f"  Gen {generation}: Best = {best_cost:.2f} min")

        # Create next generation
        new_population = []

        # Elitism: preserve best individuals
        elite_indices = sorted(range(len(fitness)), key=lambda i: fitness[i])[:elitism_count]
        for idx in elite_indices:
            new_population.append(population[idx].copy())

        # Fill rest of population with offspring
        while len(new_population) < population_size:
            # Selection
            parent1 = tournament_selection(population, fitness, tournament_size)
            parent2 = tournament_selection(population, fitness, tournament_size)

            # Crossover
            child = crossover(parent1, parent2)

            # Mutation
            if random.random() < mutation_rate:
                child = mutate(child)

            new_population.append(child)

        population = new_population

    if verbose:
        print("\nGenetic Algorithm Complete:")
        print(f"  Best cost: {best_cost:.2f} minutes")
        print(f"  Final average cost: {sum(fitness)/len(fitness):.2f} minutes")

    return best_tour, best_cost, best_per_generation


def genetic_algorithm_adaptive(
    graph: nx.Graph,
    target_time_seconds: float = 30.0,
    random_seed: Optional[int] = None,
    verbose: bool = False
) -> Tuple[List[str], float, List[float]]:
    """
    Genetic Algorithm with adaptive parameters based on target time.

    Args:
        graph: NetworkX graph with edge weights
        target_time_seconds: Target computation time
        random_seed: Random seed for reproducibility
        verbose: Print progress information

    Returns:
        Tuple of (best_tour, best_cost, best_per_generation)
    """
    import time

    # Adaptive parameters based on graph size
    closure = build_metric_closure(graph)
    n = closure.number_of_nodes()

    # Scale population with problem size
    population_size = min(100, max(20, n))

    # Estimate generations based on target time
    # Rough estimate: population_size evaluations per generation
    # Can do ~1000-5000 evaluations per second
    evaluations_per_second = 2000
    total_evaluations = int(target_time_seconds * evaluations_per_second)
    generations = total_evaluations // population_size

    if verbose:
        print("Adaptive GA parameters:")
        print(f"  Graph size: {n} nodes")
        print(f"  Target time: {target_time_seconds}s")
        print(f"  Population size: {population_size}")
        print(f"  Generations: {generations}")

    start_time = time.time()

    result = genetic_algorithm_tsp(
        closure,
        population_size=population_size,
        generations=generations,
        mutation_rate=0.2,
        crossover_type='order',
        mutation_type='reverse',
        random_seed=random_seed,
        verbose=verbose
    )

    elapsed = time.time() - start_time

    if verbose:
        print(f"\nActual computation time: {elapsed:.2f}s")

    return result
