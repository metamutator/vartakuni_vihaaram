#!/usr/bin/env python3
"""
Graph Builder Module for Singapore MRT/LRT Network

This module constructs a NetworkX graph from CSV data files containing
station information, connections, and line metadata.
"""

import csv
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
