#!/usr/bin/env python3
"""
Unit tests for Nearest Neighbor TSP algorithm (US-301)

Tests cover:
- Basic functionality
- Determinism
- Performance requirements
- Edge cases
- Invalid inputs
"""

import pytest
import networkx as nx
import time
from src.solvers.nearest_neighbor import nearest_neighbor_tsp, nearest_neighbor_tsp_with_stats


class TestNearestNeighborTSP:
    """Test suite for Nearest Neighbor TSP algorithm."""

    @pytest.fixture
    def simple_graph(self):
        """Create a simple 4-node graph for testing."""
        G = nx.Graph()
        G.add_node('A')
        G.add_node('B')
        G.add_node('C')
        G.add_node('D')

        # Create a square with diagonal
        G.add_edge('A', 'B', weight=1.0)
        G.add_edge('B', 'C', weight=1.0)
        G.add_edge('C', 'D', weight=1.0)
        G.add_edge('D', 'A', weight=1.0)
        G.add_edge('A', 'C', weight=1.5)
        G.add_edge('B', 'D', weight=1.5)

        return G

    @pytest.fixture
    def triangle_graph(self):
        """Create a 3-node triangle graph."""
        G = nx.Graph()
        G.add_node('X')
        G.add_node('Y')
        G.add_node('Z')

        G.add_edge('X', 'Y', weight=2.0)
        G.add_edge('Y', 'Z', weight=3.0)
        G.add_edge('Z', 'X', weight=4.0)

        return G

    @pytest.fixture
    def line_graph(self):
        """Create a linear graph (worst case for NN)."""
        G = nx.Graph()
        for i in range(5):
            G.add_node(str(i))

        for i in range(4):
            G.add_edge(str(i), str(i+1), weight=1.0)

        return G

    def test_accepts_graph_and_starting_station(self, simple_graph):
        """Test that function accepts graph and starting station."""
        tour, total_time = nearest_neighbor_tsp(simple_graph, 'A')

        assert isinstance(tour, list)
        assert isinstance(total_time, (int, float))
        assert len(tour) > 0

    def test_returns_tour_and_total_time(self, simple_graph):
        """Test that function returns tour and total time."""
        tour, total_time = nearest_neighbor_tsp(simple_graph, 'A')

        # Tour should contain all nodes
        assert set(tour[:-1]) == set(simple_graph.nodes())  # Exclude last (return to start)

        # Total time should be positive
        assert total_time > 0

    def test_tour_visits_all_stations(self, simple_graph):
        """Test that tour visits all stations exactly once."""
        tour, total_time = nearest_neighbor_tsp(simple_graph, 'A')

        # Remove last station (return to start)
        tour_without_return = tour[:-1]

        # All nodes should be in tour
        assert set(tour_without_return) == set(simple_graph.nodes())

        # Each node visited exactly once (except start/end)
        assert len(tour_without_return) == len(set(tour_without_return))

    def test_tour_starts_and_ends_at_same_station(self, simple_graph):
        """Test that tour is a cycle (starts and ends at same station)."""
        tour, total_time = nearest_neighbor_tsp(simple_graph, 'B')

        assert tour[0] == 'B'
        assert tour[-1] == 'B'

    def test_deterministic_results(self, simple_graph):
        """Test that algorithm produces deterministic results."""
        tour1, time1 = nearest_neighbor_tsp(simple_graph, 'A')
        tour2, time2 = nearest_neighbor_tsp(simple_graph, 'A')
        tour3, time3 = nearest_neighbor_tsp(simple_graph, 'A')

        # Same results every time
        assert tour1 == tour2 == tour3
        assert time1 == time2 == time3

    def test_different_starting_stations(self, triangle_graph):
        """Test with different starting stations."""
        tour_x, time_x = nearest_neighbor_tsp(triangle_graph, 'X')
        tour_y, time_y = nearest_neighbor_tsp(triangle_graph, 'Y')
        tour_z, time_z = nearest_neighbor_tsp(triangle_graph, 'Z')

        # All should visit all nodes
        assert set(tour_x[:-1]) == {'X', 'Y', 'Z'}
        assert set(tour_y[:-1]) == {'X', 'Y', 'Z'}
        assert set(tour_z[:-1]) == {'X', 'Y', 'Z'}

        # Tours should start at specified stations
        assert tour_x[0] == 'X'
        assert tour_y[0] == 'Y'
        assert tour_z[0] == 'Z'

    def test_total_time_calculation(self, triangle_graph):
        """Test that total time is calculated correctly."""
        # For triangle: X -2-> Y -3-> Z -4-> X
        # Starting from X, nearest neighbor gives: X -> Y (2) -> Z (3) -> X (4) = 9
        tour, total_time = nearest_neighbor_tsp(triangle_graph, 'X')

        # Verify tour
        assert tour == ['X', 'Y', 'Z', 'X']

        # Verify total time
        assert total_time == 9.0

    def test_empty_graph_raises_error(self):
        """Test that empty graph raises ValueError."""
        G = nx.Graph()

        with pytest.raises(ValueError, match="Graph is empty"):
            nearest_neighbor_tsp(G, 'A')

    def test_invalid_start_station_raises_error(self, simple_graph):
        """Test that invalid start station raises ValueError."""
        with pytest.raises(ValueError, match="not found in graph"):
            nearest_neighbor_tsp(simple_graph, 'INVALID')

    def test_single_node_graph(self):
        """Test with a graph containing only one node."""
        G = nx.Graph()
        G.add_node('ONLY')

        tour, total_time = nearest_neighbor_tsp(G, 'ONLY')

        assert tour == ['ONLY', 'ONLY']
        assert total_time == 0.0

    def test_two_node_graph(self):
        """Test with a graph containing two nodes."""
        G = nx.Graph()
        G.add_edge('A', 'B', weight=5.0)

        tour, total_time = nearest_neighbor_tsp(G, 'A')

        assert tour == ['A', 'B', 'A']
        assert total_time == 10.0  # 5 + 5

    def test_performance_small_graph(self, simple_graph):
        """Test that algorithm runs quickly on small graph."""
        start_time = time.time()
        tour, total_time = nearest_neighbor_tsp(simple_graph, 'A')
        elapsed = time.time() - start_time

        # Should be nearly instantaneous for 4 nodes
        assert elapsed < 0.1

    def test_with_stats_function(self, simple_graph):
        """Test the with_stats variant."""
        tour, total_time, stats = nearest_neighbor_tsp_with_stats(simple_graph, 'A')

        # Verify stats
        assert 'computation_time_seconds' in stats
        assert 'num_stations' in stats
        assert 'algorithm' in stats
        assert 'deterministic' in stats

        assert stats['algorithm'] == 'Nearest Neighbor'
        assert stats['deterministic'] is True
        assert stats['num_stations'] == 4
        assert stats['computation_time_seconds'] >= 0

    def test_greedy_selection(self, simple_graph):
        """Test that algorithm makes greedy (nearest neighbor) choices."""
        # Starting from A in simple_graph
        # A has edges to B (1.0), D (1.0), C (1.5)
        # NN should pick B or D first (both are 1.0)

        tour, total_time = nearest_neighbor_tsp(simple_graph, 'A')

        # Second node should be B or D (both distance 1.0 from A)
        assert tour[1] in ['B', 'D']

    def test_tour_validity_on_line_graph(self, line_graph):
        """Test tour validity on a linear graph."""
        tour, total_time = nearest_neighbor_tsp(line_graph, '0')

        # Should visit all 5 nodes
        assert len(set(tour[:-1])) == 5

        # Should start and end at '0'
        assert tour[0] == '0'
        assert tour[-1] == '0'

        # Total time should account for going down the line and back
        assert total_time > 0


