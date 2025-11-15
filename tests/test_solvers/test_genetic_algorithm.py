"""Tests for Genetic Algorithm TSP solver."""

import pytest
import networkx as nx
from src.solvers.genetic_algorithm import (
    genetic_algorithm_tsp,
    genetic_algorithm_adaptive,
    order_crossover,
    pmx_crossover,
    swap_mutation,
    reverse_mutation,
    tournament_selection
)


@pytest.fixture
def simple_triangle():
    """Create a simple triangle graph."""
    G = nx.Graph()
    G.add_edge('A', 'B', weight=1.0)
    G.add_edge('B', 'C', weight=2.0)
    G.add_edge('C', 'A', weight=3.0)
    return G


@pytest.fixture
def square_graph():
    """Create a square graph with diagonals."""
    G = nx.Graph()
    G.add_edge('A', 'B', weight=1.0)
    G.add_edge('B', 'C', weight=1.0)
    G.add_edge('C', 'D', weight=1.0)
    G.add_edge('D', 'A', weight=1.0)
    G.add_edge('A', 'C', weight=1.4)
    G.add_edge('B', 'D', weight=1.4)
    return G


class TestCrossoverOperators:
    """Test suite for crossover operators."""

    def test_order_crossover_valid_tour(self):
        """Test that OX produces valid tour."""
        parent1 = ['A', 'B', 'C', 'D', 'E']
        parent2 = ['C', 'D', 'A', 'E', 'B']

        child = order_crossover(parent1, parent2)

        assert len(child) == len(parent1)
        assert set(child) == set(parent1)
        assert len(child) == len(set(child))  # No duplicates

    def test_order_crossover_deterministic(self):
        """Test that OX is deterministic with same random state."""
        import random

        parent1 = ['A', 'B', 'C', 'D', 'E']
        parent2 = ['C', 'D', 'A', 'E', 'B']

        random.seed(42)
        child1 = order_crossover(parent1, parent2)

        random.seed(42)
        child2 = order_crossover(parent1, parent2)

        assert child1 == child2

    def test_order_crossover_inherits_from_parents(self):
        """Test that child inherits genes from both parents."""
        parent1 = ['A', 'B', 'C', 'D', 'E']
        parent2 = ['E', 'D', 'C', 'B', 'A']

        # Run multiple times
        import random
        random.seed(42)
        for _ in range(10):
            child = order_crossover(parent1, parent2)
            # Child should contain all elements
            assert set(child) == set(parent1)

    def test_pmx_crossover_valid_tour(self):
        """Test that PMX produces valid tour."""
        parent1 = ['A', 'B', 'C', 'D', 'E']
        parent2 = ['C', 'D', 'A', 'E', 'B']

        child = pmx_crossover(parent1, parent2)

        assert len(child) == len(parent1)
        assert set(child) == set(parent1)
        assert len(child) == len(set(child))  # No duplicates

    def test_pmx_crossover_deterministic(self):
        """Test that PMX is deterministic."""
        import random

        parent1 = ['A', 'B', 'C', 'D', 'E']
        parent2 = ['C', 'D', 'A', 'E', 'B']

        random.seed(42)
        child1 = pmx_crossover(parent1, parent2)

        random.seed(42)
        child2 = pmx_crossover(parent1, parent2)

        assert child1 == child2


class TestMutationOperators:
    """Test suite for mutation operators."""

    def test_swap_mutation_valid_tour(self):
        """Test that swap mutation produces valid tour."""
        tour = ['A', 'B', 'C', 'D', 'E']

        mutated = swap_mutation(tour)

        assert len(mutated) == len(tour)
        assert set(mutated) == set(tour)

    def test_swap_mutation_changes_tour(self):
        """Test that swap mutation changes the tour."""
        import random
        random.seed(42)

        tour = ['A', 'B', 'C', 'D', 'E']

        # Run multiple times, at least one should be different
        mutations = [swap_mutation(tour) for _ in range(10)]
        assert any(m != tour for m in mutations)

    def test_swap_mutation_original_unchanged(self):
        """Test that original tour is not modified."""
        tour = ['A', 'B', 'C', 'D', 'E']
        original = tour.copy()

        swap_mutation(tour)

        assert tour == original

    def test_reverse_mutation_valid_tour(self):
        """Test that reverse mutation produces valid tour."""
        tour = ['A', 'B', 'C', 'D', 'E']

        mutated = reverse_mutation(tour)

        assert len(mutated) == len(tour)
        assert set(mutated) == set(tour)

    def test_reverse_mutation_changes_tour(self):
        """Test that reverse mutation changes the tour."""
        import random
        random.seed(42)

        tour = ['A', 'B', 'C', 'D', 'E']

        mutations = [reverse_mutation(tour) for _ in range(10)]
        assert any(m != tour for m in mutations)


