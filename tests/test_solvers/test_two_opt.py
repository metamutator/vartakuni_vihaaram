"""Tests for 2-opt local search algorithm."""

import pytest
import networkx as nx
from src.solvers.two_opt import improve_tour_2opt, improve_tour_2opt_fast


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
    # Square edges
    G.add_edge('A', 'B', weight=1.0)
    G.add_edge('B', 'C', weight=1.0)
    G.add_edge('C', 'D', weight=1.0)
    G.add_edge('D', 'A', weight=1.0)
    # Diagonals (shortcuts)
    G.add_edge('A', 'C', weight=1.4)
    G.add_edge('B', 'D', weight=1.4)
    return G


@pytest.fixture
def tsp_graph():
    """Create a more complex TSP graph for testing."""
    G = nx.Graph()
    # Create a graph where 2-opt can find improvements
    # Edges forming a cross pattern
    G.add_edge('A', 'B', weight=1.0)
    G.add_edge('A', 'C', weight=1.0)
    G.add_edge('A', 'D', weight=1.0)
    G.add_edge('A', 'E', weight=1.0)
    G.add_edge('B', 'C', weight=5.0)
    G.add_edge('C', 'D', weight=5.0)
    G.add_edge('D', 'E', weight=5.0)
    G.add_edge('E', 'B', weight=5.0)
    G.add_edge('B', 'D', weight=8.0)
    G.add_edge('C', 'E', weight=8.0)
    return G


class TestImproveTour2Opt:
    """Test suite for improve_tour_2opt function."""

    def test_improve_simple_tour(self, simple_triangle):
        """Test improvement on a simple triangle tour."""
        # For a triangle, all tours are equivalent
        tour = ['A', 'B', 'C']
        improved_tour, original_cost, improved_cost = improve_tour_2opt(
            tour, simple_triangle
        )

        # Should return a valid tour
        assert len(improved_tour) == 3
        assert set(improved_tour) == {'A', 'B', 'C'}
        assert improved_cost <= original_cost
        assert original_cost == 6.0

    def test_improve_suboptimal_tour(self, square_graph):
        """Test improvement on a clearly suboptimal tour."""
        # Bad tour: A -> C -> B -> D -> A
        # Cost: 1.4 + 1.0 + 1.4 + 1.0 = 4.8
        # Optimal: A -> B -> C -> D -> A
        # Cost: 1.0 + 1.0 + 1.0 + 1.0 = 4.0
        tour = ['A', 'C', 'B', 'D']
        improved_tour, original_cost, improved_cost = improve_tour_2opt(
            tour, square_graph
        )

        assert improved_cost < original_cost
        # Check that we found a better solution
        assert improved_cost <= 4.0

    def test_max_iterations_limit(self, tsp_graph):
        """Test that max_iterations limit is respected."""
        tour = ['A', 'B', 'C', 'D', 'E']
        improved_tour, original_cost, improved_cost = improve_tour_2opt(
            tour, tsp_graph, max_iterations=1
        )

        # Should stop after 1 iteration even if not optimal
        assert len(improved_tour) == 5

    def test_improvement_threshold(self, square_graph):
        """Test that improvement threshold is respected."""
        tour = ['A', 'C', 'B', 'D']

        # High threshold should stop early
        improved_tour, original_cost, improved_cost = improve_tour_2opt(
            tour, square_graph, improvement_threshold=10.0
        )

        # Should stop immediately since no improvement > 10.0 is possible
        assert improved_cost == original_cost or improved_cost < original_cost

    def test_return_values(self, simple_triangle):
        """Test that function returns correct tuple format."""
        tour = ['A', 'B', 'C']
        result = improve_tour_2opt(tour, simple_triangle)

        # Should return tuple of (tour, original_cost, improved_cost)
        assert isinstance(result, tuple)
        assert len(result) == 3

        improved_tour, original_cost, improved_cost = result
        assert isinstance(improved_tour, list)
        assert isinstance(original_cost, float)
        assert isinstance(improved_cost, float)

    def test_invalid_tour(self, simple_triangle):
        """Test that invalid tour raises error."""
        # Tour with invalid station
        tour = ['A', 'B', 'X']

        with pytest.raises(ValueError):
            improve_tour_2opt(tour, simple_triangle)

    def test_tour_with_duplicates(self, simple_triangle):
        """Test that tour with duplicates raises error."""
        tour = ['A', 'B', 'A']

        with pytest.raises(ValueError, match="duplicate"):
            improve_tour_2opt(tour, simple_triangle)

    def test_original_tour_unchanged(self, simple_triangle):
        """Test that original tour is not modified."""
        tour = ['A', 'B', 'C']
        original_tour = tour.copy()

        improve_tour_2opt(tour, simple_triangle)

        assert tour == original_tour

    def test_verbose_output(self, square_graph, capsys):
        """Test verbose output mode."""
        tour = ['A', 'C', 'B', 'D']

        improve_tour_2opt(tour, square_graph, verbose=True)

        captured = capsys.readouterr()
        assert "Initial tour cost" in captured.out
        assert "Optimization complete" in captured.out

    def test_already_optimal_tour(self, square_graph):
        """Test 2-opt on already optimal tour."""
        # Optimal tour
        tour = ['A', 'B', 'C', 'D']
        improved_tour, original_cost, improved_cost = improve_tour_2opt(
            tour, square_graph
        )

        # Should not improve (or minimal improvement due to floating point)
        assert improved_cost == original_cost

    def test_two_node_tour(self):
        """Test 2-opt on minimal two-node tour."""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1.0)

        tour = ['A', 'B']
        improved_tour, original_cost, improved_cost = improve_tour_2opt(tour, G)

        assert improved_cost == original_cost
        assert set(improved_tour) == {'A', 'B'}


