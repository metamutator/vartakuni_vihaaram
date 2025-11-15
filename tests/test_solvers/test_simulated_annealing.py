"""Tests for Simulated Annealing TSP solver."""

import pytest
import networkx as nx
from src.solvers.simulated_annealing import (
    simulated_annealing_tsp,
    simulated_annealing_adaptive,
    linear_cooling,
    exponential_cooling,
    logarithmic_cooling,
    generate_neighbor_2opt
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


class TestCoolingSchedules:
    """Test suite for cooling schedule functions."""

    def test_linear_cooling_starts_at_initial(self):
        """Test that linear cooling starts at initial temperature."""
        temp = linear_cooling(100.0, 0, 1000)
        assert temp == 100.0

    def test_linear_cooling_ends_at_zero(self):
        """Test that linear cooling ends at zero."""
        temp = linear_cooling(100.0, 1000, 1000)
        assert temp == 0.0

    def test_linear_cooling_decreases(self):
        """Test that linear cooling decreases monotonically."""
        temps = [linear_cooling(100.0, i, 100) for i in range(101)]
        assert all(temps[i] >= temps[i+1] for i in range(100))

    def test_exponential_cooling_starts_at_initial(self):
        """Test that exponential cooling starts at initial temperature."""
        temp = exponential_cooling(100.0, 0, 0.95)
        assert temp == 100.0

    def test_exponential_cooling_decreases(self):
        """Test that exponential cooling decreases monotonically."""
        temps = [exponential_cooling(100.0, i, 0.95) for i in range(100)]
        assert all(temps[i] >= temps[i+1] for i in range(99))

    def test_exponential_cooling_never_zero(self):
        """Test that exponential cooling never reaches zero."""
        temp = exponential_cooling(100.0, 1000, 0.95)
        assert temp > 0

    def test_logarithmic_cooling_starts_at_initial(self):
        """Test that logarithmic cooling starts at initial temperature."""
        temp = logarithmic_cooling(100.0, 0)
        assert temp == 100.0

    def test_logarithmic_cooling_decreases(self):
        """Test that logarithmic cooling decreases."""
        temps = [logarithmic_cooling(100.0, i) for i in range(100)]
        assert temps[99] < temps[0]


class TestGenerateNeighbor:
    """Test suite for neighbor generation."""

    def test_generate_neighbor_returns_valid_tour(self):
        """Test that neighbor generation returns valid tour."""
        tour = ['A', 'B', 'C', 'D', 'E']
        neighbor, i, j = generate_neighbor_2opt(tour)

        assert len(neighbor) == len(tour)
        assert set(neighbor) == set(tour)

    def test_generate_neighbor_is_different(self):
        """Test that neighbor is different from original (usually)."""
        tour = ['A', 'B', 'C', 'D', 'E']

        # Generate multiple neighbors
        neighbors = [generate_neighbor_2opt(tour)[0] for _ in range(10)]

        # At least one should be different
        assert any(n != tour for n in neighbors)

    def test_generate_neighbor_indices(self):
        """Test that indices are valid."""
        tour = ['A', 'B', 'C', 'D', 'E']
        neighbor, i, j = generate_neighbor_2opt(tour)

        assert 0 <= i < len(tour)
        assert 0 <= j < len(tour)
        assert i < j


class TestSimulatedAnnealingTSP:
    """Test suite for simulated_annealing_tsp function."""

    def test_basic_functionality(self, simple_triangle):
        """Test basic SA functionality."""
        tour, cost, history = simulated_annealing_tsp(
            simple_triangle,
            max_iterations=100,
            random_seed=42
        )

        assert len(tour) == 3
        assert set(tour) == {'A', 'B', 'C'}
        assert cost > 0
        assert len(history) == 101  # Initial + 100 iterations

    def test_with_initial_tour(self, square_graph):
        """Test SA with provided initial tour."""
        initial = ['A', 'B', 'C', 'D']

        tour, cost, history = simulated_annealing_tsp(
            square_graph,
            initial_tour=initial,
            max_iterations=50,
            random_seed=42
        )

        assert len(tour) == 4
        assert set(tour) == {'A', 'B', 'C', 'D'}

    def test_deterministic_with_seed(self, simple_triangle):
        """Test that results are deterministic with same seed."""
        tour1, cost1, _ = simulated_annealing_tsp(
            simple_triangle,
            max_iterations=100,
            random_seed=42
        )

        tour2, cost2, _ = simulated_annealing_tsp(
            simple_triangle,
            max_iterations=100,
            random_seed=42
        )

        assert tour1 == tour2
        assert cost1 == cost2

    def test_different_seeds_different_results(self, square_graph):
        """Test that different seeds give different results (usually)."""
        tour1, cost1, _ = simulated_annealing_tsp(
            square_graph,
            max_iterations=100,
            random_seed=42
        )

        tour2, cost2, _ = simulated_annealing_tsp(
            square_graph,
            max_iterations=100,
            random_seed=123
        )

        # At least cost or tour should be different
        assert tour1 != tour2 or cost1 != cost2

    def test_linear_cooling(self, square_graph):
        """Test SA with linear cooling schedule."""
        tour, cost, history = simulated_annealing_tsp(
            square_graph,
            cooling_schedule='linear',
            max_iterations=50,
            random_seed=42
        )

        assert len(tour) == 4

    def test_exponential_cooling(self, square_graph):
        """Test SA with exponential cooling schedule."""
        tour, cost, history = simulated_annealing_tsp(
            square_graph,
            cooling_schedule='exponential',
            max_iterations=50,
            random_seed=42
        )

        assert len(tour) == 4

    def test_logarithmic_cooling(self, square_graph):
        """Test SA with logarithmic cooling schedule."""
        tour, cost, history = simulated_annealing_tsp(
            square_graph,
            cooling_schedule='logarithmic',
            max_iterations=50,
            random_seed=42
        )

        assert len(tour) == 4

    def test_invalid_cooling_schedule(self, simple_triangle):
        """Test that invalid cooling schedule raises error."""
        with pytest.raises(ValueError, match="Unknown cooling schedule"):
            simulated_annealing_tsp(
                simple_triangle,
                cooling_schedule='invalid',
                max_iterations=10
            )

    def test_verbose_output(self, square_graph, capsys):
        """Test verbose output."""
        simulated_annealing_tsp(
            square_graph,
            max_iterations=100,
            verbose=True,
            random_seed=42
        )

        captured = capsys.readouterr()
        assert "Simulated Annealing Starting" in captured.out
        assert "Simulated Annealing Complete" in captured.out

    def test_cost_history_length(self, simple_triangle):
        """Test that cost history has correct length."""
        tour, cost, history = simulated_annealing_tsp(
            simple_triangle,
            max_iterations=50,
            random_seed=42
        )

        assert len(history) == 51  # Initial + 50 iterations

    def test_best_cost_in_history(self, square_graph):
        """Test that best cost is in history."""
        tour, best_cost, history = simulated_annealing_tsp(
            square_graph,
            max_iterations=100,
            random_seed=42
        )

        # Best cost should be minimum in history
        assert best_cost <= min(history)

    def test_initial_temperature_effect(self, square_graph):
        """Test effect of initial temperature."""
        # High temperature should explore more
        tour1, cost1, history1 = simulated_annealing_tsp(
            square_graph,
            initial_temp=1000.0,
            max_iterations=100,
            random_seed=42
        )

        # Low temperature should behave more like hill climbing
        tour2, cost2, history2 = simulated_annealing_tsp(
            square_graph,
            initial_temp=0.1,
            max_iterations=100,
            random_seed=42
        )

        # Both should find valid solutions
        assert len(tour1) == 4
        assert len(tour2) == 4

    def test_longer_run_better_result(self, square_graph):
        """Test that longer runs tend to find better results."""
        # Short run
        tour_short, cost_short, _ = simulated_annealing_tsp(
            square_graph,
            max_iterations=10,
            random_seed=42
        )

        # Long run
        tour_long, cost_long, _ = simulated_annealing_tsp(
            square_graph,
            max_iterations=1000,
            random_seed=42
        )

        # Long run should be at least as good
        assert cost_long <= cost_short


class TestSimulatedAnnealingAdaptive:
    """Test suite for simulated_annealing_adaptive function."""

    def test_basic_functionality(self, square_graph):
        """Test basic adaptive SA functionality."""
        tour, cost, history = simulated_annealing_adaptive(
            square_graph,
            target_time_seconds=1.0,
            random_seed=42
        )

        assert len(tour) == 4
        assert set(tour) == {'A', 'B', 'C', 'D'}
        assert cost > 0

    def test_verbose_output(self, square_graph, capsys):
        """Test verbose output for adaptive SA."""
        simulated_annealing_adaptive(
            square_graph,
            target_time_seconds=0.5,
            verbose=True,
            random_seed=42
        )

        captured = capsys.readouterr()
        assert "Adaptive SA parameters" in captured.out
        assert "Actual computation time" in captured.out

    def test_deterministic_with_seed(self, simple_triangle):
        """Test determinism with random seed."""
        tour1, cost1, _ = simulated_annealing_adaptive(
            simple_triangle,
            target_time_seconds=0.5,
            random_seed=42
        )

        tour2, cost2, _ = simulated_annealing_adaptive(
            simple_triangle,
            target_time_seconds=0.5,
            random_seed=42
        )

        assert tour1 == tour2
        assert cost1 == cost2


class TestSimulatedAnnealingIntegration:
    """Integration tests for Simulated Annealing."""

    def test_sa_improves_random_tour(self):
        """Test that SA improves upon random initial tour."""
        from src.utils.tour import calculate_tour_cost

        # Create test graph
        G = nx.complete_graph(5)
        for u, v in G.edges():
            G[u][v]['weight'] = abs(u - v)

        # Random initial tour
        import random
        random.seed(42)
        initial_tour = list(G.nodes())
        random.shuffle(initial_tour)
        initial_cost = calculate_tour_cost(initial_tour, G)

        # Optimize with SA
        tour, cost, history = simulated_annealing_tsp(
            G,
            initial_tour=initial_tour,
            max_iterations=500,
            random_seed=42
        )

        # Should find equal or better solution
        assert cost <= initial_cost

    def test_sa_vs_greedy(self, square_graph):
        """Test that SA can find better solutions than greedy methods."""
        from src.solvers.nearest_neighbor import nearest_neighbor_tsp

        # Get greedy solution
        nn_tour, nn_cost = nearest_neighbor_tsp(square_graph)

        # Run SA
        sa_tour, sa_cost, _ = simulated_annealing_tsp(
            square_graph,
            max_iterations=1000,
            random_seed=42
        )

        # SA should be competitive (within reasonable range)
        assert sa_cost <= nn_cost * 1.5  # Allow some variance

    @pytest.mark.slow
    def test_performance_larger_graph(self):
        """Test SA performance on larger graph."""
        import random
        import time

        # Create larger graph
        n = 30
        G = nx.complete_graph(n)

        random.seed(42)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(1.0, 10.0)

        # Time SA execution
        start = time.time()
        tour, cost, history = simulated_annealing_tsp(
            G,
            max_iterations=1000,
            random_seed=42
        )
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 10.0  # Less than 10 seconds

        # Should visit all nodes
        assert len(tour) == n
        assert set(tour) == set(range(n))