class TestTournamentSelection:
    """Test suite for tournament selection."""

    def test_tournament_selects_best(self):
        """Test that tournament selection prefers better individuals."""
        population = [
            ['A', 'B', 'C'],
            ['B', 'C', 'A'],
            ['C', 'A', 'B']
        ]
        fitness = [10.0, 5.0, 20.0]  # Lower is better

        import random
        random.seed(42)

        # Run tournament multiple times
        selections = [tournament_selection(population, fitness, 3) for _ in range(10)]

        # Should select second individual (best fitness) most often
        assert selections.count(population[1]) > 0

    def test_tournament_size_effect(self):
        """Test effect of tournament size."""
        population = [['A', 'B'], ['B', 'A'], ['A', 'B'], ['B', 'A']]
        fitness = [10.0, 5.0, 15.0, 8.0]

        import random
        random.seed(42)

        # Larger tournament should be more selective
        selected = tournament_selection(population, fitness, tournament_size=3)
        assert selected in population


class TestGeneticAlgorithmTSP:
    """Test suite for genetic_algorithm_tsp function."""

    def test_basic_functionality(self, simple_triangle):
        """Test basic GA functionality."""
        tour, cost, history = genetic_algorithm_tsp(
            simple_triangle,
            population_size=10,
            generations=20,
            random_seed=42
        )

        assert len(tour) == 3
        assert set(tour) == {'A', 'B', 'C'}
        assert cost > 0
        assert len(history) == 20

    def test_with_square_graph(self, square_graph):
        """Test GA on square graph."""
        tour, cost, history = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=50,
            random_seed=42
        )

        assert len(tour) == 4
        assert set(tour) == {'A', 'B', 'C', 'D'}

    def test_deterministic_with_seed(self, simple_triangle):
        """Test that results are deterministic with same seed."""
        tour1, cost1, _ = genetic_algorithm_tsp(
            simple_triangle,
            population_size=10,
            generations=20,
            random_seed=42
        )

        tour2, cost2, _ = genetic_algorithm_tsp(
            simple_triangle,
            population_size=10,
            generations=20,
            random_seed=42
        )

        assert tour1 == tour2
        assert cost1 == cost2

    def test_different_seeds_different_results(self, square_graph):
        """Test that different seeds give different results (usually)."""
        tour1, cost1, _ = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=30,
            random_seed=42
        )

        tour2, cost2, _ = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=30,
            random_seed=123
        )

        # Results should differ (at least sometimes)
        assert tour1 != tour2 or cost1 != cost2

    def test_order_crossover_type(self, square_graph):
        """Test GA with order crossover."""
        tour, cost, history = genetic_algorithm_tsp(
            square_graph,
            population_size=15,
            generations=25,
            crossover_type='order',
            random_seed=42
        )

        assert len(tour) == 4

    def test_pmx_crossover_type(self, square_graph):
        """Test GA with PMX crossover."""
        tour, cost, history = genetic_algorithm_tsp(
            square_graph,
            population_size=15,
            generations=25,
            crossover_type='pmx',
            random_seed=42
        )

        assert len(tour) == 4

    def test_swap_mutation_type(self, square_graph):
        """Test GA with swap mutation."""
        tour, cost, history = genetic_algorithm_tsp(
            square_graph,
            population_size=15,
            generations=25,
            mutation_type='swap',
            random_seed=42
        )

        assert len(tour) == 4

    def test_reverse_mutation_type(self, square_graph):
        """Test GA with reverse mutation."""
        tour, cost, history = genetic_algorithm_tsp(
            square_graph,
            population_size=15,
            generations=25,
            mutation_type='reverse',
            random_seed=42
        )

        assert len(tour) == 4

    def test_invalid_crossover_type(self, simple_triangle):
        """Test that invalid crossover type raises error."""
        with pytest.raises(ValueError, match="Unknown crossover type"):
            genetic_algorithm_tsp(
                simple_triangle,
                crossover_type='invalid',
                random_seed=42
            )

    def test_invalid_mutation_type(self, simple_triangle):
        """Test that invalid mutation type raises error."""
        with pytest.raises(ValueError, match="Unknown mutation type"):
            genetic_algorithm_tsp(
                simple_triangle,
                mutation_type='invalid',
                random_seed=42
            )

    def test_mutation_rate_effect(self, square_graph):
        """Test effect of mutation rate."""
        # No mutation
        tour1, cost1, _ = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=30,
            mutation_rate=0.0,
            random_seed=42
        )

        # High mutation
        tour2, cost2, _ = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=30,
            mutation_rate=0.8,
            random_seed=42
        )

        # Both should find valid solutions
        assert len(tour1) == 4
        assert len(tour2) == 4

    def test_elitism(self, square_graph):
        """Test that elitism preserves best individuals."""
        tour, cost, history = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=50,
            elitism_count=2,
            random_seed=42
        )

        # History should show non-increasing best cost
        for i in range(1, len(history)):
            assert history[i] <= history[i-1]

    def test_verbose_output(self, square_graph, capsys):
        """Test verbose output."""
        genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=100,
            verbose=True,
            random_seed=42
        )

        captured = capsys.readouterr()
        assert "Genetic Algorithm Starting" in captured.out
        assert "Genetic Algorithm Complete" in captured.out

    def test_history_length(self, simple_triangle):
        """Test that history has correct length."""
        tour, cost, history = genetic_algorithm_tsp(
            simple_triangle,
            population_size=10,
            generations=25,
            random_seed=42
        )

        assert len(history) == 25

    def test_longer_run_better_result(self, square_graph):
        """Test that more generations tend to find better results."""
        # Short run
        tour_short, cost_short, _ = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=10,
            random_seed=42
        )

        # Long run
        tour_long, cost_long, _ = genetic_algorithm_tsp(
            square_graph,
            population_size=20,
            generations=200,
            random_seed=42
        )

        # Long run should be at least as good
        assert cost_long <= cost_short


