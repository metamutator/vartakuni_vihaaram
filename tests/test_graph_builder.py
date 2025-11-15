#!/usr/bin/env python3
"""
Unit tests for the graph builder module.

Tests cover:
- CSV parsing
- Graph construction
- Connectivity validation
- Edge weight assignment
- Multi-line station handling
"""

import pytest
import tempfile
import csv
from pathlib import Path
import networkx as nx
from src.graph.builder import MetroGraphBuilder, build_singapore_metro_graph


class TestMetroGraphBuilder:
    """Test suite for MetroGraphBuilder class."""

    @pytest.fixture
    def sample_stations_csv(self, tmp_path):
        """Create a sample stations CSV file for testing."""
        stations_file = tmp_path / "stations.csv"
        with open(stations_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'station_id', 'station_name', 'line_code',
                'latitude', 'longitude', 'operational_status'
            ])
            writer.writeheader()
            writer.writerows([
                {'station_id': 'NS1', 'station_name': 'Jurong East', 'line_code': 'NS',
                 'latitude': '1.3330', 'longitude': '103.7421', 'operational_status': 'active'},
                {'station_id': 'NS2', 'station_name': 'Bukit Batok', 'line_code': 'NS',
                 'latitude': '1.3490', 'longitude': '103.7497', 'operational_status': 'active'},
                {'station_id': 'NS3', 'station_name': 'Bukit Gombak', 'line_code': 'NS',
                 'latitude': '1.3587', 'longitude': '103.7518', 'operational_status': 'active'},
                {'station_id': 'EW24', 'station_name': 'Jurong East', 'line_code': 'EW',
                 'latitude': '1.3330', 'longitude': '103.7421', 'operational_status': 'active'},
            ])
        return stations_file

    @pytest.fixture
    def sample_lines_csv(self, tmp_path):
        """Create a sample lines CSV file for testing."""
        lines_file = tmp_path / "lines.csv"
        with open(lines_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'line_code', 'line_name', 'color_hex', 'line_type'
            ])
            writer.writeheader()
            writer.writerows([
                {'line_code': 'NS', 'line_name': 'North-South Line',
                 'color_hex': '#D42E12', 'line_type': 'mrt'},
                {'line_code': 'EW', 'line_name': 'East-West Line',
                 'color_hex': '#009645', 'line_type': 'mrt'},
            ])
        return lines_file

    @pytest.fixture
    def sample_connections_csv(self, tmp_path):
        """Create a sample connections CSV file for testing."""
        connections_file = tmp_path / "connections.csv"
        with open(connections_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'connection_id', 'from_station_id', 'to_station_id',
                'connection_type', 'travel_time_minutes', 'distance_meters', 'line_code'
            ])
            writer.writeheader()
            writer.writerows([
                {'connection_id': '1', 'from_station_id': 'NS1', 'to_station_id': 'NS2',
                 'connection_type': 'train', 'travel_time_minutes': '2.5', 'distance_meters': '1500', 'line_code': 'NS'},
                {'connection_id': '2', 'from_station_id': 'NS2', 'to_station_id': 'NS1',
                 'connection_type': 'train', 'travel_time_minutes': '2.5', 'distance_meters': '1500', 'line_code': 'NS'},
                {'connection_id': '3', 'from_station_id': 'NS2', 'to_station_id': 'NS3',
                 'connection_type': 'train', 'travel_time_minutes': '3.0', 'distance_meters': '1800', 'line_code': 'NS'},
                {'connection_id': '4', 'from_station_id': 'NS3', 'to_station_id': 'NS2',
                 'connection_type': 'train', 'travel_time_minutes': '3.0', 'distance_meters': '1800', 'line_code': 'NS'},
                {'connection_id': '5', 'from_station_id': 'NS1', 'to_station_id': 'EW24',
                 'connection_type': 'walk_transfer', 'travel_time_minutes': '3.0', 'distance_meters': '0', 'line_code': ''},
                {'connection_id': '6', 'from_station_id': 'EW24', 'to_station_id': 'NS1',
                 'connection_type': 'walk_transfer', 'travel_time_minutes': '3.0', 'distance_meters': '0', 'line_code': ''},
            ])
        return connections_file

    @pytest.fixture
    def builder(self):
        """Create a fresh MetroGraphBuilder instance."""
        return MetroGraphBuilder()

    def test_init(self, builder):
        """Test that builder initializes with empty data structures."""
        assert isinstance(builder.graph, nx.Graph)
        assert builder.graph.number_of_nodes() == 0
        assert builder.graph.number_of_edges() == 0
        assert len(builder.stations) == 0
        assert len(builder.lines) == 0
        assert len(builder.connections) == 0

    def test_load_stations(self, builder, sample_stations_csv):
        """Test loading stations from CSV."""
        builder.load_stations(sample_stations_csv)

        # Check stations loaded
        assert len(builder.stations) == 4
        assert 'NS1' in builder.stations
        assert builder.stations['NS1']['name'] == 'Jurong East'

        # Check graph nodes created
        assert builder.graph.number_of_nodes() == 4
        assert 'NS1' in builder.graph.nodes()

        # Check node attributes
        node_data = builder.graph.nodes['NS1']
        assert node_data['name'] == 'Jurong East'
        assert node_data['line_code'] == 'NS'
        assert node_data['latitude'] == 1.3330
        assert node_data['longitude'] == 103.7421

    def test_load_stations_file_not_found(self, builder, tmp_path):
        """Test that loading non-existent file raises error."""
        non_existent = tmp_path / "does_not_exist.csv"
        with pytest.raises(FileNotFoundError):
            builder.load_stations(non_existent)

    def test_load_lines(self, builder, sample_lines_csv):
        """Test loading line metadata from CSV."""
        builder.load_lines(sample_lines_csv)

        assert len(builder.lines) == 2
        assert 'NS' in builder.lines
        assert builder.lines['NS']['name'] == 'North-South Line'
        assert builder.lines['NS']['color'] == '#D42E12'
        assert builder.lines['NS']['type'] == 'mrt'

    def test_load_connections(self, builder, sample_stations_csv, sample_connections_csv):
        """Test loading connections and creating graph edges."""
        # Must load stations first
        builder.load_stations(sample_stations_csv)
        builder.load_connections(sample_connections_csv)

        # Check connections loaded (6 bidirectional rows in CSV)
        assert len(builder.connections) == 6

        # Check graph edges created (3 undirected edges for 6 bidirectional connections)
        assert builder.graph.number_of_edges() == 3
        assert builder.graph.has_edge('NS1', 'NS2')
        assert builder.graph.has_edge('NS1', 'EW24')

        # Check edge attributes (weight = travel time)
        edge_data = builder.graph['NS1']['NS2']
        assert edge_data['weight'] == 2.5
        assert edge_data['connection_type'] == 'train'
        assert edge_data['distance_meters'] == 1500

        # Check walking edge
        walk_edge = builder.graph['NS1']['EW24']
        assert walk_edge['weight'] == 3.0
        assert walk_edge['connection_type'] == 'walk_transfer'
        assert walk_edge['distance_meters'] == 0

    def test_load_connections_invalid_station(self, builder, sample_stations_csv, tmp_path):
        """Test that connections with invalid station IDs raise error."""
        builder.load_stations(sample_stations_csv)

        # Create connections with invalid station
        bad_connections = tmp_path / "bad_connections.csv"
        with open(bad_connections, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'connection_id', 'from_station_id', 'to_station_id',
                'connection_type', 'travel_time_minutes', 'distance_meters', 'line_code'
            ])
            writer.writeheader()
            writer.writerow({
                'connection_id': '1', 'from_station_id': 'NS1', 'to_station_id': 'INVALID',
                'connection_type': 'train', 'travel_time_minutes': '2.5',
                'distance_meters': '1500', 'line_code': 'NS'
            })

        with pytest.raises(ValueError, match="Unknown station"):
            builder.load_connections(bad_connections)

    def test_build_graph(self, builder, sample_stations_csv, sample_connections_csv, sample_lines_csv):
        """Test complete graph building process."""
        graph = builder.build_graph(
            sample_stations_csv,
            sample_connections_csv,
            sample_lines_csv
        )

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 4
        assert graph.number_of_edges() == 3  # 3 undirected edges from 6 bidirectional connections
        assert len(builder.lines) == 2

    def test_validate_connectivity_connected(self, builder, sample_stations_csv, sample_connections_csv):
        """Test connectivity validation on a connected graph."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        is_connected, components = builder.validate_connectivity()

        assert is_connected is True
        assert len(components) == 0

    def test_validate_connectivity_disconnected(self, builder, sample_stations_csv, tmp_path):
        """Test connectivity validation on a disconnected graph."""
        builder.load_stations(sample_stations_csv)

        # Create connections that leave EW24 disconnected
        disconnected_connections = tmp_path / "disconnected.csv"
        with open(disconnected_connections, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'connection_id', 'from_station_id', 'to_station_id',
                'connection_type', 'travel_time_minutes', 'distance_meters', 'line_code'
            ])
            writer.writeheader()
            writer.writerows([
                {'connection_id': '1', 'from_station_id': 'NS1', 'to_station_id': 'NS2',
                 'connection_type': 'train', 'travel_time_minutes': '2.5',
                 'distance_meters': '1500', 'line_code': 'NS'},
                {'connection_id': '2', 'from_station_id': 'NS2', 'to_station_id': 'NS1',
                 'connection_type': 'train', 'travel_time_minutes': '2.5',
                 'distance_meters': '1500', 'line_code': 'NS'},
            ])

        builder.load_connections(disconnected_connections)

        is_connected, components = builder.validate_connectivity()

        assert is_connected is False
        assert len(components) > 0

    def test_validate_connectivity_empty_graph(self, builder):
        """Test that validating empty graph raises error."""
        with pytest.raises(ValueError, match="Graph is empty"):
            builder.validate_connectivity()

    def test_get_graph(self, builder, sample_stations_csv, sample_connections_csv):
        """Test getting the constructed graph."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        graph = builder.get_graph()

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() > 0

    def test_get_graph_empty(self, builder):
        """Test that getting graph before building raises error."""
        with pytest.raises(ValueError, match="Graph is empty"):
            builder.get_graph()

    def test_get_station_info(self, builder, sample_stations_csv):
        """Test getting station information."""
        builder.load_stations(sample_stations_csv)

        info = builder.get_station_info('NS1')

        assert info['name'] == 'Jurong East'
        assert info['line_code'] == 'NS'
        assert info['latitude'] == 1.3330

    def test_get_station_info_not_found(self, builder, sample_stations_csv):
        """Test getting non-existent station raises error."""
        builder.load_stations(sample_stations_csv)

        with pytest.raises(ValueError, match="Station not found"):
            builder.get_station_info('INVALID')

    def test_get_neighbors(self, builder, sample_stations_csv, sample_connections_csv):
        """Test getting neighboring stations."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        neighbors = builder.get_neighbors('NS1')

        # NS1 connects to NS2 and EW24
        assert len(neighbors) == 2

        # Check sorted by travel time
        neighbor_ids = [n[0] for n in neighbors]
        assert 'NS2' in neighbor_ids
        assert 'EW24' in neighbor_ids

        # Check travel times
        for neighbor_id, travel_time in neighbors:
            assert travel_time > 0

    def test_get_neighbors_not_found(self, builder, sample_stations_csv, sample_connections_csv):
        """Test getting neighbors of non-existent station."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        with pytest.raises(ValueError, match="Station not found"):
            builder.get_neighbors('INVALID')

    def test_get_shortest_path(self, builder, sample_stations_csv, sample_connections_csv):
        """Test finding shortest path between stations."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        path, length = builder.get_shortest_path('NS1', 'NS3')

        # Should be NS1 -> NS2 -> NS3
        assert path == ['NS1', 'NS2', 'NS3']
        assert length == 5.5  # 2.5 + 3.0

    def test_get_shortest_path_invalid_start(self, builder, sample_stations_csv, sample_connections_csv):
        """Test shortest path with invalid start station."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        with pytest.raises(ValueError, match="Start station not found"):
            builder.get_shortest_path('INVALID', 'NS3')

    def test_get_shortest_path_invalid_end(self, builder, sample_stations_csv, sample_connections_csv):
        """Test shortest path with invalid end station."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        with pytest.raises(ValueError, match="End station not found"):
            builder.get_shortest_path('NS1', 'INVALID')

    def test_get_graph_stats(self, builder, sample_stations_csv, sample_connections_csv, sample_lines_csv):
        """Test graph statistics calculation."""
        builder.build_graph(sample_stations_csv, sample_connections_csv, sample_lines_csv)

        stats = builder.get_graph_stats()

        assert stats['num_stations'] == 4
        assert stats['num_connections'] == 3  # 3 undirected edges
        assert stats['is_connected'] is True
        assert stats['num_lines'] == 2
        assert 'train' in stats['connection_types']
        assert 'walk_transfer' in stats['connection_types']
        assert stats['average_degree'] > 0
        assert 'diameter' in stats
        assert 'average_clustering' in stats

    def test_get_graph_stats_empty(self, builder):
        """Test graph statistics on empty graph."""
        stats = builder.get_graph_stats()

        assert stats['num_stations'] == 0
        assert stats['num_connections'] == 0
        assert stats['is_connected'] is False

    def test_graph_is_undirected(self, builder, sample_stations_csv, sample_connections_csv):
        """Test that constructed graph is undirected."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        # NetworkX Graph is undirected by default
        assert not builder.graph.is_directed()

        # Check that edges exist in both directions
        if builder.graph.has_edge('NS1', 'NS2'):
            assert builder.graph.has_edge('NS2', 'NS1')

    def test_multi_line_stations_separate_nodes(self, builder, sample_stations_csv):
        """Test that multi-line stations create separate nodes."""
        builder.load_stations(sample_stations_csv)

        # Jurong East has two platforms: NS1 and EW24
        assert 'NS1' in builder.graph.nodes()
        assert 'EW24' in builder.graph.nodes()

        # They should be at the same location
        ns1_data = builder.graph.nodes['NS1']
        ew24_data = builder.graph.nodes['EW24']

        assert ns1_data['latitude'] == ew24_data['latitude']
        assert ns1_data['longitude'] == ew24_data['longitude']
        assert ns1_data['name'] == ew24_data['name']

    def test_edge_weights_are_travel_times(self, builder, sample_stations_csv, sample_connections_csv):
        """Test that edge weights are set to travel times."""
        builder.build_graph(sample_stations_csv, sample_connections_csv)

        # Get edge data
        edge_data = builder.graph['NS1']['NS2']

        # Weight should equal travel_time_minutes
        assert edge_data['weight'] == 2.5


