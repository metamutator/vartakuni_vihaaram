#!/usr/bin/env python3
"""
Validation script for connections.csv

Checks data quality and completeness for the Singapore MRT/LRT connections dataset.
"""

import csv
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def add_error(self, message: str):
        self.errors.append(f"❌ ERROR: {message}")

    def add_warning(self, message: str):
        self.warnings.append(f"⚠️  WARNING: {message}")

    def add_info(self, message: str):
        self.info.append(f"ℹ️  INFO: {message}")

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_summary(self):
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        if self.errors:
            print(f"\n🔴 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n🟡 WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.info:
            print(f"\n🔵 INFO ({len(self.info)}):")
            for info in self.info:
                print(f"  {info}")

        print("\n" + "=" * 70)
        if not self.has_errors():
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
        print("=" * 70 + "\n")


def validate_connections_csv(
    connections_csv: Path,
    stations_csv: Path
) -> ValidationResult:
    """
    Validate the connections.csv file.

    Returns:
        ValidationResult with errors, warnings, and info messages
    """
    result = ValidationResult()

    # Check file exists
    if not connections_csv.exists():
        result.add_error(f"File not found: {connections_csv}")
        return result

    if not stations_csv.exists():
        result.add_error(f"Stations file not found: {stations_csv}")
        return result

    # Read stations for validation
    try:
        with open(stations_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            valid_station_ids = {row['station_id'] for row in reader}
    except Exception as e:
        result.add_error(f"Failed to read stations CSV: {e}")
        return result

    # Read connections
    try:
        with open(connections_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            connections = list(reader)
    except Exception as e:
        result.add_error(f"Failed to read connections CSV: {e}")
        return result

    # Expected columns
    expected_columns = {
        'connection_id',
        'from_station_id',
        'to_station_id',
        'connection_type',
        'travel_time_minutes',
        'distance_meters',
        'line_code'
    }

    # Check columns
    if not connections:
        result.add_error("CSV is empty")
        return result

    actual_columns = set(connections[0].keys())
    if actual_columns != expected_columns:
        missing = expected_columns - actual_columns
        extra = actual_columns - expected_columns
        if missing:
            result.add_error(f"Missing columns: {missing}")
        if extra:
            result.add_warning(f"Extra columns: {extra}")

    # Track bidirectionality
    forward_connections = {}  # (from, to) -> connection
    backward_connections = {}  # (to, from) -> connection
    connection_ids = set()
    line_codes = set()

    # Validate each connection
    for idx, conn in enumerate(connections, start=2):
        row_id = f"Row {idx} ({conn.get('connection_id', 'UNKNOWN')})"

        # Check for missing values (line_code can be empty for walking connections)
        for col in expected_columns:
            value = conn.get(col, '').strip()
            # line_code can be empty for walking connections
            if not value and not (col == 'line_code' and conn.get('connection_type', '').startswith('walk')):
                result.add_error(f"{row_id}: Missing value for '{col}'")

        # Validate connection_id uniqueness
        conn_id = conn.get('connection_id', '')
        if conn_id:
            if conn_id in connection_ids:
                result.add_error(f"{row_id}: Duplicate connection_id '{conn_id}'")
            connection_ids.add(conn_id)

        # Validate station IDs exist
        from_station = conn.get('from_station_id', '')
        to_station = conn.get('to_station_id', '')

        if from_station and from_station not in valid_station_ids:
            result.add_error(
                f"{row_id}: from_station_id '{from_station}' not found in stations.csv"
            )

        if to_station and to_station not in valid_station_ids:
            result.add_error(
                f"{row_id}: to_station_id '{to_station}' not found in stations.csv"
            )

        # Check for self-loops
        if from_station == to_station:
            result.add_error(f"{row_id}: Self-loop detected ({from_station} → {to_station})")

        # Validate connection_type
        conn_type = conn.get('connection_type', '')
        valid_types = {'train', 'walk_transfer', 'walk_between_stations'}
        if conn_type and conn_type not in valid_types:
            result.add_warning(
                f"{row_id}: Unknown connection_type '{conn_type}'. "
                f"Expected one of: {valid_types}"
            )

        # Validate travel_time_minutes
        try:
            travel_time = float(conn.get('travel_time_minutes', '0'))
            if travel_time <= 0:
                result.add_error(f"{row_id}: Invalid travel_time_minutes: {travel_time}")
            elif travel_time > 10:
                result.add_warning(
                    f"{row_id}: Unusually long travel time: {travel_time} minutes "
                    f"({from_station} → {to_station})"
                )
        except ValueError as e:
            result.add_error(f"{row_id}: Invalid travel_time_minutes value - {e}")

        # Validate distance_meters (can be 0 for walk_transfer at same location)
        try:
            distance = int(conn.get('distance_meters', '0'))
            # Allow 0 distance for walk_transfer (same location platform transfers)
            if distance < 0:
                result.add_error(f"{row_id}: Invalid distance_meters: {distance}")
            elif distance == 0 and conn_type not in ['walk_transfer', 'walk_between_stations']:
                result.add_error(f"{row_id}: Invalid distance_meters: {distance}")
            elif distance > 5000:
                result.add_warning(
                    f"{row_id}: Unusually long distance: {distance}m "
                    f"({from_station} → {to_station})"
                )
        except ValueError as e:
            result.add_error(f"{row_id}: Invalid distance_meters value - {e}")

        # Track line codes
        line_code = conn.get('line_code', '')
        if line_code:
            line_codes.add(line_code)

        # Track bidirectional pairs
        pair = (from_station, to_station)
        reverse_pair = (to_station, from_station)

        if conn_type == 'train':  # Only check bidirectionality for train connections
            forward_connections[pair] = conn
            if reverse_pair in forward_connections:
                backward_connections[pair] = forward_connections[reverse_pair]

    # Check bidirectionality
    missing_reverse = []
    for pair in forward_connections:
        reverse_pair = (pair[1], pair[0])
        if reverse_pair not in forward_connections:
            missing_reverse.append(pair)

    if missing_reverse:
        result.add_error(
            f"Found {len(missing_reverse)} connections without reverse pairs. "
            f"All train connections should be bidirectional."
        )
        for pair in missing_reverse[:5]:  # Show first 5 examples
            result.add_error(f"  Missing reverse: {pair[0]} → {pair[1]}")

    # Count statistics
    total_connections = len(connections)
    unique_pairs = len(forward_connections)
    bidirectional_pairs = len(backward_connections)

    # Info messages
    result.add_info(f"Total connections: {total_connections}")
    result.add_info(f"Unique directional pairs: {unique_pairs}")
    result.add_info(f"Bidirectional pairs: {bidirectional_pairs}")
    result.add_info(f"Line codes found: {sorted(line_codes)}")

    # Check if connections cover all lines
    expected_lines = {'NS', 'EW', 'CC', 'NE', 'DT', 'TE', 'CE', 'CG',
                     'BP', 'SE', 'SW', 'PE', 'PW'}
    missing_lines = expected_lines - line_codes
    if missing_lines:
        result.add_warning(f"No connections found for lines: {sorted(missing_lines)}")

    # Calculate network statistics
    total_distance = sum(int(c.get('distance_meters', 0)) for c in connections) // 2
    avg_distance = total_distance / (unique_pairs if unique_pairs > 0 else 1)

    result.add_info(f"Total network distance: {total_distance/1000:.1f} km")
    result.add_info(f"Average inter-station distance: {avg_distance:.0f} m")

    return result


if __name__ == '__main__':
    # Define paths
    project_root = Path(__file__).parent.parent
    connections_csv = project_root / 'data' / 'raw' / 'connections.csv'
    stations_csv = project_root / 'data' / 'raw' / 'stations.csv'

    print(f"Validating: {connections_csv}")
    print(f"Against stations: {stations_csv}")

    # Run validation
    result = validate_connections_csv(connections_csv, stations_csv)

    # Print results
    result.print_summary()

    # Exit with appropriate code
    exit(1 if result.has_errors() else 0)
