"""Tests for Nearest Neighbor TSP heuristic."""

import pytest
import networkx as nx
from src.solvers.nearest_neighbor import (
    nearest_neighbor_tsp,
    nearest_neighbor_multi_start,
    nearest_neighbor_with_2opt
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
    # Square edges
    G.add_edge('A', 'B', weight=1.0)
    G.add_edge('B', 'C', weight=1.0)
    G.add_edge('C', 'D', weight=1.0)
    G.add_edge('D', 'A', weight=1.0)
    # Diagonals
    G.add_edge('A', 'C', weight=1.4)
    G.add_edge('B', 'D', weight=1.4)
    return G


@pytest.fixture
def line_graph():
    """Create a linear chain graph."""
    G = nx.Graph()
    G.add_edge('A', 'B', weight=1.0)
    G.add_edge('B', 'C', weight=1.0)
    G.add_edge('C', 'D', weight=1.0)
    G.add_edge('D', 'E', weight=1.0)
    return G


class TestNearestNeighborTSP:
    """Test suite for nearest_neighbor_tsp function."""

    def test_simple_triangle(self, simple_triangle):
        """Test Nearest Neighbor on a simple triangle."""
        tour, cost = nearest_neighbor_tsp(simple_triangle, start_station='A')

        # Should visit all 3 nodes
        assert len(tour) == 3
        assert set(tour) == {'A', 'B', 'C'}

        # Should start at specified station
        assert tour[0] == 'A'

        # Cost should be sum of edges in tour
        assert cost == 6.0  # A->B (1.0) + B->C (2.0) + C->A (3.0)

    def test_default_start_station(self, simple_triangle):
        """Test that default start station is first node."""
        tour, cost = nearest_neighbor_tsp(simple_triangle)

        # Should visit all nodes
        assert len(tour) == 3
        assert set(tour) == {'A', 'B', 'C'}

        # Should return valid tour with valid cost
        assert cost > 0

    def test_square_graph_greedy_behavior(self, square_graph):
        """Test that Nearest Neighbor makes greedy choices."""
        tour, cost = nearest_neighbor_tsp(square_graph, start_station='A')

        # Should visit all 4 nodes
        assert len(tour) == 4
        assert set(tour) == {'A', 'B', 'C', 'D'}

        # From A, nearest is B (1.0) or D (1.0)
        assert tour[1] in ['B', 'D']

    def test_deterministic_results(self, square_graph):
        """Test that results are deterministic."""
        tour1, cost1 = nearest_neighbor_tsp(square_graph, start_station='A')
        tour2, cost2 = nearest_neighbor_tsp(square_graph, start_station='A')

        assert tour1 == tour2
        assert cost1 == cost2

    def test_different_start_stations(self, simple_triangle):
        """Test that different start stations may produce different tours."""
        tour_a, cost_a = nearest_neighbor_tsp(simple_triangle, start_station='A')
        tour_b, cost_b = nearest_neighbor_tsp(simple_triangle, start_station='B')
        tour_c, cost_c = nearest_neighbor_tsp(simple_triangle, start_station='C')

        # All should visit all nodes
        assert set(tour_a) == set(tour_b) == set(tour_c) == {'A', 'B', 'C'}

        # Should start at different stations
        assert tour_a[0] == 'A'
        assert tour_b[0] == 'B'
        assert tour_c[0] == 'C'

    def test_empty_graph(self):
        """Test that empty graph raises error."""
        G = nx.Graph()

        with pytest.raises(ValueError, match="Graph is empty"):
            nearest_neighbor_tsp(G)

    def test_invalid_start_station(self, simple_triangle):
        """Test that invalid start station raises error."""
        with pytest.raises(ValueError, match="not in graph"):
            nearest_neighbor_tsp(simple_triangle, start_station='X')

    def test_disconnected_graph(self):
        """Test that disconnected graph raises error."""
        G = nx.Graph()
        # Two separate components
        G.add_edge('A', 'B', weight=1.0)
        G.add_edge('C', 'D', weight=1.0)

        with pytest.raises(ValueError, match="not connected"):
            nearest_neighbor_tsp(G, start_station='A')

    def test_single_node(self):
        """Test graph with single node."""
        G = nx.Graph()
        G.add_node('A')

        tour, cost = nearest_neighbor_tsp(G, start_station='A')

        assert tour == ['A']
        assert cost == 0.0  # No edges to traverse

    def test_two_nodes(self):
        """Test graph with two nodes."""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=5.0)

        tour, cost = nearest_neighbor_tsp(G, start_station='A')

        assert len(tour) == 2
        assert set(tour) == {'A', 'B'}
        assert tour[0] == 'A'
        # Cost is A->B + B->A = 5.0 + 5.0 = 10.0
        assert cost == 10.0

    def test_complete_graph(self):
        """Test on a complete graph."""
        G = nx.complete_graph(5)
        for u, v in G.edges():
            G[u][v]['weight'] = 1.0

        tour, cost = nearest_neighbor_tsp(G, start_station=0)

        # Should visit all 5 nodes
        assert len(tour) == 5
        assert set(tour) == {0, 1, 2, 3, 4}

        # Cost should be 5.0 (5 edges with weight 1.0 each)
        assert cost == 5.0

    def test_validate_result_flag(self, simple_triangle):
        """Test that validate_result flag works."""
        # Should not raise error with validation
        tour, cost = nearest_neighbor_tsp(
            simple_triangle,
            start_station='A',
            validate_result=True
        )
        assert len(tour) == 3

        # Should also work without validation
        tour, cost = nearest_neighbor_tsp(
            simple_triangle,
            start_station='A',
            validate_result=False
        )
        assert len(tour) == 3


