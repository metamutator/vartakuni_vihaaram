"""Graph construction module for Singapore MRT/LRT network."""

import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Optional


def build_network_graph(
    stations_csv: str,
    connections_csv: str,
    validate: bool = True
) -> nx.Graph:
    """
    Build a NetworkX graph from station and connection CSV files.

    Args:
        stations_csv: Path to stations CSV file
        connections_csv: Path to connections CSV file
        validate: Whether to validate the graph after construction

    Returns:
        NetworkX Graph with stations as nodes and connections as edges

    Raises:
        FileNotFoundError: If CSV files don't exist
        ValueError: If data is invalid or validation fails
    """
    # Verify files exist
    stations_path = Path(stations_csv)
    connections_path = Path(connections_csv)

    if not stations_path.exists():
        raise FileNotFoundError(f"Stations file not found: {stations_csv}")
    if not connections_path.exists():
        raise FileNotFoundError(f"Connections file not found: {connections_csv}")

    # Load data
    stations_df = pd.read_csv(stations_csv)
    connections_df = pd.read_csv(connections_csv)

    # Validate required columns
    required_station_cols = {'station_id', 'station_name', 'line_code'}
    required_connection_cols = {'from_station_id', 'to_station_id', 'travel_time_minutes'}

    if not required_station_cols.issubset(stations_df.columns):
        missing = required_station_cols - set(stations_df.columns)
        raise ValueError(f"Missing required station columns: {missing}")

    if not required_connection_cols.issubset(connections_df.columns):
        missing = required_connection_cols - set(connections_df.columns)
        raise ValueError(f"Missing required connection columns: {missing}")

    # Create graph
    G = nx.Graph()

    # Add nodes with attributes
    for _, station in stations_df.iterrows():
        node_attrs = {
            'name': station['station_name'],
            'line_code': station['line_code']
        }

        # Add optional attributes if they exist
        if 'latitude' in station:
            node_attrs['latitude'] = station['latitude']
        if 'longitude' in station:
            node_attrs['longitude'] = station['longitude']
        if 'operational_status' in station:
            node_attrs['operational_status'] = station['operational_status']

        G.add_node(station['station_id'], **node_attrs)

    # Add edges with weights
    for _, connection in connections_df.iterrows():
        from_station = connection['from_station_id']
        to_station = connection['to_station_id']
        travel_time = connection['travel_time_minutes']

        # Skip if travel time is invalid
        if pd.isna(travel_time) or travel_time <= 0:
            continue

        edge_attrs = {'weight': travel_time}

        # Add optional attributes
        if 'connection_type' in connection:
            edge_attrs['connection_type'] = connection['connection_type']
        if 'distance_meters' in connection:
            edge_attrs['distance_meters'] = connection['distance_meters']
        if 'line_code' in connection:
            edge_attrs['line_code'] = connection['line_code']

        G.add_edge(from_station, to_station, **edge_attrs)

    # Validate graph if requested
    if validate:
        _validate_graph(G, stations_df, connections_df)

    return G


def _validate_graph(G: nx.Graph, stations_df: pd.DataFrame, connections_df: pd.DataFrame) -> None:
    """
    Validate the constructed graph.

    Args:
        G: NetworkX graph to validate
        stations_df: Original stations DataFrame
        connections_df: Original connections DataFrame

    Raises:
        ValueError: If validation fails
    """
    # Check that graph is not empty
    if G.number_of_nodes() == 0:
        raise ValueError("Graph has no nodes")

    if G.number_of_edges() == 0:
        raise ValueError("Graph has no edges")

    # Check that all nodes from stations are in graph
    expected_nodes = set(stations_df['station_id'])
    actual_nodes = set(G.nodes())

    if expected_nodes != actual_nodes:
        missing = expected_nodes - actual_nodes
        extra = actual_nodes - expected_nodes
        msg = []
        if missing:
            msg.append(f"Missing nodes: {missing}")
        if extra:
            msg.append(f"Extra nodes: {extra}")
        raise ValueError("; ".join(msg))

    # Check that all edges have positive weights
    for u, v, data in G.edges(data=True):
        if 'weight' not in data:
            raise ValueError(f"Edge ({u}, {v}) missing weight")
        if data['weight'] <= 0:
            raise ValueError(f"Edge ({u}, {v}) has non-positive weight: {data['weight']}")


def load_default_graph() -> nx.Graph:
    """
    Load the default Singapore MRT/LRT network graph.

    Returns:
        NetworkX Graph of the Singapore metro network

    Raises:
        FileNotFoundError: If default data files don't exist
    """
    # Get project root (assuming this file is in src/graph/)
    project_root = Path(__file__).parent.parent.parent
    stations_csv = project_root / "data" / "raw" / "stations.csv"
    connections_csv = project_root / "data" / "raw" / "connections.csv"

    return build_network_graph(str(stations_csv), str(connections_csv))
