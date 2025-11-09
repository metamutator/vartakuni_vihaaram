#!/usr/bin/env python3
"""
Validation script for stations.csv

Checks data quality and completeness for the Singapore MRT/LRT stations dataset.
"""

import csv
from pathlib import Path
from typing import List, Dict, Tuple
import re


# Singapore geographic bounds (approximate)
SINGAPORE_LAT_MIN = 1.15
SINGAPORE_LAT_MAX = 1.48
SINGAPORE_LON_MIN = 103.6
SINGAPORE_LON_MAX = 104.1

# Known MRT/LRT line codes
KNOWN_LINE_CODES = {
    'NS', 'EW', 'CC', 'NE', 'DT', 'TE', 'CE', 'CR', 'CG',  # MRT lines (CG = Changi Airport)
    'BP', 'SE', 'SW', 'PE', 'PW', 'STC', 'PTC'  # LRT lines
}

# Minimum expected station count (from acceptance criteria)
MIN_STATION_COUNT = 189


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


def validate_stations_csv(csv_path: Path) -> ValidationResult:
    """
    Validate the stations.csv file.

    Returns:
        ValidationResult with errors, warnings, and info messages
    """
    result = ValidationResult()

    # Check file exists
    if not csv_path.exists():
        result.add_error(f"File not found: {csv_path}")
        return result

    # Read CSV
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            stations = list(reader)
    except Exception as e:
        result.add_error(f"Failed to read CSV: {e}")
        return result

    # Expected columns
    expected_columns = {
        'station_id',
        'station_name',
        'line_code',
        'latitude',
        'longitude',
        'operational_status'
    }

    # Check columns
    if not stations:
        result.add_error("CSV is empty")
        return result

    actual_columns = set(stations[0].keys())
    if actual_columns != expected_columns:
        missing = expected_columns - actual_columns
        extra = actual_columns - expected_columns
        if missing:
            result.add_error(f"Missing columns: {missing}")
        if extra:
            result.add_warning(f"Extra columns: {extra}")

    # Validate each station
    station_ids = set()
    station_names = set()
    line_codes = set()
    multi_line_stations = {}  # name -> list of line codes

    for idx, station in enumerate(stations, start=2):  # start=2 (header is row 1)
        row_id = f"Row {idx} ({station.get('station_id', 'UNKNOWN')})"

        # Check for missing values
        for col in expected_columns:
            if not station.get(col, '').strip():
                result.add_error(f"{row_id}: Missing value for '{col}'")

        # Validate station_id format
        station_id = station.get('station_id', '')
        if station_id:
            if not re.match(r'^[A-Z]{1,3}\d+[A-Z]?$', station_id):
                result.add_warning(
                    f"{row_id}: Station ID '{station_id}' has unusual format"
                )
            station_ids.add(station_id)

        # Validate station_name
        station_name = station.get('station_name', '')
        if station_name:
            station_names.add(station_name)

        # Validate line_code
        line_code = station.get('line_code', '')
        if line_code:
            if line_code not in KNOWN_LINE_CODES:
                result.add_warning(
                    f"{row_id}: Unknown line code '{line_code}'"
                )
            line_codes.add(line_code)

            # Track multi-line stations
            if station_name:
                if station_name not in multi_line_stations:
                    multi_line_stations[station_name] = []
                multi_line_stations[station_name].append(line_code)

        # Validate coordinates
        try:
            lat = float(station.get('latitude', '0'))
            lon = float(station.get('longitude', '0'))

            if not (SINGAPORE_LAT_MIN <= lat <= SINGAPORE_LAT_MAX):
                result.add_error(
                    f"{row_id}: Latitude {lat} is outside Singapore bounds"
                )

            if not (SINGAPORE_LON_MIN <= lon <= SINGAPORE_LON_MAX):
                result.add_error(
                    f"{row_id}: Longitude {lon} is outside Singapore bounds"
                )
        except ValueError as e:
            result.add_error(
                f"{row_id}: Invalid coordinate value - {e}"
            )

        # Validate operational_status
        status = station.get('operational_status', '')
        valid_statuses = {'active', 'under_construction', 'planned'}
        if status and status not in valid_statuses:
            result.add_warning(
                f"{row_id}: Unknown operational status '{status}'. "
                f"Expected one of: {valid_statuses}"
            )

    # Check for duplicate station IDs
    if len(station_ids) < len(stations):
        result.add_error(
            f"Duplicate station IDs found. "
            f"{len(stations)} rows but only {len(station_ids)} unique IDs"
        )

    # Count statistics
    interchange_stations = {
        name: codes for name, codes in multi_line_stations.items()
        if len(codes) > 1
    }

    # Check minimum station count
    if len(stations) < MIN_STATION_COUNT:
        result.add_error(
            f"Insufficient station entries: {len(stations)} < {MIN_STATION_COUNT}"
        )
    else:
        result.add_info(
            f"Station count requirement met: {len(stations)} >= {MIN_STATION_COUNT}"
        )

    # Info messages
    result.add_info(f"Total station entries: {len(stations)}")
    result.add_info(f"Unique station IDs: {len(station_ids)}")
    result.add_info(f"Unique station names: {len(station_names)}")
    result.add_info(f"Line codes found: {sorted(line_codes)}")
    result.add_info(
        f"Interchange stations: {len(interchange_stations)}"
    )

    if interchange_stations:
        result.add_info("Interchange stations:")
        for name, codes in sorted(interchange_stations.items()):
            result.add_info(f"  - {name}: {', '.join(sorted(codes))}")

    return result


if __name__ == '__main__':
    # Define path
    project_root = Path(__file__).parent.parent
    csv_path = project_root / 'data' / 'raw' / 'stations.csv'

    print(f"Validating: {csv_path}")

    # Run validation
    result = validate_stations_csv(csv_path)

    # Print results
    result.print_summary()

    # Exit with appropriate code
    exit(1 if result.has_errors() else 0)
