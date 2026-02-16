#!/usr/bin/env python3
"""Render a TSP tour onto the SVG map with directional arrows and step numbers.

This script:
1. Loads the pruned SVG map
2. Loads the station mapping
3. Accepts a tour as a list of station IDs
4. Draws the tour path with arrows and step numbers
5. Adds start/end markers
6. Outputs a new SVG file
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import csv
from typing import List, Dict, Tuple
import math
import json


def load_mapping(mapping_path: Path) -> Dict[str, Dict]:
    """Load SVG station mapping."""
    mapping = {}
    with open(mapping_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create entries for each station ID in this location
            station_ids = [sid.strip() for sid in row['station_ids'].split(',')]
            for station_id in station_ids:
                mapping[station_id] = {
                    'x': float(row['x']),
                    'y': float(row['y']),
                    'label': row['display_label']
                }
    return mapping


def calculate_midpoint(x1: float, y1: float, x2: float, y2: float, offset: float = 0.5) -> Tuple[float, float]:
    """Calculate a point between two coordinates."""
    return (
        x1 + (x2 - x1) * offset,
        y1 + (y2 - y1) * offset
    )


def calculate_angle(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate angle in degrees from point 1 to point 2."""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def create_arrowhead_marker(defs_elem, marker_id: str, color: str = "#FF0000"):
    """Create an arrowhead marker definition."""
    marker = ET.SubElement(defs_elem, 'marker', {
        'id': marker_id,
        'markerWidth': '10',
        'markerHeight': '10',
        'refX': '5',
        'refY': '3',
        'orient': 'auto',
        'markerUnits': 'strokeWidth'
    })

    ET.SubElement(marker, 'path', {
        'd': 'M0,0 L0,6 L9,3 z',
        'fill': color
    })


