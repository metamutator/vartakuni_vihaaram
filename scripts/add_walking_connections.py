#!/usr/bin/env python3
"""
Add walking connections to the metro network.

This script processes walking connection data and adds transfer times:
1. Platform-to-platform transfers at interchange stations (walk_transfer)
2. Walking connections between nearby stations (walk_between_stations)

Data sources:
- sg-rail-walks.geojson from sgraildata (actual walking times)
- Estimated transfers for interchanges not in source data

Walking time estimation:
- Typical walking speed: 80 m/min (4.8 km/h)
- Interchange transfers: 2-5 minutes (estimated if not in source)
- Between-station walks: based on distance
"""

import json
import csv
import math
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

# Default walking speeds and transfer times
DEFAULT_WALKING_SPEED_M_PER_MIN = 80  # 4.8 km/h
DEFAULT_INTERCHANGE_TRANSFER_MIN = 3  # Default transfer time if not specified

# Maximum walking distance between stations (meters)
MAX_WALK_BETWEEN_STATIONS_M = 800  # ~10 min walk


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great circle distance in kilometers."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Earth radius in km
    return c * r


def parse_station_codes(station_codes: str) -> List[str]:
    """Parse combined station codes into list."""
    if not station_codes:
        return []
    # Handle codes like "NS24-NE6-CC1" or "EW12-DT14"
    return [code.strip() for code in station_codes.split('-')]


def load_walking_connections(geojson_path: Path) -> List[Dict]:
    """Load walking connections from sgraildata GeoJSON."""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    walks = []
    for feature in data['features']:
        props = feature.get('properties', {})
        if props and 'duration_min' in props:
            codes1 = props.get('station_codes_1', '')
            codes2 = props.get('station_codes_2', '')

            if codes1 and codes2:
                walks.append({
                    'station_codes_1': codes1,
                    'station_codes_2': codes2,
                    'duration_min': props.get('duration_min'),
                    'exit_1': props.get('exit_name_1', ''),
                    'exit_2': props.get('exit_name_2', '')
                })

    return walks