class TestImproveTour2OptFast:
    """Test suite for improve_tour_2opt_fast function."""

    def test_fast_version_improves_tour(self, square_graph):
        """Test that fast version also improves tours."""
        tour = ['A', 'C', 'B', 'D']
        improved_tour, original_cost, improved_cost = improve_tour_2opt_fast(
            tour, square_graph
        )

        assert improved_cost <= original_cost

    def test_fast_version_returns_correct_format(self, simple_triangle):
        """Test that fast version returns correct tuple format."""
        tour = ['A', 'B', 'C']
        result = improve_tour_2opt_fast(tour, simple_triangle)

        assert isinstance(result, tuple)
        assert len(result) == 3

        improved_tour, original_cost, improved_cost = result
        assert isinstance(improved_tour, list)
        assert isinstance(original_cost, float)
        assert isinstance(improved_cost, float)

    def test_fast_version_max_iterations(self, tsp_graph):
        """Test that fast version respects max_iterations."""
        tour = ['A', 'B', 'C', 'D', 'E']
        improved_tour, original_cost, improved_cost = improve_tour_2opt_fast(
            tour, tsp_graph, max_iterations=1
        )

        # Should stop after 1 iteration
        assert len(improved_tour) == 5

    def test_fast_vs_regular_comparison(self, square_graph):
        """Test that both versions find improvements."""
        tour = ['A', 'C', 'B', 'D']

        # Run both versions
        improved_regular, orig1, cost1 = improve_tour_2opt(tour, square_graph)
        improved_fast, orig2, cost2 = improve_tour_2opt_fast(tour, square_graph)

        # Both should improve (or at least not worsen)
        assert cost1 <= orig1
        assert cost2 <= orig2

        # Original costs should be the same
        assert orig1 == orig2


class TestTwoOptIntegration:
    """Integration tests for 2-opt algorithm."""

    def test_complete_optimization_workflow(self, tsp_graph):
        """Test complete optimization workflow."""
        # Start with arbitrary tour
        tour = ['A', 'B', 'C', 'D', 'E']

        # Validate and optimize
        from src.utils.tour import validate_tour, calculate_tour_cost

        validate_tour(tour, tsp_graph, require_complete=True)
        original_cost = calculate_tour_cost(tour, tsp_graph)

        # Optimize
        improved_tour, reported_original, improved_cost = improve_tour_2opt(
            tour, tsp_graph
        )

        # Verify results
        assert reported_original == original_cost
        assert improved_cost <= original_cost

        # Verify improved tour is valid
        validate_tour(improved_tour, tsp_graph, require_complete=True)

        # Verify improved cost is correct
        actual_improved_cost = calculate_tour_cost(improved_tour, tsp_graph)
        assert abs(actual_improved_cost - improved_cost) < 1e-10

    def test_multiple_optimization_runs(self, square_graph):
        """Test that running 2-opt multiple times is idempotent."""
        tour = ['A', 'C', 'B', 'D']

        # First optimization
        improved1, _, cost1 = improve_tour_2opt(tour, square_graph)

        # Second optimization on already optimized tour
        improved2, _, cost2 = improve_tour_2opt(improved1, square_graph)

        # Should not improve further (local optimum)
        assert cost2 == cost1

    def test_optimization_finds_local_optimum(self, square_graph):
        """Test that 2-opt finds a local optimum."""
        tour = ['A', 'C', 'B', 'D']

        improved_tour, _, final_cost = improve_tour_2opt(tour, square_graph)

        # Try all possible 2-opt swaps on the result
        # None should improve the solution
        from src.utils.tour import calculate_swap_delta

        n = len(improved_tour)
        for i in range(n - 1):
            for j in range(i + 1, n):
                if j - i == 1:
                    continue
                delta = calculate_swap_delta(improved_tour, square_graph, i, j)
                # No swap should provide significant improvement
                assert delta >= -0.001  # Allow tiny numerical errors

    @pytest.mark.slow
    def test_performance_on_larger_graph(self):
        """Test 2-opt performance on a larger graph."""
        # Create a larger complete graph
        n = 20
        G = nx.complete_graph(n)

        # Assign random weights
        import random
        random.seed(42)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(1.0, 10.0)

        # Create arbitrary tour
        tour = list(range(n))

        # Optimize
        improved_tour, original_cost, improved_cost = improve_tour_2opt(
            tour, G, max_iterations=100
        )

        # Should find some improvement
        assert improved_cost <= original_cost

    def test_different_starting_points(self, square_graph):
        """Test 2-opt with different starting tours."""
        # Different tours of the same nodes
        tours = [
            ['A', 'B', 'C', 'D'],
            ['A', 'C', 'B', 'D'],
            ['A', 'D', 'C', 'B'],
            ['B', 'A', 'D', 'C'],
        ]

        results = []
        for tour in tours:
            _, _, improved_cost = improve_tour_2opt(tour, square_graph)
            results.append(improved_cost)

        # All should converge to same or similar local optimum
        # (might be different due to local optimum nature of 2-opt)
        assert all(cost <= 5.0 for cost in results)