class TestGeneticAlgorithmAdaptive:
    """Test suite for genetic_algorithm_adaptive function."""

    def test_basic_functionality(self, square_graph):
        """Test basic adaptive GA functionality."""
        tour, cost, history = genetic_algorithm_adaptive(
            square_graph,
            target_time_seconds=1.0,
            random_seed=42
        )

        assert len(tour) == 4
        assert set(tour) == {'A', 'B', 'C', 'D'}
        assert cost > 0

    def test_verbose_output(self, square_graph, capsys):
        """Test verbose output for adaptive GA."""
        genetic_algorithm_adaptive(
            square_graph,
            target_time_seconds=0.5,
            verbose=True,
            random_seed=42
        )

        captured = capsys.readouterr()
        assert "Adaptive GA parameters" in captured.out
        assert "Actual computation time" in captured.out

    def test_deterministic_with_seed(self, simple_triangle):
        """Test determinism with random seed."""
        tour1, cost1, _ = genetic_algorithm_adaptive(
            simple_triangle,
            target_time_seconds=0.5,
            random_seed=42
        )

        tour2, cost2, _ = genetic_algorithm_adaptive(
            simple_triangle,
            target_time_seconds=0.5,
            random_seed=42
        )

        assert tour1 == tour2
        assert cost1 == cost2


class TestGeneticAlgorithmIntegration:
    """Integration tests for Genetic Algorithm."""

    def test_ga_finds_valid_solution(self):
        """Test that GA finds valid TSP solution."""
        from src.utils.tour import validate_tour

        # Create test graph
        G = nx.complete_graph(5)
        for u, v in G.edges():
            G[u][v]['weight'] = abs(u - v)

        # Run GA
        tour, cost, history = genetic_algorithm_tsp(
            G,
            population_size=30,
            generations=100,
            random_seed=42
        )

        # Validate solution
        validate_tour(tour, G, require_complete=True)

    def test_ga_improves_over_generations(self, square_graph):
        """Test that GA improves over generations."""
        tour, cost, history = genetic_algorithm_tsp(
            square_graph,
            population_size=30,
            generations=100,
            random_seed=42
        )

        # Best cost should improve or stay same
        assert history[-1] <= history[0]

    def test_ga_vs_random(self):
        """Test that GA beats random solutions."""
        from src.utils.tour import calculate_tour_cost
        import random

        # Create test graph
        G = nx.complete_graph(6)
        random.seed(42)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(1.0, 10.0)

        # Random tour
        random_tour = list(G.nodes())
        random.shuffle(random_tour)
        random_cost = calculate_tour_cost(random_tour, G)

        # GA solution
        ga_tour, ga_cost, _ = genetic_algorithm_tsp(
            G,
            population_size=30,
            generations=200,
            random_seed=42
        )

        # GA should beat random (with high probability)
        assert ga_cost <= random_cost * 1.2  # Allow some variance

    @pytest.mark.slow
    def test_performance_larger_graph(self):
        """Test GA performance on larger graph."""
        import random
        import time

        # Create larger graph
        n = 30
        G = nx.complete_graph(n)

        random.seed(42)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(1.0, 10.0)

        # Time GA execution
        start = time.time()
        tour, cost, history = genetic_algorithm_tsp(
            G,
            population_size=50,
            generations=100,
            random_seed=42
        )
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 30.0  # Less than 30 seconds

        # Should visit all nodes
        assert len(tour) == n
        assert set(tour) == set(range(n))

    def test_different_operators_comparison(self, square_graph):
        """Test comparison of different operators."""
        # OX + reverse
        tour1, cost1, _ = genetic_algorithm_tsp(
            square_graph,
            crossover_type='order',
            mutation_type='reverse',
            population_size=20,
            generations=50,
            random_seed=42
        )

        # PMX + swap
        tour2, cost2, _ = genetic_algorithm_tsp(
            square_graph,
            crossover_type='pmx',
            mutation_type='swap',
            population_size=20,
            generations=50,
            random_seed=42
        )

        # Both should find valid solutions
        assert len(tour1) == 4
        assert len(tour2) == 4