class TestNearestNeighborMultiStart:
    """Test suite for nearest_neighbor_multi_start function."""

    def test_multi_start_finds_best(self, square_graph):
        """Test that multi-start finds best among starting points."""
        tour, cost, best_start = nearest_neighbor_multi_start(
            square_graph,
            num_starts=4
        )

        # Should return valid tour
        assert len(tour) == 4
        assert set(tour) == {'A', 'B', 'C', 'D'}

        # Should return best starting station
        assert best_start in square_graph.nodes()

    def test_multi_start_with_specific_stations(self, simple_triangle):
        """Test multi-start with specific starting stations."""
        tour, cost, best_start = nearest_neighbor_multi_start(
            simple_triangle,
            start_stations=['A', 'B']
        )

        # Should try only A and B
        assert best_start in ['A', 'B']
        assert len(tour) == 3

    def test_multi_start_default_num_starts(self, square_graph):
        """Test that default num_starts works."""
        tour, cost, best_start = nearest_neighbor_multi_start(square_graph)

        assert len(tour) == 4
        assert cost > 0

    def test_multi_start_more_starts_than_nodes(self):
        """Test when num_starts > number of nodes."""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1.0)
        G.add_edge('B', 'C', weight=1.0)
        G.add_edge('C', 'A', weight=1.0)

        # Request 10 starts but only 3 nodes exist
        tour, cost, best_start = nearest_neighbor_multi_start(G, num_starts=10)

        # Should only try 3 starts
        assert len(tour) == 3

    def test_multi_start_empty_graph(self):
        """Test that empty graph raises error."""
        G = nx.Graph()

        with pytest.raises(ValueError, match="Graph is empty"):
            nearest_neighbor_multi_start(G)

    def test_multi_start_invalid_station_list(self, simple_triangle):
        """Test that invalid station in list raises error."""
        with pytest.raises(ValueError, match="not in graph"):
            nearest_neighbor_multi_start(
                simple_triangle,
                start_stations=['A', 'X']
            )

    def test_multi_start_deterministic(self, square_graph):
        """Test that multi-start is deterministic."""
        tour1, cost1, start1 = nearest_neighbor_multi_start(
            square_graph,
            num_starts=4
        )
        tour2, cost2, start2 = nearest_neighbor_multi_start(
            square_graph,
            num_starts=4
        )

        assert tour1 == tour2
        assert cost1 == cost2
        assert start1 == start2

    def test_multi_start_better_than_single(self):
        """Test that multi-start can find better solutions."""
        # Create asymmetric graph where starting point matters
        G = nx.Graph()
        G.add_edge('A', 'B', weight=10.0)
        G.add_edge('B', 'C', weight=1.0)
        G.add_edge('C', 'D', weight=1.0)
        G.add_edge('D', 'A', weight=1.0)
        G.add_edge('A', 'C', weight=5.0)
        G.add_edge('B', 'D', weight=5.0)

        # Single start from A
        tour_a, cost_a = nearest_neighbor_tsp(G, start_station='A')

        # Multi-start
        tour_multi, cost_multi, _ = nearest_neighbor_multi_start(
            G,
            start_stations=['A', 'B', 'C', 'D']
        )

        # Multi-start should be at least as good as single start
        assert cost_multi <= cost_a


