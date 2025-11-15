#!/usr/bin/env python3
"""
Fix Disconnected LRT and TE Extension Connections (US-108)

Adds missing connections to make the graph fully connected:
1. Sengkang LRT: STC hub ↔ SE1 (East Loop) and STC hub ↔ SW1 (West Loop)
2. Punggol LRT: PTC hub ↔ PE1 (East Loop) and PTC hub ↔ PW1 (West Loop)
3. Thomson-East Coast Line: TE20 ↔ TE22 (direct, bypassing unopened TE21)
"""

import csv
from pathlib import Path
from typing import Dict, List
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.

    Returns:
        Distance in meters
    """
    R = 6371000  # Earth's radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def estimate_travel_time(distance_m: float, line_type: str, average_speeds: Dict[str, float],
                        dwell_time: float = 0.5) -> float:
    """
    Estimate travel time based on distance and line type.

    Args:
        distance_m: Distance in meters
        line_type: 'mrt' or 'lrt'
        average_speeds: Dictionary with average speeds in km/h
        dwell_time: Station dwell time in minutes

    Returns:
        Travel time in minutes
    """
    distance_km = distance_m / 1000
    avg_speed = average_speeds[line_type]
    travel_time = (distance_km / avg_speed) * 60
    total_time = travel_time + dwell_time
    return round(total_time, 2)


def load_stations(stations_csv: Path) -> Dict[str, Dict]:
    """Load stations data into dictionary."""
    stations = {}
    with open(stations_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stations[row['station_id']] = {
                'name': row['station_name'],
                'line_code': row['line_code'],
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'operational_status': row['operational_status']
            }
    return stations


def get_next_connection_id(connections_csv: Path) -> int:
    """Get the next available connection ID."""
    max_id = 0
    with open(connections_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn_id = int(row['connection_id'])
            max_id = max(max_id, conn_id)
    return max_id + 1


def create_missing_connections(
    stations: Dict[str, Dict],
    next_id: int,
    average_speeds: Dict[str, float] = None
) -> List[Dict]:
    """
    Create the missing connections for disconnected components.

    Returns:
        List of connection dictionaries
    """
    if average_speeds is None:
        average_speeds = {
            'mrt': 50.0,  # km/h
            'lrt': 35.0   # km/h
        }

    connections = []
    current_id = next_id

    # 1. Sengkang LRT: STC ↔ SE1 and STC ↔ SW1
    # STC is the hub station for Sengkang LRT loops
    stc = stations['STC']
    se1 = stations['SE1']
    sw1 = stations['SW1']

    # STC ↔ SE1
    dist_se = haversine_distance(stc['latitude'], stc['longitude'],
                                  se1['latitude'], se1['longitude'])
    time_se = estimate_travel_time(dist_se, 'lrt', average_speeds)

    connections.extend([
        {
            'connection_id': str(current_id),
            'from_station_id': 'STC',
            'to_station_id': 'SE1',
            'connection_type': 'train',
            'travel_time_minutes': str(time_se),
            'distance_meters': str(int(dist_se)),
            'line_code': 'SE'
        },
        {
            'connection_id': str(current_id + 1),
            'from_station_id': 'SE1',
            'to_station_id': 'STC',
            'connection_type': 'train',
            'travel_time_minutes': str(time_se),
            'distance_meters': str(int(dist_se)),
            'line_code': 'SE'
        }
    ])
    current_id += 2

    # STC ↔ SW1
    dist_sw = haversine_distance(stc['latitude'], stc['longitude'],
                                  sw1['latitude'], sw1['longitude'])
    time_sw = estimate_travel_time(dist_sw, 'lrt', average_speeds)

    connections.extend([
        {
            'connection_id': str(current_id),
            'from_station_id': 'STC',
            'to_station_id': 'SW1',
            'connection_type': 'train',
            'travel_time_minutes': str(time_sw),
            'distance_meters': str(int(dist_sw)),
            'line_code': 'SW'
        },
        {
            'connection_id': str(current_id + 1),
            'from_station_id': 'SW1',
            'to_station_id': 'STC',
            'connection_type': 'train',
            'travel_time_minutes': str(time_sw),
            'distance_meters': str(int(dist_sw)),
            'line_code': 'SW'
        }
    ])
    current_id += 2

    # 2. Punggol LRT: PTC ↔ PE1 and PTC ↔ PW1
    # PTC is the hub station for Punggol LRT loops
    ptc = stations['PTC']
    pe1 = stations['PE1']
    pw1 = stations['PW1']

    # PTC ↔ PE1
    dist_pe = haversine_distance(ptc['latitude'], ptc['longitude'],
                                  pe1['latitude'], pe1['longitude'])
    time_pe = estimate_travel_time(dist_pe, 'lrt', average_speeds)

    connections.extend([
        {
            'connection_id': str(current_id),
            'from_station_id': 'PTC',
            'to_station_id': 'PE1',
            'connection_type': 'train',
            'travel_time_minutes': str(time_pe),
            'distance_meters': str(int(dist_pe)),
            'line_code': 'PE'
        },
        {
            'connection_id': str(current_id + 1),
            'from_station_id': 'PE1',
            'to_station_id': 'PTC',
            'connection_type': 'train',
            'travel_time_minutes': str(time_pe),
            'distance_meters': str(int(dist_pe)),
            'line_code': 'PE'
        }
    ])
    current_id += 2

    # PTC ↔ PW1
    dist_pw = haversine_distance(ptc['latitude'], ptc['longitude'],
                                  pw1['latitude'], pw1['longitude'])
    time_pw = estimate_travel_time(dist_pw, 'lrt', average_speeds)

    connections.extend([
        {
            'connection_id': str(current_id),
            'from_station_id': 'PTC',
            'to_station_id': 'PW1',
            'connection_type': 'train',
            'travel_time_minutes': str(time_pw),
            'distance_meters': str(int(dist_pw)),
            'line_code': 'PW'
        },
        {
            'connection_id': str(current_id + 1),
            'from_station_id': 'PW1',
            'to_station_id': 'PTC',
            'connection_type': 'train',
            'travel_time_minutes': str(time_pw),
            'distance_meters': str(int(dist_pw)),
            'line_code': 'PW'
        }
    ])
    current_id += 2

    # 3. Thomson-East Coast Line: TE20 ↔ TE22 (direct, bypassing unopened TE21)
    te20 = stations['TE20']
    te22 = stations['TE22']

    dist_te = haversine_distance(te20['latitude'], te20['longitude'],
                                  te22['latitude'], te22['longitude'])
    time_te = estimate_travel_time(dist_te, 'mrt', average_speeds)

    connections.extend([
        {
            'connection_id': str(current_id),
            'from_station_id': 'TE20',
            'to_station_id': 'TE22',
            'connection_type': 'train',
            'travel_time_minutes': str(time_te),
            'distance_meters': str(int(dist_te)),
            'line_code': 'TE'
        },
        {
            'connection_id': str(current_id + 1),
            'from_station_id': 'TE22',
            'to_station_id': 'TE20',
            'connection_type': 'train',
            'travel_time_minutes': str(time_te),
            'distance_meters': str(int(dist_te)),
            'line_code': 'TE'
        }
    ])

    return connections


def add_connections_to_csv(
    connections_csv: Path,
    new_connections: List[Dict]
) -> None:
    """Append new connections to connections.csv file."""
    with open(connections_csv, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['connection_id', 'from_station_id', 'to_station_id',
                     'connection_type', 'travel_time_minutes', 'distance_meters', 'line_code']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        for conn in new_connections:
            writer.writerow(conn)


def main():
    """Main execution function."""
    # Define paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data' / 'raw'
    stations_csv = data_dir / 'stations.csv'
    connections_csv = data_dir / 'connections.csv'

    print("US-108: Fixing Disconnected LRT and TE Extension Connections")
    print("=" * 70)

    # Load stations
    print("\n📍 Loading stations...")
    stations = load_stations(stations_csv)
    print(f"   Loaded {len(stations)} stations")

    # Get next connection ID
    next_id = get_next_connection_id(connections_csv)
    print(f"\n🔗 Next connection ID: {next_id}")

    # Create missing connections
    print("\n🛠️  Creating missing connections...")
    new_connections = create_missing_connections(stations, next_id)

    print(f"\n   Created {len(new_connections)} new connections:")
    print(f"   - Sengkang LRT: STC ↔ SE1 (East Loop)")
    print(f"   - Sengkang LRT: STC ↔ SW1 (West Loop)")
    print(f"   - Punggol LRT: PTC ↔ PE1 (East Loop)")
    print(f"   - Punggol LRT: PTC ↔ PW1 (West Loop)")
    print(f"   - Thomson-East Coast: TE20 ↔ TE22 (direct, bypassing unopened TE21)")

    # Show details
    print("\n📊 Connection Details:")
    for conn in new_connections:
        print(f"   {conn['from_station_id']} → {conn['to_station_id']}: "
              f"{conn['travel_time_minutes']} min, {conn['distance_meters']}m "
              f"({conn['connection_type']}, line {conn['line_code']})")

    # Add to CSV
    print(f"\n💾 Adding connections to {connections_csv.name}...")
    add_connections_to_csv(connections_csv, new_connections)

    print("\n✅ Connections added successfully!")
    print("\n🔍 Next step: Run graph builder to validate connectivity")
    print("   python -m src.graph.builder")


if __name__ == '__main__':
    main()
