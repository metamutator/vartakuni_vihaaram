#!/usr/bin/env python3
"""Create initial SVG-to-station mapping file.

This script:
1. Extracts station labels from the SVG (grouping multi-line text)
2. Matches them to station names from stations.csv
3. Creates initial svg_name_map.csv
4. Exports unmatched labels for manual review
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import csv
from typing import List, Dict, Set, Tuple
import re
from collections import defaultdict


def extract_station_groups_from_svg(svg_path: Path) -> List[Dict]:
    """
    Extract station text labels from SVG, grouping multi-line station names.

    Returns:
        List of dicts with 'label', 'x', 'y' keys
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Collect all text elements with coordinates
    text_elements = []

    for text_elem in root.iter('{http://www.w3.org/2000/svg}text'):
        try:
            x = float(text_elem.get('x', '0'))
            y = float(text_elem.get('y', '0'))
            font_size = text_elem.get('font-size', '12')

            # Extract text from tspan elements
            tspans = text_elem.findall('.//{http://www.w3.org/2000/svg}tspan')
            for tspan in tspans:
                text = tspan.text
                if text:
                    text = text.strip()
                    # Filter out obvious non-station text
                    if (text and len(text) > 1 and
                        not re.search(r'\(20\d{2}\)', text) and
                        not re.search(r'Under studies', text) and
                        not re.search(r'Mothballed', text) and
                        not text.startswith('??') and
                        'Line' not in text or 'Punggol' in text):  # Keep specific cases

                        text_elements.append({
                            'text': text,
                            'x': x,
                            'y': y,
                            'font_size': font_size
                        })
        except (ValueError, TypeError):
            continue

    # Group text elements that are close together (multi-line station names)
    # Sort by x, then y
    text_elements.sort(key=lambda e: (e['x'], e['y']))

    grouped = []
    skip_indices = set()

    for i, elem in enumerate(text_elements):
        if i in skip_indices:
            continue

        # Start a new group
        group_text = [elem['text']]
        group_x = elem['x']
        group_y = elem['y']

        # Look for nearby elements (within 20 pixels vertically, same x ± 10)
        for j in range(i + 1, len(text_elements)):
            if j in skip_indices:
                continue

            other = text_elements[j]
            # Check if elements are part of the same station label
            if (abs(other['x'] - group_x) < 15 and
                abs(other['y'] - group_y) < 25):
                group_text.append(other['text'])
                skip_indices.add(j)

        # Combine grouped text
        combined = ' '.join(group_text)

        # Additional filtering for combined text
        if (len(combined) >= 3 and
            not combined.startswith('SINGAPORE') and
            not combined.startswith('Correct as at') and
            'Alignment of future' not in combined):

            grouped.append({
                'label': combined,
                'x': group_x,
                'y': group_y
            })

    return grouped


def load_stations(csv_path: Path) -> List[Dict]:
    """Load station data from CSV."""
    stations = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['operational_status'] == 'active':
                stations.append(row)
    return stations


def normalize_name(name: str) -> str:
    """Normalize name for matching."""
    # Remove special characters, convert to lowercase
    normalized = name.lower().strip()
    # Remove common suffixes
    normalized = normalized.replace(' station', '')
    # Standardize spacing
    normalized = ' '.join(normalized.split())
    return normalized


def match_svg_to_stations(svg_labels: List[Dict], stations: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """
    Match SVG labels to station IDs.

    Returns:
        (matched_mappings, unmatched_svg_labels)
    """
    # Create lookup dict by normalized station name
    station_lookup = defaultdict(list)
    for station in stations:
        norm_name = normalize_name(station['station_name'])
        station_lookup[norm_name].append(station)

    matched = []
    unmatched = []

    for svg_label in svg_labels:
        label = svg_label['label']
        norm_label = normalize_name(label)

        # Try exact match first
        if norm_label in station_lookup:
            stations_matched = station_lookup[norm_label]

            # Group all station IDs for this location
            station_ids = sorted([s['station_id'] for s in stations_matched])
            station_ids_str = ','.join(station_ids)

            # Create display label with IDs
            if len(station_ids) == 1:
                display_label = f"{label} ({station_ids[0]})"
            else:
                display_label = f"{label} ({', '.join(station_ids)})"

            matched.append({
                'svg_label': label,
                'station_ids': station_ids_str,
                'display_label': display_label,
                'x': svg_label['x'],
                'y': svg_label['y']
            })
        else:
            # Try partial matches
            found = False
            for station_norm, station_list in station_lookup.items():
                if norm_label in station_norm or station_norm in norm_label:
                    station_ids = sorted([s['station_id'] for s in station_list])
                    station_ids_str = ','.join(station_ids)

                    if len(station_ids) == 1:
                        display_label = f"{label} ({station_ids[0]})"
                    else:
                        display_label = f"{label} ({', '.join(station_ids)})"

                    matched.append({
                        'svg_label': label,
                        'station_ids': station_ids_str,
                        'display_label': display_label,
                        'x': svg_label['x'],
                        'y': svg_label['y']
                    })
                    found = True
                    break

            if not found:
                unmatched.append(label)

    return matched, unmatched


def main():
    # Paths
    svg_path = Path('data/raw/Singapore_MRT_and_LRT_System_Map.svg')
    stations_path = Path('data/raw/stations.csv')
    mapping_output = Path('data/processed/svg_name_map.csv')
    unmatched_output = Path('data/processed/unmatched_svg_labels.csv')

    print("=" * 70)
    print("US-801: Creating SVG-to-Station Mapping")
    print("=" * 70)

    # Extract SVG labels
    print(f"\n1. Extracting labels from {svg_path.name}...")
    svg_labels = extract_station_groups_from_svg(svg_path)
    print(f"   Found {len(svg_labels)} station labels in SVG")

    # Load stations
    print(f"\n2. Loading active stations from {stations_path.name}...")
    stations = load_stations(stations_path)
    print(f"   Found {len(stations)} active stations")

    # Match
    print(f"\n3. Matching SVG labels to station IDs...")
    matched, unmatched = match_svg_to_stations(svg_labels, stations)
    print(f"   Matched: {len(matched)}")
    print(f"   Unmatched: {len(unmatched)}")

    # Write mapping
    print(f"\n4. Writing mapping to {mapping_output}...")
    with open(mapping_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['svg_label', 'station_ids', 'display_label', 'x', 'y'])
        writer.writeheader()
        for row in sorted(matched, key=lambda x: x['svg_label']):
            writer.writerow(row)
    print(f"   ✓ Wrote {len(matched)} mappings")

    # Write unmatched
    print(f"\n5. Writing unmatched labels to {unmatched_output}...")
    with open(unmatched_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['svg_label', 'suggested_station_name', 'notes'])
        for label in sorted(unmatched):
            writer.writerow([label, '', 'Manual mapping required'])
    print(f"   ✓ Wrote {len(unmatched)} unmatched labels")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    match_rate = (len(matched) / (len(matched) + len(unmatched)) * 100) if (len(matched) + len(unmatched)) > 0 else 0
    print(f"Match rate: {match_rate:.1f}% ({len(matched)}/{len(matched) + len(unmatched)})")

    if unmatched:
        print(f"\nUnmatched labels (first 20):")
        for label in sorted(unmatched)[:20]:
            print(f"  - {label}")
        if len(unmatched) > 20:
            print(f"  ... and {len(unmatched) - 20} more")

    print(f"\nNext steps:")
    print(f"  1. Review {unmatched_output}")
    print(f"  2. Manually update {mapping_output} for unmatched labels")
    print(f"  3. Run US-802 validation script")


if __name__ == '__main__':
    main()