class TestNearestNeighborWith2Opt:
    """Test suite for nearest_neighbor_with_2opt function."""

    def test_combined_algorithm(self, square_graph):
        """Test combined Nearest Neighbor + 2-opt."""
        tour, initial_cost, final_cost = nearest_neighbor_with_2opt(
            square_graph,
            start_station='A'
        )

        # Should return valid tour
        assert len(tour) == 4
        assert set(tour) == {'A', 'B', 'C', 'D'}

        # 2-opt should not increase cost
        assert final_cost <= initial_cost

    def test_improvement_from_2opt(self):
        """Test that 2-opt improves the solution."""
        # Create graph where NN gives suboptimal solution
        G = nx.Graph()
        G.add_edge('A', 'B', weight=1.0)
        G.add_edge('B', 'C', weight=1.0)
        G.add_edge('C', 'D', weight=1.0)
        G.add_edge('D', 'A', weight=1.0)
        G.add_edge('A', 'C', weight=2.0)
        G.add_edge('B', 'D', weight=2.0)

        tour, initial_cost, final_cost = nearest_neighbor_with_2opt(G)

        # 2-opt should improve or maintain cost
        assert final_cost <= initial_cost

    def test_verbose_output(self, square_graph, capsys):
        """Test verbose output mode."""
        nearest_neighbor_with_2opt(
            square_graph,
            start_station='A',
            verbose=True
        )

        captured = capsys.readouterr()
        assert "Generating initial tour" in captured.out
        assert "Initial tour cost" in captured.out
        assert "Final Results" in captured.out

    def test_max_iterations_parameter(self, square_graph):
        """Test that max_iterations is passed to 2-opt."""
        tour, initial_cost, final_cost = nearest_neighbor_with_2opt(
            square_graph,
            max_iterations=1
        )

        # Should complete without error
        assert len(tour) == 4

    def test_improvement_threshold_parameter(self, square_graph):
        """Test that improvement_threshold is passed to 2-opt."""
        tour, initial_cost, final_cost = nearest_neighbor_with_2opt(
            square_graph,
            improvement_threshold=10.0  # High threshold
        )

        # Should complete without error
        assert len(tour) == 4

    def test_default_start_station(self, square_graph):
        """Test with default (None) start station."""
        tour, initial_cost, final_cost = nearest_neighbor_with_2opt(square_graph)

        assert len(tour) == 4
        assert final_cost <= initial_cost


class TestNearestNeighborIntegration:
    """Integration tests for Nearest Neighbor algorithms."""

    def test_complete_workflow(self):
        """Test complete workflow from graph loading to optimization."""
        from src.utils.tour import calculate_tour_cost, validate_tour

        # Create test graph
        G = nx.Graph()
        for i in range(5):
            for j in range(i + 1, 5):
                G.add_edge(i, j, weight=abs(i - j))

        # Generate initial tour
        tour, cost = nearest_neighbor_tsp(G, start_station=0)

        # Validate tour
        validate_tour(tour, G, require_complete=True)

        # Verify cost
        actual_cost = calculate_tour_cost(tour, G)
        assert abs(actual_cost - cost) < 1e-10

    def test_nn_then_manual_2opt(self, square_graph):
        """Test using NN to generate initial solution for manual 2-opt."""
        from src.solvers.two_opt import improve_tour_2opt

        # Generate initial solution with NN
        initial_tour, initial_cost = nearest_neighbor_tsp(
            square_graph,
            start_station='A'
        )

        # Manually improve with 2-opt
        improved_tour, reported_initial, improved_cost = improve_tour_2opt(
            initial_tour,
            square_graph
        )

        # Costs should match
        assert abs(reported_initial - initial_cost) < 1e-10

        # Should not increase cost
        assert improved_cost <= initial_cost

    @pytest.mark.slow
    def test_performance_on_larger_graph(self):
        """Test performance on a larger graph."""
        import time

        # Create larger graph (50 nodes)
        n = 50
        G = nx.complete_graph(n)

        import random
        random.seed(42)
        for u, v in G.edges():
            G[u][v]['weight'] = random.uniform(1.0, 10.0)

        # Test that NN completes in reasonable time
        start_time = time.time()
        tour, cost = nearest_neighbor_tsp(G, start_station=0)
        elapsed = time.time() - start_time

        # Should complete in under 1 second for 50 nodes
        assert elapsed < 1.0

        # Should visit all nodes
        assert len(tour) == n
        assert set(tour) == set(range(n))
