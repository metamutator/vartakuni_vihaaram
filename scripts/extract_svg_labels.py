#!/usr/bin/env python3
"""Extract station labels from SVG map for analysis and mapping.

This script parses the Singapore MRT/LRT SVG map and extracts all station
text labels to help create the mapping between SVG labels and station IDs.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import csv
from typing import List, Dict, Set
import re


def extract_station_labels_from_svg(svg_path: Path) -> List[Dict[str, str]]:
    """
    Extract all station text labels from the SVG map.

    Args:
        svg_path: Path to the SVG file

    Returns:
        List of dicts with keys: 'label', 'x', 'y', 'font_size'
    """
    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    labels = []

    # Find all text elements
    for text_elem in root.iter('{http://www.w3.org/2000/svg}text'):
        # Get position and font size
        x = text_elem.get('x', '')
        y = text_elem.get('y', '')
        font_size = text_elem.get('font-size', '')

        # Extract text from tspan elements
        tspans = text_elem.findall('.//{http://www.w3.org/2000/svg}tspan')

        for tspan in tspans:
            text = tspan.text
            if text:
                text = text.strip()
                # Filter out non-station labels (line names, legend, etc.)
                # Station labels are typically font-size 12 or larger
                # And don't contain parentheses with years or "Line" keyword
                if (text and
                    not re.search(r'\(20\d{2}\)', text) and  # Not future stations
                    not re.search(r'\(Under studies', text) and
                    not re.search(r'\(Mothballed', text) and
                    'Line' not in text and
                    'Station' not in text or text.endswith('Station')):

                    labels.append({
                        'label': text,
                        'x': x,
                        'y': y,
                        'font_size': font_size
                    })

    return labels


def clean_station_name(name: str) -> str:
    """Normalize station name for matching."""
    # Remove extra whitespace
    name = ' '.join(name.split())
    # Remove common suffixes
    name = name.replace(' Station', '')
    return name.strip()


def main():
    # Paths
    svg_path = Path('data/raw/Singapore_MRT_and_LRT_System_Map.svg')
    output_path = Path('data/processed/svg_labels_extracted.csv')

    print(f"Extracting labels from {svg_path}...")
    labels = extract_station_labels_from_svg(svg_path)

    # Remove duplicates and sort
    unique_labels = {}
    for item in labels:
        label = clean_station_name(item['label'])
        if label and len(label) > 2:  # Filter out very short labels
            if label not in unique_labels:
                unique_labels[label] = item

    print(f"\nFound {len(unique_labels)} unique station labels")

    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['label', 'x', 'y', 'font_size'])
        writer.writeheader()
        for label, data in sorted(unique_labels.items()):
            writer.writerow({
                'label': label,
                'x': data['x'],
                'y': data['y'],
                'font_size': data['font_size']
            })

    print(f"Wrote labels to {output_path}")
    print("\nSample labels:")
    for i, (label, _) in enumerate(sorted(unique_labels.items())[:20]):
        print(f"  - {label}")
    if len(unique_labels) > 20:
        print(f"  ... and {len(unique_labels) - 20} more")


if __name__ == '__main__':
    main()