class TestNearestNeighborOnRealData:
    """Test Nearest Neighbor on Singapore MRT data (if available)."""

    @pytest.fixture
    def singapore_graph(self):
        """Load Singapore MRT graph for real-world testing."""
        try:
            from pathlib import Path
            from src.graph.builder import build_singapore_metro_graph

            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / 'data' / 'raw'

            if not data_dir.exists():
                pytest.skip("Singapore MRT data not available")

            graph = build_singapore_metro_graph(data_dir)
            return graph
        except Exception as e:
            pytest.skip(f"Could not load Singapore MRT data: {e}")

    def test_performance_on_real_data(self, singapore_graph):
        """Test that algorithm runs in < 5 seconds on 214 stations."""
        # Pick a starting station
        start_station = list(singapore_graph.nodes())[0]

        start_time = time.time()
        tour, total_time = nearest_neighbor_tsp(singapore_graph, start_station)
        elapsed = time.time() - start_time

        # Should complete in < 5 seconds (requirement from US-301)
        assert elapsed < 5.0, f"Algorithm took {elapsed:.2f}s, exceeds 5s requirement"

        # Should visit all stations
        assert len(set(tour[:-1])) == singapore_graph.number_of_nodes()

        print(f"\n✓ Nearest Neighbor on {singapore_graph.number_of_nodes()} stations:")
        print(f"  Computation time: {elapsed:.3f}s")
        print(f"  Total travel time: {total_time:.2f} minutes")
        print(f"  Stations visited: {len(set(tour[:-1]))}")

    def test_determinism_on_real_data(self, singapore_graph):
        """Test determinism on real data."""
        start_station = list(singapore_graph.nodes())[0]

        tour1, time1 = nearest_neighbor_tsp(singapore_graph, start_station)
        tour2, time2 = nearest_neighbor_tsp(singapore_graph, start_station)

        assert tour1 == tour2
        assert time1 == time2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