class TestBuildSingaporeMetroGraph:
    """Test the convenience function for building Singapore MRT/LRT graph."""

    def test_build_singapore_metro_graph(self, tmp_path):
        """Test building graph from data directory."""
        import shutil

        # Create sample data files
        data_dir = tmp_path / 'raw'
        data_dir.mkdir(parents=True)

        # Create stations.csv
        with open(data_dir / 'stations.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'station_id', 'station_name', 'line_code',
                'latitude', 'longitude', 'operational_status'
            ])
            writer.writeheader()
            writer.writerows([
                {'station_id': 'NS1', 'station_name': 'Jurong East', 'line_code': 'NS',
                 'latitude': '1.3330', 'longitude': '103.7421', 'operational_status': 'active'},
                {'station_id': 'NS2', 'station_name': 'Bukit Batok', 'line_code': 'NS',
                 'latitude': '1.3490', 'longitude': '103.7497', 'operational_status': 'active'},
            ])

        # Create connections.csv
        with open(data_dir / 'connections.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'connection_id', 'from_station_id', 'to_station_id',
                'connection_type', 'travel_time_minutes', 'distance_meters', 'line_code'
            ])
            writer.writeheader()
            writer.writerows([
                {'connection_id': '1', 'from_station_id': 'NS1', 'to_station_id': 'NS2',
                 'connection_type': 'train', 'travel_time_minutes': '2.5', 'distance_meters': '1500', 'line_code': 'NS'},
                {'connection_id': '2', 'from_station_id': 'NS2', 'to_station_id': 'NS1',
                 'connection_type': 'train', 'travel_time_minutes': '2.5', 'distance_meters': '1500', 'line_code': 'NS'},
            ])

        # Create lines.csv
        with open(data_dir / 'lines.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'line_code', 'line_name', 'color_hex', 'line_type'
            ])
            writer.writeheader()
            writer.writerows([
                {'line_code': 'NS', 'line_name': 'North-South Line',
                 'color_hex': '#D42E12', 'line_type': 'mrt'},
            ])

        # Build graph (suppress output)
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            graph = build_singapore_metro_graph(data_dir)
        finally:
            sys.stdout = old_stdout

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() == 2
        assert graph.number_of_edges() == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
