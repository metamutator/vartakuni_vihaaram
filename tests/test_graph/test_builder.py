"""Tests for graph builder module."""

import pytest
import networkx as nx
import tempfile
import os
from pathlib import Path
from src.graph.builder import build_network_graph, load_default_graph, _validate_graph
import pandas as pd


class TestBuildNetworkGraph:
    """Test suite for build_network_graph function."""

    @pytest.fixture
    def sample_data_files(self):
        """Create temporary CSV files for testing."""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Create sample stations CSV
        stations_data = """station_id,station_name,line_code,latitude,longitude,operational_status
NS1,Marina Bay,NS,1.282,103.857,active
NS2,Raffles Place,NS,1.284,103.851,active
EW1,Pasir Ris,EW,1.373,103.949,active
"""
        stations_file = os.path.join(temp_dir, "stations.csv")
        with open(stations_file, 'w') as f:
            f.write(stations_data)

        # Create sample connections CSV
        connections_data = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
0001,NS1,NS2,train,1.5,600,NS
0002,NS2,NS1,train,1.5,600,NS
0003,NS2,EW1,train,2.0,800,NS
0004,EW1,NS2,train,2.0,800,EW
"""
        connections_file = os.path.join(temp_dir, "connections.csv")
        with open(connections_file, 'w') as f:
            f.write(connections_data)

        yield stations_file, connections_file

        # Cleanup
        os.remove(stations_file)
        os.remove(connections_file)
        os.rmdir(temp_dir)

    def test_build_graph_success(self, sample_data_files):
        """Test successful graph construction."""
        stations_file, connections_file = sample_data_files

        G = build_network_graph(stations_file, connections_file)

        # Check nodes
        assert G.number_of_nodes() == 3
        assert 'NS1' in G.nodes()
        assert 'NS2' in G.nodes()
        assert 'EW1' in G.nodes()

        # Check edges (undirected graph, so should have 2 edges)
        assert G.number_of_edges() == 2

        # Check node attributes
        assert G.nodes['NS1']['name'] == 'Marina Bay'
        assert G.nodes['NS1']['line_code'] == 'NS'
        assert 'latitude' in G.nodes['NS1']

        # Check edge weights
        assert G['NS1']['NS2']['weight'] == 1.5
        assert G['NS2']['EW1']['weight'] == 2.0

    def test_missing_stations_file(self):
        """Test error when stations file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Stations file not found"):
            build_network_graph("nonexistent_stations.csv", "connections.csv")

    def test_missing_connections_file(self, sample_data_files):
        """Test error when connections file doesn't exist."""
        stations_file, _ = sample_data_files

        with pytest.raises(FileNotFoundError, match="Connections file not found"):
            build_network_graph(stations_file, "nonexistent_connections.csv")

    def test_missing_required_station_columns(self):
        """Test error when stations CSV is missing required columns."""
        temp_dir = tempfile.mkdtemp()

        # Create invalid stations CSV (missing line_code)
        stations_data = """station_id,station_name
NS1,Marina Bay
"""
        stations_file = os.path.join(temp_dir, "stations.csv")
        with open(stations_file, 'w') as f:
            f.write(stations_data)

        # Create minimal connections CSV
        connections_data = """from_station_id,to_station_id,travel_time_minutes
NS1,NS2,1.5
"""
        connections_file = os.path.join(temp_dir, "connections.csv")
        with open(connections_file, 'w') as f:
            f.write(connections_data)

        with pytest.raises(ValueError, match="Missing required station columns"):
            build_network_graph(stations_file, connections_file)

        # Cleanup
        os.remove(stations_file)
        os.remove(connections_file)
        os.rmdir(temp_dir)

    def test_missing_required_connection_columns(self):
        """Test error when connections CSV is missing required columns."""
        temp_dir = tempfile.mkdtemp()

        # Create minimal stations CSV
        stations_data = """station_id,station_name,line_code
NS1,Marina Bay,NS
"""
        stations_file = os.path.join(temp_dir, "stations.csv")
        with open(stations_file, 'w') as f:
            f.write(stations_data)

        # Create invalid connections CSV (missing travel_time_minutes)
        connections_data = """from_station_id,to_station_id
NS1,NS2
"""
        connections_file = os.path.join(temp_dir, "connections.csv")
        with open(connections_file, 'w') as f:
            f.write(connections_data)

        with pytest.raises(ValueError, match="Missing required connection columns"):
            build_network_graph(stations_file, connections_file)

        # Cleanup
        os.remove(stations_file)
        os.remove(connections_file)
        os.rmdir(temp_dir)

    def test_skip_invalid_travel_times(self):
        """Test that edges with invalid travel times are skipped."""
        temp_dir = tempfile.mkdtemp()

        stations_data = """station_id,station_name,line_code
NS1,Marina Bay,NS
NS2,Raffles Place,NS
"""
        stations_file = os.path.join(temp_dir, "stations.csv")
        with open(stations_file, 'w') as f:
            f.write(stations_data)

        # Include invalid travel times
        connections_data = """from_station_id,to_station_id,travel_time_minutes
NS1,NS2,
NS2,NS1,0
"""
        connections_file = os.path.join(temp_dir, "connections.csv")
        with open(connections_file, 'w') as f:
            f.write(connections_data)

        # Should build graph but skip invalid edges
        # With validation disabled (since graph would be invalid)
        G = build_network_graph(stations_file, connections_file, validate=False)

        assert G.number_of_nodes() == 2
        assert G.number_of_edges() == 0  # Both edges invalid

        # Cleanup
        os.remove(stations_file)
        os.remove(connections_file)
        os.rmdir(temp_dir)


