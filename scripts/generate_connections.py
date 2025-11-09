#!/usr/bin/env python3
"""
Generate inter-station connections and travel times for Singapore MRT/LRT network.

This script builds station-to-station connections based on sequential station codes
and estimates travel times using geographic distance and average train speeds.

Methodology:
- Connections inferred from sequential station codes (e.g., NS1→NS2, EW1→EW2)
- Travel times estimated using Haversine distance and average speeds:
  * MRT: ~50 km/h (average including acceleration/deceleration)
  * LRT: ~35 km/h (average including acceleration/deceleration)
  * Dwell time: ~30 seconds per station added
- Bidirectional connections created (undirected graph)

Note: These are ESTIMATED travel times. Official schedule data not publicly available.
Recommend validation against actual journey times where possible.
"""

import csv
import math
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Average speeds (km/h) including acceleration/deceleration
AVERAGE_SPEEDS = {
    'MRT': 50.0,  # MRT lines: NS, EW, CC, NE, DT, TE, CE, CG
    'LRT': 35.0,  # LRT lines: BP, SE, SW, PE, PW, STC, PTC
}

# Dwell time at each station (minutes)
DWELL_TIME = 0.5  # 30 seconds

# Line type mapping
MRT_LINES = {'NS', 'EW', 'CC', 'NE', 'DT', 'TE', 'CE', 'CR', 'CG'}
LRT_LINES = {'BP', 'SE', 'SW', 'PE', 'PW', 'STC', 'PTC'}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on earth (in kilometers).

    Args:
        lat1, lon1: Latitude and longitude of point 1 (in decimal degrees)
        lat2, lon2: Latitude and longitude of point 2 (in decimal degrees)

    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers
    r = 6371

    return c * r


def parse_station_code(station_id: str) -> Tuple[str, int]:
    """
    Parse station code into line code and station number.

    Examples:
        'NS10' -> ('NS', 10)
        'EW12' -> ('EW', 12)
        'BP9' -> ('BP', 9)
        'CG' -> ('CG', 0)  # Special case: terminal

    Returns:
        (line_code, station_number) or (line_code, 0) if no number found
    """
    line_code = ''
    number_str = ''

    for char in station_id:
        if char.isalpha():
            line_code += char
        elif char.isdigit():
            number_str += char

    station_num = int(number_str) if number_str else 0
    return (line_code, station_num)


def get_line_type(line_code: str) -> str:
    """Determine if line is MRT or LRT."""
    if line_code in MRT_LINES:
        return 'MRT'
    elif line_code in LRT_LINES:
        return 'LRT'
    else:
        # Default to MRT for unknown lines
        return 'MRT'


def estimate_travel_time(distance_km: float, line_type: str) -> float:
    """
    Estimate travel time based on distance and line type.

    Args:
        distance_km: Distance between stations in kilometers
        line_type: 'MRT' or 'LRT'

    Returns:
        Estimated travel time in minutes
    """
    avg_speed = AVERAGE_SPEEDS[line_type]

    # Time = Distance / Speed (in hours), convert to minutes
    travel_time = (distance_km / avg_speed) * 60

    # Add dwell time
    total_time = travel_time + DWELL_TIME

    return round(total_time, 2)


def build_connections(stations_csv: Path) -> List[Dict]:
    """
    Build station connections from stations CSV.

    Strategy:
    1. Group stations by line code
    2. Sort by station number
    3. Connect sequential stations
    4. Calculate distance and estimate travel time
    5. Create bidirectional connections
    """
    # Read stations
    with open(stations_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        stations = list(reader)

    # Build station lookup
    station_lookup = {
        s['station_id']: {
            'name': s['station_name'],
            'lat': float(s['latitude']),
            'lon': float(s['longitude']),
            'line_code': s['line_code']
        }
        for s in stations
    }

    # Group stations by line
    lines = defaultdict(list)
    for station_id, info in station_lookup.items():
        line_code, station_num = parse_station_code(station_id)
        if station_num > 0:  # Skip terminals without numbers
            lines[line_code].append((station_num, station_id, info))

    # Sort each line by station number
    for line_code in lines:
        lines[line_code].sort(key=lambda x: x[0])

    connections = []
    connection_id = 1

    # Create connections for each line
    for line_code, line_stations in sorted(lines.items()):
        line_type = get_line_type(line_code)

        print(f"Processing {line_code} ({line_type}): {len(line_stations)} stations")

        # Connect sequential stations
        for i in range(len(line_stations) - 1):
            station_num1, station_id1, info1 = line_stations[i]
            station_num2, station_id2, info2 = line_stations[i + 1]

            # Only connect if sequential (difference of 1)
            if station_num2 - station_num1 == 1:
                # Calculate distance
                distance_km = haversine_distance(
                    info1['lat'], info1['lon'],
                    info2['lat'], info2['lon']
                )

                # Estimate travel time
                travel_time = estimate_travel_time(distance_km, line_type)

                # Create forward connection
                connections.append({
                    'connection_id': f"{connection_id:04d}",
                    'from_station_id': station_id1,
                    'to_station_id': station_id2,
                    'connection_type': 'train',
                    'travel_time_minutes': travel_time,
                    'distance_meters': int(distance_km * 1000),
                    'line_code': line_code
                })
                connection_id += 1

                # Create backward connection (bidirectional)
                connections.append({
                    'connection_id': f"{connection_id:04d}",
                    'from_station_id': station_id2,
                    'to_station_id': station_id1,
                    'connection_type': 'train',
                    'travel_time_minutes': travel_time,
                    'distance_meters': int(distance_km * 1000),
                    'line_code': line_code
                })
                connection_id += 1

    print(f"\nGenerated {len(connections)} connections ({len(connections)//2} unique pairs)")

    return connections


def write_connections_csv(connections: List[Dict], output_path: Path):
    """Write connections to CSV file."""
    fieldnames = [
        'connection_id',
        'from_station_id',
        'to_station_id',
        'connection_type',
        'travel_time_minutes',
        'distance_meters',
        'line_code'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(connections)

    print(f"✓ Written to {output_path}")

    # Print summary statistics
    unique_pairs = len(connections) // 2
    total_distance_km = sum(c['distance_meters'] for c in connections) / 2000  # Divide by 2 for bidirectional
    avg_time = sum(c['travel_time_minutes'] for c in connections) / len(connections)

    print(f"\nSummary:")
    print(f"  - Total connections (bidirectional): {len(connections)}")
    print(f"  - Unique station pairs: {unique_pairs}")
    print(f"  - Total network distance: {total_distance_km:.1f} km")
    print(f"  - Average travel time: {avg_time:.2f} minutes")


if __name__ == '__main__':
    # Define paths
    project_root = Path(__file__).parent.parent
    stations_csv = project_root / 'data' / 'raw' / 'stations.csv'
    output_csv = project_root / 'data' / 'raw' / 'connections.csv'

    print("=" * 70)
    print("GENERATING STATION CONNECTIONS")
    print("=" * 70)
    print(f"\nInput: {stations_csv}")
    print(f"Output: {output_csv}\n")

    # Build connections
    connections = build_connections(stations_csv)

    # Write to CSV
    write_connections_csv(connections, output_csv)

    print("\n" + "=" * 70)
    print("✅ CONNECTIONS GENERATED SUCCESSFULLY")
    print("=" * 70)
    print("\n⚠️  NOTE: Travel times are ESTIMATED based on distance and")
    print("   average speeds. Recommend validation against official sources.")
