#!/usr/bin/env python3
"""
Graph Builder Module for Singapore MRT/LRT Network

This module constructs a NetworkX graph from CSV data files containing
station information, connections, and line metadata.
"""

import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx


class MetroGraphBuilder:
    """
    Builds and manages a NetworkX graph representation of a metro network.

    The graph is undirected and weighted by travel time. Multi-line stations
    are represented as separate nodes (e.g., NS24, NE6, CC1 for Dhoby Ghaut)
    connected by walking edges.
    """

    def __init__(self):
        """Initialize an empty graph builder."""
        self.graph: nx.Graph = nx.Graph()
        self.stations: Dict[str, Dict] = {}
        self.lines: Dict[str, Dict] = {}
        self.connections: List[Dict] = []

    def load_stations(self, stations_csv: Path) -> None:
        """
        Load station data from CSV file.

        Args:
            stations_csv: Path to stations.csv file

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If CSV is malformed or missing required columns
        """
        if not stations_csv.exists():
            raise FileNotFoundError(f"Stations file not found: {stations_csv}")

        required_columns = {'station_id', 'station_name', 'line_code',
                          'latitude', 'longitude', 'operational_status'}

        with open(stations_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate columns
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(f"Missing required columns: {missing}")

            # Read stations
            for row in reader:
                station_id = row['station_id']
                self.stations[station_id] = {
                    'name': row['station_name'],
                    'line_code': row['line_code'],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'operational_status': row['operational_status']
                }

                # Add node to graph
                self.graph.add_node(
                    station_id,
                    name=row['station_name'],
                    line_code=row['line_code'],
                    pos=(float(row['longitude']), float(row['latitude'])),
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    operational_status=row['operational_status']
                )

    def load_lines(self, lines_csv: Path) -> None:
        """
        Load line metadata from CSV file.

        Args:
            lines_csv: Path to lines.csv file

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If CSV is malformed or missing required columns
        """
        if not lines_csv.exists():
            raise FileNotFoundError(f"Lines file not found: {lines_csv}")

        required_columns = {'line_code', 'line_name', 'color_hex', 'line_type'}

        with open(lines_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate columns
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(f"Missing required columns: {missing}")

            # Read lines
            for row in reader:
                line_code = row['line_code']
                self.lines[line_code] = {
                    'name': row['line_name'],
                    'color': row['color_hex'],
                    'type': row['line_type']
                }

    def load_connections(self, connections_csv: Path) -> None:
        """
        Load connection data and build graph edges.

        Args:
            connections_csv: Path to connections.csv file

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If CSV is malformed or missing required columns
        """
        if not connections_csv.exists():
            raise FileNotFoundError(f"Connections file not found: {connections_csv}")

        required_columns = {'connection_id', 'from_station_id', 'to_station_id',
                          'connection_type', 'travel_time_minutes', 'distance_meters'}

        with open(connections_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate columns
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(f"Missing required columns: {missing}")

            # Read connections
            for row in reader:
                from_station = row['from_station_id']
                to_station = row['to_station_id']

                # Validate stations exist
                if from_station not in self.stations:
                    raise ValueError(f"Unknown station: {from_station}")
                if to_station not in self.stations:
                    raise ValueError(f"Unknown station: {to_station}")

                # Store connection data
                connection = {
                    'id': row['connection_id'],
                    'from': from_station,
                    'to': to_station,
                    'type': row['connection_type'],
                    'time': float(row['travel_time_minutes']),
                    'distance': int(row['distance_meters']),
                    'line_code': row.get('line_code', '')
                }
                self.connections.append(connection)

                # Add edge to graph (undirected, weighted by travel time)
                self.graph.add_edge(
                    from_station,
                    to_station,
                    weight=float(row['travel_time_minutes']),
                    connection_type=row['connection_type'],
                    distance_meters=int(row['distance_meters']),
                    line_code=row.get('line_code', ''),
                    connection_id=row['connection_id']
                )

    def build_graph(
        self,
        stations_csv: Path,
        connections_csv: Path,
        lines_csv: Optional[Path] = None
    ) -> nx.Graph:
        """
        Build the complete metro network graph.

        Args:
            stations_csv: Path to stations.csv file
            connections_csv: Path to connections.csv file
            lines_csv: Optional path to lines.csv file

        Returns:
            NetworkX Graph object representing the metro network

        Raises:
            FileNotFoundError: If required files don't exist
            ValueError: If data is malformed
        """
        # Load data in order
        self.load_stations(stations_csv)
        if lines_csv:
            self.load_lines(lines_csv)
        self.load_connections(connections_csv)

        return self.graph

    def validate_connectivity(self) -> Tuple[bool, List[str]]:
        """
        Validate that all stations in the graph are reachable from each other.

        Returns:
            Tuple of (is_connected, list_of_disconnected_components)
            - is_connected: True if graph is fully connected
            - list_of_disconnected_components: Empty if connected, otherwise
              contains lists of nodes in each disconnected component

        Raises:
            ValueError: If graph is empty
        """
        if self.graph.number_of_nodes() == 0:
            raise ValueError("Graph is empty. Load data first.")

        # Check if graph is connected
        is_connected = nx.is_connected(self.graph)

        if is_connected:
            return True, []
        else:
            # Find all disconnected components
            components = list(nx.connected_components(self.graph))
            disconnected_info = []

            for i, component in enumerate(components, 1):
                component_list = sorted(list(component))
                disconnected_info.append(
                    f"Component {i} ({len(component_list)} stations): "
                    f"{', '.join(component_list[:5])}"
                    f"{', ...' if len(component_list) > 5 else ''}"
                )

            return False, disconnected_info

    def get_graph(self) -> nx.Graph:
        """
        Get the constructed graph.

        Returns:
            NetworkX Graph object

        Raises:
            ValueError: If graph hasn't been built yet
        """
        if self.graph.number_of_nodes() == 0:
            raise ValueError("Graph is empty. Build the graph first using build_graph().")

        return self.graph

    def get_station_info(self, station_id: str) -> Dict:
        """
        Get detailed information about a specific station.

        Args:
            station_id: Station identifier (e.g., 'NS24', 'EW13')

        Returns:
            Dictionary with station details

        Raises:
            ValueError: If station doesn't exist
        """
        if station_id not in self.stations:
            raise ValueError(f"Station not found: {station_id}")

        return self.stations[station_id]

    def get_line_info(self, line_code: str) -> Dict:
        """
        Get detailed information about a specific line.

        Args:
            line_code: Line code (e.g., 'NS', 'EW', 'TE')

        Returns:
            Dictionary with line details (name, color, type)

        Raises:
            ValueError: If line doesn't exist
        """
        if line_code not in self.lines:
            raise ValueError(f"Line not found: {line_code}")

        return self.lines[line_code]

    def get_neighbors(self, station_id: str) -> List[Tuple[str, float]]:
        """
        Get all neighboring stations and their travel times.

        Args:
            station_id: Station identifier

        Returns:
            List of tuples (neighbor_id, travel_time_minutes)

        Raises:
            ValueError: If station doesn't exist
        """
        if station_id not in self.graph:
            raise ValueError(f"Station not found in graph: {station_id}")

        neighbors = []
        for neighbor in self.graph.neighbors(station_id):
            edge_data = self.graph[station_id][neighbor]
            travel_time = edge_data['weight']
            neighbors.append((neighbor, travel_time))

        return sorted(neighbors, key=lambda x: x[1])

    def get_shortest_path(
        self,
        start: str,
        end: str,
        weight: str = 'weight'
    ) -> Tuple[List[str], float]:
        """
        Find the shortest path between two stations.

        Args:
            start: Starting station ID
            end: Ending station ID
            weight: Edge attribute to use as weight (default: 'weight' = travel time)

        Returns:
            Tuple of (path_as_list_of_stations, total_weight)

        Raises:
            ValueError: If stations don't exist
            nx.NetworkXNoPath: If no path exists between stations
        """
        if start not in self.graph:
            raise ValueError(f"Start station not found: {start}")
        if end not in self.graph:
            raise ValueError(f"End station not found: {end}")

        path = nx.shortest_path(self.graph, start, end, weight=weight)
        length = nx.shortest_path_length(self.graph, start, end, weight=weight)

        return path, length

    def get_graph_stats(self) -> Dict:
        """
        Get statistical information about the graph.

        Returns:
            Dictionary with graph statistics
        """
        if self.graph.number_of_nodes() == 0:
            return {
                'num_stations': 0,
                'num_connections': 0,
                'is_connected': False
            }

        is_connected, _ = self.validate_connectivity()

        # Count connection types
        connection_types = {}
        for _, _, data in self.graph.edges(data=True):
            conn_type = data.get('connection_type', 'unknown')
            connection_types[conn_type] = connection_types.get(conn_type, 0) + 1

        # Calculate average degree
        degrees = [self.graph.degree(node) for node in self.graph.nodes()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        return {
            'num_stations': self.graph.number_of_nodes(),
            'num_connections': self.graph.number_of_edges(),
            'is_connected': is_connected,
            'num_lines': len(self.lines),
            'connection_types': connection_types,
            'average_degree': round(avg_degree, 2),
            'diameter': nx.diameter(self.graph) if is_connected else None,
            'average_clustering': round(nx.average_clustering(self.graph), 3)
        }


def build_singapore_metro_graph(data_dir: Path) -> nx.Graph:
    """
    Convenience function to build Singapore MRT/LRT graph from data directory.

    Args:
        data_dir: Path to data/raw directory containing CSV files

    Returns:
        NetworkX Graph object

    Example:
        >>> from pathlib import Path
        >>> graph = build_singapore_metro_graph(Path('data/raw'))
        >>> print(f"Loaded {graph.number_of_nodes()} stations")
    """
    builder = MetroGraphBuilder()

    stations_csv = data_dir / 'stations.csv'
    connections_csv = data_dir / 'connections.csv'
    lines_csv = data_dir / 'lines.csv'

    graph = builder.build_graph(stations_csv, connections_csv, lines_csv)

    # Validate connectivity
    is_connected, disconnected = builder.validate_connectivity()
    if not is_connected:
        print("⚠️  WARNING: Graph is not fully connected!")
        for component_info in disconnected:
            print(f"  {component_info}")
    else:
        print("✅ Graph is fully connected")

    # Print stats
    stats = builder.get_graph_stats()
    print(f"\n📊 Graph Statistics:")
    print(f"   Stations: {stats['num_stations']}")
    print(f"   Connections: {stats['num_connections']}")
    print(f"   Lines: {stats['num_lines']}")
    print(f"   Connection types: {stats['connection_types']}")
    print(f"   Average degree: {stats['average_degree']}")
    if stats['diameter']:
        print(f"   Diameter: {stats['diameter']}")
    print(f"   Average clustering: {stats['average_clustering']}")

    return graph


if __name__ == '__main__':
    """Example usage and testing."""
    from pathlib import Path

    # Build graph
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data' / 'raw'

    print("Building Singapore MRT/LRT network graph...")
    print(f"Data directory: {data_dir}\n")

    graph = build_singapore_metro_graph(data_dir)

    print(f"\n✅ Graph built successfully!")
    print(f"   Graph type: {'Connected' if nx.is_connected(graph) else 'Disconnected'}")
    print(f"   Ready for TSP algorithms")


# Alternative pandas-based implementation for simpler use cases
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