def render_tour_on_svg(
    svg_path: Path,
    mapping: Dict[str, Dict],
    tour: List[str],
    output_path: Path,
    tour_name: str = "TSP Tour",
    tour_color: str = "#FF0000",
    tour_width: str = "3",
    show_step_numbers: bool = True
):
    """
    Render a tour onto the SVG map.

    Args:
        svg_path: Path to pruned SVG
        mapping: Station ID to position mapping
        tour: Ordered list of station IDs
        output_path: Path for output SVG
        tour_name: Name of the tour (for legend)
        tour_color: Color for tour path
        tour_width: Width of tour path
        show_step_numbers: Whether to show step numbers
    """
    # Register namespaces
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('svg', 'http://www.w3.org/2000/svg')

    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Create defs element for markers if it doesn't exist
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    defs = root.find('.//svg:defs', ns)
    if defs is None:
        defs = ET.Element('{http://www.w3.org/2000/svg}defs')
        root.insert(0, defs)

    # Create arrowhead marker
    create_arrowhead_marker(defs, 'tour-arrow', tour_color)

    # Create a group for the tour overlay
    tour_group = ET.SubElement(root, '{http://www.w3.org/2000/svg}g', {
        'id': 'tour-overlay',
        'opacity': '0.9'
    })

    # Add a comment
    tour_comment = ET.Comment(f' Tour: {tour_name} - {len(tour)} stations ')
    tour_group.append(tour_comment)

    # Validate tour stations are in mapping
    missing_stations = [sid for sid in tour if sid not in mapping]
    if missing_stations:
        print(f"Warning: {len(missing_stations)} stations not in mapping: {missing_stations[:10]}")

    # Draw tour segments
    for i in range(len(tour)):
        current_station = tour[i]
        next_station = tour[(i + 1) % len(tour)]  # Wrap around for circular tour

        if current_station not in mapping or next_station not in mapping:
            continue

        x1, y1 = mapping[current_station]['x'], mapping[current_station]['y']
        x2, y2 = mapping[next_station]['x'], mapping[next_station]['y']

        # Draw line segment with arrowhead
        line = ET.SubElement(tour_group, '{http://www.w3.org/2000/svg}line', {
            'x1': str(x1),
            'y1': str(y1),
            'x2': str(x2),
            'y2': str(y2),
            'stroke': tour_color,
            'stroke-width': tour_width,
            'stroke-opacity': '0.8',
            'marker-end': 'url(#tour-arrow)'
        })

    # Add step numbers and markers
    if show_step_numbers:
        for i, station_id in enumerate(tour):
            if station_id not in mapping:
                continue

            x, y = mapping[station_id]['x'], mapping[station_id]['y']
            step_num = i + 1

            # Circle background for step number
            circle = ET.SubElement(tour_group, '{http://www.w3.org/2000/svg}circle', {
                'cx': str(x),
                'cy': str(y),
                'r': '8',
                'fill': '#FFFFFF' if i > 0 else '#00FF00',  # Green for start
                'stroke': tour_color,
                'stroke-width': '2'
            })

            # Step number text
            text = ET.SubElement(tour_group, '{http://www.w3.org/2000/svg}text', {
                'x': str(x),
                'y': str(y + 4),  # Offset for vertical centering
                'text-anchor': 'middle',
                'font-family': 'Arial',
                'font-size': '10',
                'font-weight': 'bold',
                'fill': '#000000'
            })
            text.text = str(step_num)

    # Add start marker (larger green circle)
    if tour:
        start_station = tour[0]
        if start_station in mapping:
            x, y = mapping[start_station]['x'], mapping[start_station]['y']
            start_marker = ET.SubElement(tour_group, '{http://www.w3.org/2000/svg}circle', {
                'cx': str(x),
                'cy': str(y),
                'r': '12',
                'fill': 'none',
                'stroke': '#00FF00',
                'stroke-width': '3'
            })

    # Add legend
    legend_group = ET.SubElement(root, '{http://www.w3.org/2000/svg}g', {
        'id': 'tour-legend',
        'transform': 'translate(20, 930)'
    })

    # Legend background
    legend_bg = ET.SubElement(legend_group, '{http://www.w3.org/2000/svg}rect', {
        'x': '0',
        'y': '0',
        'width': '250',
        'height': '70',
        'fill': '#FFFFFF',
        'stroke': '#000000',
        'stroke-width': '1',
        'opacity': '0.9'
    })

    # Legend title
    legend_title = ET.SubElement(legend_group, '{http://www.w3.org/2000/svg}text', {
        'x': '10',
        'y': '20',
        'font-family': 'Arial',
        'font-size': '14',
        'font-weight': 'bold',
        'fill': '#000000'
    })
    legend_title.text = tour_name

    # Legend content
    legend_text = ET.SubElement(legend_group, '{http://www.w3.org/2000/svg}text', {
        'x': '10',
        'y': '40',
        'font-family': 'Arial',
        'font-size': '11',
        'fill': '#000000'
    })
    legend_text.text = f"Stations: {len(tour)}"

    # Tour path indicator
    legend_line = ET.SubElement(legend_group, '{http://www.w3.org/2000/svg}line', {
        'x1': '10',
        'y1': '55',
        'x2': '50',
        'y2': '55',
        'stroke': tour_color,
        'stroke-width': tour_width,
        'marker-end': 'url(#tour-arrow)'
    })

    legend_line_text = ET.SubElement(legend_group, '{http://www.w3.org/2000/svg}text', {
        'x': '60',
        'y': '59',
        'font-family': 'Arial',
        'font-size': '10',
        'fill': '#000000'
    })
    legend_line_text.text = "Tour path & direction"

    # Write output
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"✓ Rendered tour to {output_path}")
    print(f"  - {len(tour)} stations")
    print(f"  - {len([s for s in tour if s in mapping])} mapped positions")


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Render TSP tour onto SVG map')
    parser.add_argument('tour_file', help='JSON file with tour data (list of station IDs)')
    parser.add_argument('--output', '-o', help='Output SVG path', default=None)
    parser.add_argument('--name', '-n', help='Tour name', default='TSP Tour')
    parser.add_argument('--color', '-c', help='Tour color (hex)', default='#FF0000')
    parser.add_argument('--width', '-w', help='Line width', default='3')
    parser.add_argument('--no-numbers', action='store_true', help='Hide step numbers')

    args = parser.parse_args()

    # Paths
    svg_input = Path('data/processed/sg_mrt_lrt_built_only.svg')
    mapping_file = Path('data/processed/svg_name_map.csv')
    tour_file = Path(args.tour_file)

    # Load tour
    print(f"Loading tour from {tour_file}...")
    with open(tour_file, 'r') as f:
        data = json.load(f)
        if isinstance(data, dict):
            tour = data.get('tour', data.get('stations', []))
        else:
            tour = data

    if not tour:
        print("Error: No tour data found in file")
        sys.exit(1)

    print(f"Tour has {len(tour)} stations")

    # Load mapping
    print(f"Loading station mapping from {mapping_file}...")
    mapping = load_mapping(mapping_file)
    print(f"Loaded {len(mapping)} station positions")

    # Output path
    if args.output:
        output_path = Path(args.output)
    else:
        tour_name_slug = args.name.lower().replace(' ', '_')
        output_path = Path(f'data/processed/maps/{tour_name_slug}.svg')

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Render
    print(f"\nRendering tour '{args.name}'...")
    render_tour_on_svg(
        svg_input,
        mapping,
        tour,
        output_path,
        tour_name=args.name,
        tour_color=args.color,
        tour_width=args.width,
        show_step_numbers=not args.no_numbers
    )

    print(f"\n✓ Complete! View the result at: {output_path}")


if __name__ == '__main__':
    main()
