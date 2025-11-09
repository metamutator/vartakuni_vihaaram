#!/usr/bin/env python3
"""
Convert sgraildata GeoJSON to stations CSV format.

This script reads the sg-rail.geojson file from the sgraildata repository
and converts it to our project's stations.csv format.

Data source: https://github.com/cheeaun/sgraildata
"""

import json
import csv
from pathlib import Path
from typing import List, Dict

def parse_station_codes(station_codes: str) -> List[str]:
    """
    Parse station codes which may be combined for multi-line stations.

    Examples:
        'NS10' -> ['NS10']
        'DT16-CE1' -> ['DT16', 'CE1']
        'NS24-NE6-CC1' -> ['NS24', 'NE6', 'CC1']
    """
    if not station_codes:
        return []
    return [code.strip() for code in station_codes.split('-')]


def extract_line_code(station_code: str) -> str:
    """
    Extract line code from station code.

    Examples:
        'NS10' -> 'NS'
        'EW9' -> 'EW'
        'CC12' -> 'CC'
        'BP9' -> 'BP'
    """
    # Extract letters from the beginning of the code
    line_code = ''
    for char in station_code:
        if char.isalpha():
            line_code += char
        else:
            break
    return line_code


def convert_geojson_to_stations_csv(
    geojson_path: Path,
    output_csv_path: Path
) -> None:
    """
    Convert GeoJSON to stations CSV format.

    Multi-line stations are split into separate rows, one per platform.
    """
    # Read GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stations = []

    # Process each feature
    for feature in data['features']:
        props = feature['properties']
        geom = feature['geometry']

        # Only process stations (not routes or other features)
        if props.get('stop_type') != 'station':
            continue

        station_name = props.get('name', '')
        station_codes_str = props.get('station_codes', '')
        coords = geom['coordinates']  # [longitude, latitude]

        # Parse station codes
        station_codes = parse_station_codes(station_codes_str)

        if not station_codes:
            print(f"Warning: No station codes for {station_name}")
            continue

        # Create one entry per line for multi-line stations
        for station_code in station_codes:
            line_code = extract_line_code(station_code)

            # Operational status: assume all active for now
            # This can be refined later if we have data on under-construction stations
            operational_status = 'active'

            stations.append({
                'station_id': station_code,
                'station_name': station_name,
                'line_code': line_code,
                'latitude': coords[1],  # GeoJSON uses [lon, lat]
                'longitude': coords[0],
                'operational_status': operational_status
            })

    # Sort by station_id for consistency
    stations.sort(key=lambda x: x['station_id'])

    # Write CSV
    fieldnames = [
        'station_id',
        'station_name',
        'line_code',
        'latitude',
        'longitude',
        'operational_status'
    ]

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stations)

    print(f"✓ Converted {len(stations)} station entries")
    print(f"✓ Written to {output_csv_path}")

    # Print summary statistics
    unique_stations = len(set(s['station_name'] for s in stations))
    unique_lines = len(set(s['line_code'] for s in stations))
    multi_line_stations = len([s for s in stations if len(parse_station_codes(
        next(f['properties']['station_codes']
             for f in data['features']
             if f['properties'].get('name') == s['station_name'])
    )) > 1])

    print(f"\nSummary:")
    print(f"  - Total station entries: {len(stations)}")
    print(f"  - Unique station names: {unique_stations}")
    print(f"  - Unique line codes: {unique_lines}")
    print(f"  - Multi-line interchange stations: {multi_line_stations // len(set(s['station_name'] for s in stations if len(parse_station_codes(next(f['properties']['station_codes'] for f in data['features'] if f['properties'].get('name') == s['station_name']))) > 1))}")


if __name__ == '__main__':
    # Define paths
    project_root = Path(__file__).parent.parent
    geojson_path = project_root / 'data' / 'raw' / 'sg-rail.geojson'
    output_csv_path = project_root / 'data' / 'raw' / 'stations.csv'

    # Convert
    convert_geojson_to_stations_csv(geojson_path, output_csv_path)
