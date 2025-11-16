#!/usr/bin/env python3
"""Prune SVG map to show only operational stations with station IDs.

This script:
1. Reads the base SVG map
2. Uses svg_name_map.csv to identify operational stations
3. Updates station labels to include station IDs
4. Hides/removes non-operational stations
5. Preserves CC BY-SA 3.0 attribution
6. Writes pruned map to data/processed/
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import csv
from typing import Dict, Set
import re


def load_mapping(mapping_path: Path) -> Dict[str, Dict]:
    """
    Load SVG-to-station mapping.

    Returns:
        Dict mapping svg_label to {station_ids, display_label, x, y}
    """
    mapping = {}
    with open(mapping_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row['svg_label']] = {
                'station_ids': row['station_ids'],
                'display_label': row['display_label'],
                'x': float(row['x']),
                'y': float(row['y'])
            }
    return mapping


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    if not text:
        return ""
    return ' '.join(text.strip().split())


def update_svg_labels(svg_path: Path, mapping: Dict[str, Dict], output_path: Path):
    """
    Update SVG with station IDs and hide non-operational stations.

    Args:
        svg_path: Path to input SVG
        mapping: Mapping dict from load_mapping()
        output_path: Path for output SVG
    """
    # Register SVG namespace
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('svg', 'http://www.w3.org/2000/svg')

    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Track statistics
    labels_updated = 0
    labels_hidden = 0

    # Build a set of all mapped labels for quick lookup
    mapped_labels = set(mapping.keys())

    # Process all text elements
    for text_elem in root.iter('{http://www.w3.org/2000/svg}text'):
        # Get text content from tspan elements
        tspans = text_elem.findall('.//{http://www.w3.org/2000/svg}tspan')

        for tspan in tspans:
            original_text = tspan.text
            if not original_text:
                continue

            normalized = normalize_text(original_text)

            # Check if this label is in our mapping
            if normalized in mapped_labels:
                # Update with display label (includes station IDs)
                new_label = mapping[normalized]['display_label']
                tspan.text = new_label
                labels_updated += 1

            else:
                # Check if this looks like a station label that we should hide
                # (future stations, unmatched stations, etc.)
                # We'll mark it as semi-transparent instead of removing it
                # to preserve the SVG structure
                if (len(normalized) > 2 and
                    not normalized.startswith('SINGAPORE') and
                    not normalized.startswith('Correct') and
                    'Line' not in normalized):

                    # Add opacity to parent text element to fade it out
                    text_elem.set('opacity', '0.2')
                    labels_hidden += 1

    # Add comment documenting this processing
    comment = ET.Comment(
        f' Processed by prune_svg_map.py - Updated {labels_updated} labels, '
        f'hid {labels_hidden} non-operational stations '
    )
    root.insert(0, comment)

    # Ensure attribution is preserved (add if not present)
    # Check for existing title
    existing_title = root.find('.//{http://www.w3.org/2000/svg}title')
    if existing_title is None:
        title = ET.Element('{http://www.w3.org/2000/svg}title')
        title.text = 'Singapore MRT/LRT system map'
        root.insert(0, title)

    # Add attribution comment
    attribution = ET.Comment(
        ' Original map: Singapore MRT/LRT System Map by Wikipedia contributors. '
        'Licensed under CC BY-SA 3.0. Source: https://commons.wikimedia.org/wiki/File:Singapore_MRT_and_LRT_System_Map.svg '
    )
    root.insert(0, attribution)

    # Write output
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    return labels_updated, labels_hidden


def main():
    # Paths
    svg_input = Path('data/raw/Singapore_MRT_and_LRT_System_Map.svg')
    mapping_file = Path('data/processed/svg_name_map.csv')
    svg_output = Path('data/processed/sg_mrt_lrt_built_only.svg')

    print("=" * 70)
    print("US-801: Pruning SVG Map to Operational Stations")
    print("=" * 70)

    # Load mapping
    print(f"\n1. Loading mapping from {mapping_file.name}...")
    try:
        mapping = load_mapping(mapping_file)
        print(f"   ✓ Loaded {len(mapping)} station mappings")
    except FileNotFoundError:
        print(f"   ✗ Error: {mapping_file} not found!")
        print(f"   Run create_svg_mapping.py first to create the mapping file.")
        return

    # Update SVG
    print(f"\n2. Processing {svg_input.name}...")
    print(f"   - Adding station IDs to labels")
    print(f"   - Hiding non-operational stations")
    print(f"   - Preserving CC BY-SA 3.0 attribution")

    updated, hidden = update_svg_labels(svg_input, mapping, svg_output)

    print(f"\n3. Results:")
    print(f"   ✓ Updated {updated} station labels with IDs")
    print(f"   ✓ Hidden {hidden} non-operational/unmatched labels")
    print(f"   ✓ Wrote pruned map to {svg_output}")

    # Print file sizes
    input_size = svg_input.stat().st_size / 1024
    output_size = svg_output.stat().st_size / 1024
    print(f"\n4. File sizes:")
    print(f"   Input:  {input_size:.1f} KB")
    print(f"   Output: {output_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✓ US-801 Complete")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"  1. Review {svg_output} in a browser or SVG viewer")
    print(f"  2. Check data/processed/unmatched_svg_labels.csv for labels to map")
    print(f"  3. Update svg_name_map.csv as needed")
    print(f"  4. Re-run this script to apply updates")


if __name__ == '__main__':
    main()
