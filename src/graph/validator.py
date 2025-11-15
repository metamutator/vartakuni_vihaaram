#!/usr/bin/env python3
"""
Data Validation Pipeline for Metro Network Data (US-202)

Validates metro network data files for errors and inconsistencies that could
cause failures in the TSP solver.
"""

import csv
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # e.g., 'connectivity', 'data_integrity', 'duplicates'
    message: str
    details: Optional[Dict] = None


@dataclass
class ValidationReport:
    """Container for validation results."""
    timestamp: str
    data_files: Dict[str, Path]
    issues: List[ValidationIssue] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)

    def add_error(self, category: str, message: str, details: Optional[Dict] = None):
        """Add an error to the report."""
        self.issues.append(ValidationIssue('error', category, message, details))

    def add_warning(self, category: str, message: str, details: Optional[Dict] = None):
        """Add a warning to the report."""
        self.issues.append(ValidationIssue('warning', category, message, details))

    def add_info(self, category: str, message: str, details: Optional[Dict] = None):
        """Add an info message to the report."""
        self.issues.append(ValidationIssue('info', category, message, details))

    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return any(issue.severity == 'error' for issue in self.issues)

    def get_summary(self) -> Dict[str, int]:
        """Get summary counts by severity."""
        summary = {'error': 0, 'warning': 0, 'info': 0}
        for issue in self.issues:
            summary[issue.severity] += 1
        return summary

    def print_report(self):
        """Print a formatted validation report."""
        print("\n" + "=" * 80)
        print("DATA VALIDATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")
        print(f"\nData Files:")
        for name, path in self.data_files.items():
            print(f"  {name}: {path}")

        print(f"\nStatistics:")
        for key, value in self.stats.items():
            print(f"  {key}: {value}")

        summary = self.get_summary()
        print(f"\nSummary:")
        print(f"  Errors:   {summary['error']}")
        print(f"  Warnings: {summary['warning']}")
        print(f"  Info:     {summary['info']}")

        if self.issues:
            print(f"\nIssues Found:")

            # Group by severity
            for severity in ['error', 'warning', 'info']:
                severity_issues = [i for i in self.issues if i.severity == severity]
                if severity_issues:
                    icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[severity]
                    print(f"\n{icon} {severity.upper()}S ({len(severity_issues)}):")
                    for issue in severity_issues:
                        print(f"  [{issue.category}] {issue.message}")
                        if issue.details:
                            for key, value in issue.details.items():
                                print(f"    - {key}: {value}")

        print("\n" + "=" * 80)
        if not self.has_errors():
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
        print("=" * 80 + "\n")