def load_stations(stations_csv: Path) -> Dict[str, Dict]:
    """Load stations and create lookup dictionary."""
    with open(stations_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        stations = list(reader)

    # Create lookup by station_id
    station_lookup = {}
    for s in stations:
        station_lookup[s['station_id']] = {
            'name': s['station_name'],
            'line_code': s['line_code'],
            'lat': float(s['latitude']),
            'lon': float(s['longitude'])
        }

    return station_lookup


def get_interchange_stations(station_lookup: Dict[str, Dict]) -> Dict[str, List[str]]:
    """Group stations by name to find interchanges."""
    by_name = defaultdict(list)
    for station_id, info in station_lookup.items():
        by_name[info['name']].append(station_id)

    # Return only interchanges (multiple platforms)
    return {name: ids for name, ids in by_name.items() if len(ids) > 1}


def create_walking_connections(
    stations_csv: Path,
    walks_geojson: Path,
    next_connection_id: int
) -> List[Dict]:
    """
    Create walking connections from source data and fill in gaps.

    Returns list of walking connection dictionaries.
    """
    # Load data
    station_lookup = load_stations(stations_csv)
    source_walks = load_walking_connections(walks_geojson)
    interchanges = get_interchange_stations(station_lookup)

    walking_connections = []
    processed_pairs = set()  # Track which pairs we've already connected

    print(f"Found {len(source_walks)} walking connections in source data")
    print(f"Found {len(interchanges)} interchange stations")

    # Process walking connections from source data
    for walk in source_walks:
        # Parse station codes
        codes1_list = parse_station_codes(walk['station_codes_1'])
        codes2_list = parse_station_codes(walk['station_codes_2'])

        # Try to match to our station IDs
        for code1 in codes1_list:
            for code2 in codes2_list:
                if code1 in station_lookup and code2 in station_lookup:
                    station1 = station_lookup[code1]
                    station2 = station_lookup[code2]

                    # Determine connection type
                    same_station = station1['name'] == station2['name']
                    conn_type = 'walk_transfer' if same_station else 'walk_between_stations'

                    # Calculate distance for metadata
                    distance_m = int(haversine_distance(
                        station1['lat'], station1['lon'],
                        station2['lat'], station2['lon']
                    ) * 1000)

                    # Create bidirectional connections
                    pair = tuple(sorted([code1, code2]))
                    if pair not in processed_pairs:
                        # Forward
                        walking_connections.append({
                            'connection_id': f"{next_connection_id:04d}",
                            'from_station_id': code1,
                            'to_station_id': code2,
                            'connection_type': conn_type,
                            'travel_time_minutes': float(walk['duration_min']),
                            'distance_meters': distance_m,
                            'line_code': ''  # Not applicable for walking
                        })
                        next_connection_id += 1

                        # Backward
                        walking_connections.append({
                            'connection_id': f"{next_connection_id:04d}",
                            'from_station_id': code2,
                            'to_station_id': code1,
                            'connection_type': conn_type,
                            'travel_time_minutes': float(walk['duration_min']),
                            'distance_meters': distance_m,
                            'line_code': ''
                        })
                        next_connection_id += 1

                        processed_pairs.add(pair)

    print(f"Processed {len(processed_pairs)} walking connections from source")

    # Fill in missing interchange transfers
    missing_transfers = 0
    for station_name, platform_ids in interchanges.items():
        # Create transfers between all platform pairs
        for i, id1 in enumerate(platform_ids):
            for id2 in platform_ids[i+1:]:
                pair = tuple(sorted([id1, id2]))

                if pair not in processed_pairs:
                    # Estimate transfer time (2-5 min depending on distance)
                    station1 = station_lookup[id1]
                    station2 = station_lookup[id2]

                    distance_m = int(haversine_distance(
                        station1['lat'], station1['lon'],
                        station2['lat'], station2['lon']
                    ) * 1000)

                    # Estimate: base 2 min + distance-based time
                    transfer_time = 2.0 + (distance_m / DEFAULT_WALKING_SPEED_M_PER_MIN)
                    transfer_time = min(transfer_time, 5.0)  # Cap at 5 min
                    transfer_time = round(transfer_time, 2)

                    # Forward
                    walking_connections.append({
                        'connection_id': f"{next_connection_id:04d}",
                        'from_station_id': id1,
                        'to_station_id': id2,
                        'connection_type': 'walk_transfer',
                        'travel_time_minutes': transfer_time,
                        'distance_meters': distance_m,
                        'line_code': ''
                    })
                    next_connection_id += 1

                    # Backward
                    walking_connections.append({
                        'connection_id': f"{next_connection_id:04d}",
                        'from_station_id': id2,
                        'to_station_id': id1,
                        'connection_type': 'walk_transfer',
                        'travel_time_minutes': transfer_time,
                        'distance_meters': distance_m,
                        'line_code': ''
                    })
                    next_connection_id += 1

                    processed_pairs.add(pair)
                    missing_transfers += 1

    if missing_transfers > 0:
        print(f"Added {missing_transfers} estimated interchange transfers")

    return walking_connections


def merge_connections(
    train_connections_csv: Path,
    walking_connections: List[Dict],
    output_csv: Path
):
    """Merge train and walking connections into single CSV."""
    # Read existing train connections
    with open(train_connections_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        train_connections = list(reader)

    # Combine
    all_connections = train_connections + walking_connections

    # Write combined file
    fieldnames = [
        'connection_id',
        'from_station_id',
        'to_station_id',
        'connection_type',
        'travel_time_minutes',
        'distance_meters',
        'line_code'
    ]

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_connections)

    # Print statistics
    by_type = defaultdict(int)
    for conn in all_connections:
        by_type[conn['connection_type']] += 1

    print(f"\n✓ Written to {output_csv}")
    print(f"\nConnection statistics:")
    print(f"  Train connections: {by_type['train']}")
    print(f"  Walk transfers (interchanges): {by_type['walk_transfer']}")
    print(f"  Walk between stations: {by_type['walk_between_stations']}")
    print(f"  Total connections: {len(all_connections)}")


if __name__ == '__main__':
    project_root = Path(__file__).parent.parent

    stations_csv = project_root / 'data' / 'raw' / 'stations.csv'
    walks_geojson = project_root / 'data' / 'raw' / 'sg-rail-walks.geojson'
    train_connections_csv = project_root / 'data' / 'raw' / 'connections.csv'
    output_csv = project_root / 'data' / 'raw' / 'connections.csv'

    print("=" * 70)
    print("ADDING WALKING CONNECTIONS")
    print("=" * 70)
    print(f"\nInput files:")
    print(f"  Stations: {stations_csv}")
    print(f"  Walking data: {walks_geojson}")
    print(f"  Train connections: {train_connections_csv}")
    print(f"Output: {output_csv}\n")

    # Determine next connection ID
    with open(train_connections_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        existing = list(reader)
        next_id = len(existing) + 1

    # Create walking connections
    walking_connections = create_walking_connections(
        stations_csv,
        walks_geojson,
        next_id
    )

    # Merge and write
    merge_connections(train_connections_csv, walking_connections, output_csv)

    print("\n" + "=" * 70)
    print("✅ WALKING CONNECTIONS ADDED SUCCESSFULLY")
    print("=" * 70)