class TestValidateGraph:
    """Test suite for graph validation."""

    def test_validate_empty_graph(self):
        """Test validation fails for empty graph."""
        G = nx.Graph()
        stations_df = pd.DataFrame({'station_id': []})
        connections_df = pd.DataFrame()

        with pytest.raises(ValueError, match="Graph has no nodes"):
            _validate_graph(G, stations_df, connections_df)

    def test_validate_graph_with_no_edges(self):
        """Test validation fails for graph with no edges."""
        G = nx.Graph()
        G.add_node('NS1')

        stations_df = pd.DataFrame({'station_id': ['NS1']})
        connections_df = pd.DataFrame()

        with pytest.raises(ValueError, match="Graph has no edges"):
            _validate_graph(G, stations_df, connections_df)

    def test_validate_edge_without_weight(self):
        """Test validation fails for edge without weight."""
        G = nx.Graph()
        G.add_edge('NS1', 'NS2')  # No weight attribute

        stations_df = pd.DataFrame({'station_id': ['NS1', 'NS2']})
        connections_df = pd.DataFrame()

        with pytest.raises(ValueError, match="missing weight"):
            _validate_graph(G, stations_df, connections_df)

    def test_validate_edge_with_negative_weight(self):
        """Test validation fails for edge with non-positive weight."""
        G = nx.Graph()
        G.add_edge('NS1', 'NS2', weight=-1.0)

        stations_df = pd.DataFrame({'station_id': ['NS1', 'NS2']})
        connections_df = pd.DataFrame()

        with pytest.raises(ValueError, match="non-positive weight"):
            _validate_graph(G, stations_df, connections_df)


class TestLoadDefaultGraph:
    """Test suite for load_default_graph function."""

    def test_load_default_graph(self):
        """Test loading the default Singapore MRT/LRT graph."""
        # This test will only pass if the data files exist
        project_root = Path(__file__).parent.parent.parent
        stations_csv = project_root / "data" / "raw" / "stations.csv"
        connections_csv = project_root / "data" / "raw" / "connections.csv"

        if not stations_csv.exists() or not connections_csv.exists():
            pytest.skip("Default data files not found")

        G = load_default_graph()

        # Basic sanity checks
        assert G.number_of_nodes() > 0
        assert G.number_of_edges() > 0

        # Check that it's a valid graph
        for u, v, data in G.edges(data=True):
            assert 'weight' in data
            assert data['weight'] > 0