class MetroDataValidator:
    """
    Validates metro network data files for errors and inconsistencies.

    Performs comprehensive validation including:
    - Graph connectivity checks
    - Station ID reference validation
    - Travel time validation
    - Duplicate connection detection
    - Data integrity checks
    """

    def __init__(self):
        """Initialize validator."""
        self.report = None
        self.stations: Dict[str, Dict] = {}
        self.connections: List[Dict] = []
        self.lines: Dict[str, Dict] = {}

    def validate(
        self,
        stations_csv: Path,
        connections_csv: Path,
        lines_csv: Optional[Path] = None
    ) -> ValidationReport:
        """
        Run full validation pipeline on metro network data.

        Args:
            stations_csv: Path to stations.csv
            connections_csv: Path to connections.csv
            lines_csv: Optional path to lines.csv

        Returns:
            ValidationReport with all validation results
        """
        # Initialize report
        self.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={
                'stations': stations_csv,
                'connections': connections_csv,
                'lines': lines_csv if lines_csv else Path('N/A')
            }
        )

        # Run validation checks in order
        self._check_file_existence()
        if not self.report.has_errors():
            self._load_data(stations_csv, connections_csv, lines_csv)
            self._validate_data_integrity()
            self._validate_station_references()
            self._validate_travel_times()
            self._validate_distances()
            self._detect_duplicate_connections()
            self._validate_graph_connectivity()
            self._collect_statistics()

        return self.report

    def _check_file_existence(self):
        """Check that all required files exist."""
        for name, path in self.report.data_files.items():
            if name == 'lines' and str(path) == 'N/A':
                continue
            if not path.exists():
                self.report.add_error(
                    'file_missing',
                    f"Required file not found: {name}",
                    {'path': str(path)}
                )

    def _load_data(
        self,
        stations_csv: Path,
        connections_csv: Path,
        lines_csv: Optional[Path]
    ):
        """Load all data files."""
        try:
            # Load stations
            with open(stations_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.stations[row['station_id']] = dict(row)

            # Load connections
            with open(connections_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.connections = [dict(row) for row in reader]

            # Load lines if provided
            if lines_csv and lines_csv.exists():
                with open(lines_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.lines[row['line_code']] = dict(row)

        except Exception as e:
            self.report.add_error(
                'file_read_error',
                f"Error reading data files: {str(e)}"
            )

    def _validate_data_integrity(self):
        """Validate data integrity (required fields, formats)."""
        # Check stations have required fields
        required_station_fields = {
            'station_id', 'station_name', 'line_code',
            'latitude', 'longitude', 'operational_status'
        }

        if self.stations:
            first_station = next(iter(self.stations.values()))
            missing_fields = required_station_fields - set(first_station.keys())
            if missing_fields:
                self.report.add_error(
                    'data_integrity',
                    f"Stations missing required fields: {missing_fields}"
                )

        # Check connections have required fields
        required_connection_fields = {
            'connection_id', 'from_station_id', 'to_station_id',
            'connection_type', 'travel_time_minutes', 'distance_meters'
        }

        if self.connections:
            first_conn = self.connections[0]
            missing_fields = required_connection_fields - set(first_conn.keys())
            if missing_fields:
                self.report.add_error(
                    'data_integrity',
                    f"Connections missing required fields: {missing_fields}"
                )

    def _validate_station_references(self):
        """Verify all station IDs in connections exist in stations file."""
        station_ids = set(self.stations.keys())
        missing_stations = set()

        for conn in self.connections:
            from_id = conn.get('from_station_id')
            to_id = conn.get('to_station_id')

            if from_id and from_id not in station_ids:
                missing_stations.add(from_id)
            if to_id and to_id not in station_ids:
                missing_stations.add(to_id)

        if missing_stations:
            self.report.add_error(
                'missing_references',
                f"Found {len(missing_stations)} station IDs in connections that don't exist in stations file",
                {'missing_ids': sorted(list(missing_stations)[:10])}  # Show first 10
            )

    def _validate_travel_times(self):
        """Flag missing or negative travel times."""
        invalid_times = []

        for conn in self.connections:
            conn_id = conn.get('connection_id', 'unknown')
            try:
                travel_time = float(conn.get('travel_time_minutes', -1))
                if travel_time <= 0:
                    invalid_times.append({
                        'connection_id': conn_id,
                        'from': conn.get('from_station_id'),
                        'to': conn.get('to_station_id'),
                        'time': travel_time
                    })
            except ValueError:
                invalid_times.append({
                    'connection_id': conn_id,
                    'error': 'invalid_format',
                    'value': conn.get('travel_time_minutes')
                })

        if invalid_times:
            self.report.add_error(
                'invalid_travel_times',
                f"Found {len(invalid_times)} connections with invalid travel times (≤0 or non-numeric)",
                {'examples': invalid_times[:5]}  # Show first 5
            )

    def _validate_distances(self):
        """Validate distance values."""
        invalid_distances = []

        for conn in self.connections:
            conn_id = conn.get('connection_id', 'unknown')
            conn_type = conn.get('connection_type', '')

            try:
                distance = int(conn.get('distance_meters', -1))

                # Distance can be 0 for walk_transfer at same location
                if distance < 0:
                    invalid_distances.append({
                        'connection_id': conn_id,
                        'from': conn.get('from_station_id'),
                        'to': conn.get('to_station_id'),
                        'distance': distance
                    })

                # Warn if distance is unusually large
                if distance > 5000:
                    self.report.add_warning(
                        'unusual_distance',
                        f"Connection {conn_id} has unusually large distance: {distance}m",
                        {'from': conn.get('from_station_id'), 'to': conn.get('to_station_id')}
                    )

            except ValueError:
                invalid_distances.append({
                    'connection_id': conn_id,
                    'error': 'invalid_format',
                    'value': conn.get('distance_meters')
                })

        if invalid_distances:
            self.report.add_error(
                'invalid_distances',
                f"Found {len(invalid_distances)} connections with invalid distances",
                {'examples': invalid_distances[:5]}
            )

    def _detect_duplicate_connections(self):
        """Report duplicate connections."""
        seen_pairs = {}
        duplicates = []

        for conn in self.connections:
            from_id = conn.get('from_station_id')
            to_id = conn.get('to_station_id')
            pair = (from_id, to_id)

            if pair in seen_pairs:
                duplicates.append({
                    'connection_id': conn.get('connection_id'),
                    'duplicate_of': seen_pairs[pair],
                    'from': from_id,
                    'to': to_id
                })
            else:
                seen_pairs[pair] = conn.get('connection_id')

        if duplicates:
            self.report.add_warning(
                'duplicate_connections',
                f"Found {len(duplicates)} duplicate connections (same from-to pair)",
                {'examples': duplicates[:5]}
            )

    def _validate_graph_connectivity(self):
        """Check for disconnected components in graph."""
        # Build graph from connections
        graph = nx.Graph()

        # Add nodes
        for station_id in self.stations.keys():
            graph.add_node(station_id)

        # Add edges
        for conn in self.connections:
            from_id = conn.get('from_station_id')
            to_id = conn.get('to_station_id')
            if from_id and to_id and from_id in self.stations and to_id in self.stations:
                graph.add_edge(from_id, to_id)

        # Check connectivity
        if not nx.is_connected(graph):
            components = list(nx.connected_components(graph))
            component_info = []
            for i, component in enumerate(components, 1):
                component_list = sorted(list(component))
                component_info.append({
                    'component': i,
                    'size': len(component_list),
                    'stations': component_list[:5] + (['...'] if len(component_list) > 5 else [])
                })

            self.report.add_error(
                'disconnected_graph',
                f"Graph has {len(components)} disconnected components",
                {'components': component_info}
            )
        else:
            self.report.add_info(
                'connectivity',
                "Graph is fully connected",
                {'diameter': nx.diameter(graph)}
            )

    def _collect_statistics(self):
        """Collect overall statistics."""
        self.report.stats = {
            'num_stations': len(self.stations),
            'num_connections': len(self.connections),
            'num_lines': len(self.lines),
            'connection_types': self._count_connection_types(),
        }

    def _count_connection_types(self) -> Dict[str, int]:
        """Count connections by type."""
        counts = {}
        for conn in self.connections:
            conn_type = conn.get('connection_type', 'unknown')
            counts[conn_type] = counts.get(conn_type, 0) + 1
        return counts


def validate_metro_data(
    data_dir: Path,
    stations_file: str = 'stations.csv',
    connections_file: str = 'connections.csv',
    lines_file: str = 'lines.csv'
) -> ValidationReport:
    """
    Convenience function to validate metro network data.

    Args:
        data_dir: Directory containing data files
        stations_file: Name of stations file
        connections_file: Name of connections file
        lines_file: Name of lines file

    Returns:
        ValidationReport
    """
    validator = MetroDataValidator()

    stations_path = data_dir / stations_file
    connections_path = data_dir / connections_file
    lines_path = data_dir / lines_file

    return validator.validate(
        stations_path,
        connections_path,
        lines_path if lines_path.exists() else None
    )


if __name__ == '__main__':
    """Run validation on Singapore MRT/LRT data."""
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data' / 'raw'

    print("Running Metro Data Validation Pipeline (US-202)")
    print("=" * 80)
    print(f"Data directory: {data_dir}\n")

    # Run validation
    report = validate_metro_data(data_dir)

    # Print report
    report.print_report()

    # Exit with error code if validation failed
    exit(1 if report.has_errors() else 0)
