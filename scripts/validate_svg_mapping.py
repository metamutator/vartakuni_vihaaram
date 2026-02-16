#!/usr/bin/env python3
"""Validate SVG-to-station mapping and report coverage statistics.

This script:
1. Validates svg_name_map.csv completeness
2. Checks for missing/ambiguous mappings
3. Reports coverage of operational stations
4. Identifies unmapped stations from stations.csv
5. Provides actionable recommendations
"""

from pathlib import Path
import csv
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def load_mapping(mapping_path: Path) -> Dict[str, Dict]:
    """Load SVG-to-station mapping."""
    mapping = {}
    with open(mapping_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row['svg_label']] = {
                'station_ids': row['station_ids'].split(','),
                'display_label': row['display_label'],
                'x': row['x'],
                'y': row['y']
            }
    return mapping


def load_stations(csv_path: Path) -> List[Dict]:
    """Load all active stations."""
    stations = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['operational_status'] == 'active':
                stations.append(row)
    return stations


def load_unmatched(unmatched_path: Path) -> List[str]:
    """Load unmatched SVG labels."""
    unmatched = []
    try:
        with open(unmatched_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                unmatched.append(row['svg_label'])
    except FileNotFoundError:
        pass
    return unmatched


def validate_mapping(
    mapping: Dict[str, Dict],
    stations: List[Dict],
    unmatched: List[str]
) -> Tuple[Dict, Dict]:
    """
    Validate mapping and return statistics.

    Returns:
        (stats_dict, issues_dict)
    """
    # Get all station IDs from mapping
    mapped_station_ids = set()
    for svg_label, data in mapping.items():
        for station_id in data['station_ids']:
            mapped_station_ids.add(station_id.strip())

    # Get all active station IDs
    all_station_ids = set(s['station_id'] for s in stations)

    # Find unmapped stations
    unmapped_stations = all_station_ids - mapped_station_ids

    # Calculate coverage
    coverage_pct = (len(mapped_station_ids) / len(all_station_ids)) * 100 if all_station_ids else 0

    # Find duplicate mappings (multiple SVG labels mapping to same station)
    station_to_svg = defaultdict(list)
    for svg_label, data in mapping.items():
        for station_id in data['station_ids']:
            station_to_svg[station_id.strip()].append(svg_label)

    duplicates = {sid: labels for sid, labels in station_to_svg.items() if len(labels) > 1}

    # Statistics
    stats = {
        'total_active_stations': len(all_station_ids),
        'mapped_stations': len(mapped_station_ids),
        'unmapped_stations': len(unmapped_stations),
        'coverage_pct': coverage_pct,
        'total_svg_labels': len(mapping),
        'unmatched_svg_labels': len(unmatched),
        'duplicate_mappings': len(duplicates)
    }

    # Issues
    issues = {
        'unmapped_stations': unmapped_stations,
        'duplicates': duplicates,
        'unmatched_svg': unmatched
    }

    return stats, issues


def print_validation_report(stats: Dict, issues: Dict, stations: List[Dict]):
    """Print a comprehensive validation report."""
    print("=" * 70)
    print("US-802: SVG Mapping Validation Report")
    print("=" * 70)

    # Coverage summary
    print("\n📊 COVERAGE SUMMARY")
    print("-" * 70)
    print(f"Active stations in dataset:     {stats['total_active_stations']}")
    print(f"Stations mapped to SVG:         {stats['mapped_stations']}")
    print(f"Stations not mapped:            {stats['unmapped_stations']}")
    print(f"Coverage percentage:            {stats['coverage_pct']:.1f}%")
    print()
    print(f"Total SVG labels mapped:        {stats['total_svg_labels']}")
    print(f"Unmatched SVG labels:           {stats['unmatched_svg_labels']}")

    # Coverage status
    print()
    if stats['coverage_pct'] >= 95:
        print("✅ Coverage ≥ 95% - MEETS ACCEPTANCE CRITERIA")
    else:
        needed = int((0.95 * stats['total_active_stations']) - stats['mapped_stations'])
        print(f"⚠️  Coverage < 95% - Need to map {needed} more stations")

    # Unmapped stations
    if issues['unmapped_stations']:
        print("\n🔍 UNMAPPED STATIONS")
        print("-" * 70)
        print(f"The following {len(issues['unmapped_stations'])} stations are not mapped to any SVG labels:")
        print()

        # Group by line
        by_line = defaultdict(list)
        station_lookup = {s['station_id']: s for s in stations}

        for station_id in sorted(issues['unmapped_stations']):
            if station_id in station_lookup:
                station = station_lookup[station_id]
                line = station['line_code']
                by_line[line].append(f"{station_id}: {station['station_name']}")

        for line in sorted(by_line.keys()):
            print(f"\n{line} Line:")
            for entry in by_line[line]:
                print(f"  - {entry}")

    # Duplicate mappings
    if issues['duplicates']:
        print("\n⚠️  DUPLICATE MAPPINGS")
        print("-" * 70)
        print("The following stations are mapped to multiple SVG labels:")
        print("(This may be intentional for stations with multiple entrances)")
        print()
        for station_id in sorted(issues['duplicates'].keys()):
            labels = issues['duplicates'][station_id]
            print(f"  {station_id}: {', '.join(labels)}")

    # Unmatched SVG labels (sample)
    if issues['unmatched_svg']:
        print("\n📋 UNMATCHED SVG LABELS (Sample)")
        print("-" * 70)
        print("SVG labels that don't match any active stations:")
        print("(See data/processed/unmatched_svg_labels.csv for full list)")
        print()
        for label in sorted(issues['unmatched_svg'])[:15]:
            print(f"  - {label}")
        if len(issues['unmatched_svg']) > 15:
            print(f"  ... and {len(issues['unmatched_svg']) - 15} more")

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 70)
    if stats['coverage_pct'] < 95:
        print("1. Review unmapped stations list above")
        print("2. Search for corresponding labels in unmatched_svg_labels.csv")
        print("3. Manually add mappings to svg_name_map.csv")
        print("4. Re-run this validation script")
    elif issues['unmapped_stations']:
        print("1. Coverage ≥ 95% but some stations remain unmapped")
        print("2. These may be stations without visible SVG labels")
        print("3. Review list above and document in svg_map_integration.md")
    else:
        print("✅ All active stations are mapped!")

    print("\n" + "=" * 70)


def main():
    # Paths
    mapping_file = Path('data/processed/svg_name_map.csv')
    stations_file = Path('data/raw/stations.csv')
    unmatched_file = Path('data/processed/unmatched_svg_labels.csv')

    # Load data
    try:
        mapping = load_mapping(mapping_file)
    except FileNotFoundError:
        print(f"❌ Error: {mapping_file} not found!")
        print("Run create_svg_mapping.py first.")
        return

    stations = load_stations(stations_file)
    unmatched = load_unmatched(unmatched_file)

    # Validate
    stats, issues = validate_mapping(mapping, stations, unmatched)

    # Print report
    print_validation_report(stats, issues, stations)

    # Exit code based on coverage
    if stats['coverage_pct'] < 95:
        exit(1)
    else:
        exit(0)


if __name__ == '__main__':
    main()
