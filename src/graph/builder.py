"""Graph construction module for Singapore MRT/LRT network."""

import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Optional


def build_network_graph(
    stations_csv: str,
    connections_csv: str,
    validate: bool = True,
    add_interchanges: bool = True,
    interchange_time: float = 5.0
) -> nx.Graph:
    """
    Build a NetworkX graph from station and connection CSV files.

    Args:
        stations_csv: Path to stations CSV file
        connections_csv: Path to connections CSV file
        validate: Whether to validate the graph after construction
        add_interchanges: Whether to automatically add interchange connections
        interchange_time: Travel time (minutes) for interchange transfers

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

    # Add interchange connections if requested
    if add_interchanges:
        _add_interchange_connections(G, stations_df, interchange_time)

    # Validate graph if requested
    if validate:
        _validate_graph(G, stations_df, connections_df)

    return G


def _add_interchange_connections(
    G: nx.Graph,
    stations_df: pd.DataFrame,
    interchange_time: float
) -> None:
    """
    Add interchange connections between stations with the same name.

    Stations with the same name but different station_ids are interchange
    stations where passengers can transfer between different lines.

    Args:
        G: NetworkX graph to add interchange connections to (modified in place)
        stations_df: DataFrame with station information
        interchange_time: Travel time (minutes) for interchange transfers
    """
    # Group stations by name
    station_groups = stations_df.groupby('station_name')['station_id'].apply(list)

    # Find interchange stations (same name, multiple station_ids)
    interchange_stations = station_groups[station_groups.apply(len) > 1]

    interchange_count = 0

    # Add bidirectional edges between all stations with the same name
    for station_name, station_ids in interchange_stations.items():
        # Connect all pairs of stations with the same name
        for i, station_id_1 in enumerate(station_ids):
            for station_id_2 in station_ids[i + 1:]:
                # Only add if not already connected
                if not G.has_edge(station_id_1, station_id_2):
                    G.add_edge(
                        station_id_1,
                        station_id_2,
                        weight=interchange_time,
                        connection_type='transfer',
                        line_code='INTERCHANGE'
                    )
                    interchange_count += 1

    # Print summary (useful for debugging)
    if interchange_count > 0:
        print(f"Added {interchange_count} interchange connections between {len(interchange_stations)} interchange stations")


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


def to_complete_graph(G: nx.Graph) -> nx.Graph:
    """
    Convert a sparse graph to a complete graph for TSP.

    In a complete graph, every pair of nodes is connected by an edge.
    The edge weight is the shortest path distance (sum of weights) between nodes.

    This is necessary for TSP algorithms to work on metro networks, where the
    "distance" between non-adjacent stations is the travel time along the
    shortest path.

    Args:
        G: Input graph (must be connected)

    Returns:
        Complete graph where edge (u,v) has weight = shortest path length from u to v

    Raises:
        ValueError: If graph is not connected
    """
    if not nx.is_connected(G):
        raise ValueError("Graph must be connected to convert to complete graph")

    # Create new complete graph with same nodes
    complete_G = nx.Graph()

    # Copy node attributes
    for node, attrs in G.nodes(data=True):
        complete_G.add_node(node, **attrs)

    # Compute all-pairs shortest paths
    nodes = list(G.nodes())
    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))

    # Add edges for all pairs of nodes
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            # Get shortest path length
            distance = shortest_paths[u][v]

            # Add edge with shortest path distance as weight
            complete_G.add_edge(u, v, weight=distance, connection_type='shortest_path')

    return complete_G


def load_default_graph(connected_only: bool = False, complete: bool = False) -> nx.Graph:
    """
    Load the default Singapore MRT/LRT network graph.

    Args:
        connected_only: If True, return only the largest connected component.
                       This is useful for TSP as it requires a connected graph.
        complete: If True, convert to complete graph where every pair of nodes
                 is connected by the shortest path distance. Required for TSP
                 algorithms to work correctly on sparse graphs. Implies connected_only=True.

    Returns:
        NetworkX Graph of the Singapore metro network

    Raises:
        FileNotFoundError: If default data files don't exist
    """
    # Get project root (assuming this file is in src/graph/)
    project_root = Path(__file__).parent.parent.parent
    stations_csv = project_root / "data" / "raw" / "stations.csv"
    connections_csv = project_root / "data" / "raw" / "connections.csv"

    G = build_network_graph(str(stations_csv), str(connections_csv))

    # Complete graph implies connected_only
    if complete:
        connected_only = True

    # Extract largest connected component if requested
    if connected_only and not nx.is_connected(G):
        components = list(nx.connected_components(G))
        largest_component = max(components, key=len)
        G = G.subgraph(largest_component).copy()
        print(f"Extracted largest connected component with {G.number_of_nodes()} stations")

    # Convert to complete graph if requested
    if complete:
        print(f"Converting to complete graph (all-pairs shortest paths)...")
        G = to_complete_graph(G)
        print(f"Complete graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    return G
