#!/usr/bin/env python3
"""Generate a sample TSP tour using the Nearest Neighbor algorithm.

This creates a tour JSON file that can be rendered onto the SVG map.
"""

from pathlib import Path
import json
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.builder import build_singapore_metro_graph
from src.solvers.nearest_neighbor import nearest_neighbor_tsp


def main():
    print("=" * 70)
    print("Generating Sample TSP Tour")
    print("=" * 70)

    # Build graph
    print("\n1. Building metro graph...")
    data_dir = Path('data/raw')
    graph = build_singapore_metro_graph(data_dir)

    print(f"   ✓ Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    # Generate tour using Nearest Neighbor
    print("\n2. Running Nearest Neighbor algorithm...")
    print("   (This may take a few moments...)")

    # Start from a well-known station
    start_station = "NS1"  # Jurong East

    tour, cost = nearest_neighbor_tsp(graph, start_station=start_station, validate_result=True)

    print(f"   ✓ Tour generated:")
    print(f"     - Stations: {len(tour)}")
    print(f"     - Total cost: {cost:.2f} minutes")
    print(f"     - Start/End: {start_station}")

    # Save to JSON
    output_dir = Path('data/processed/tours')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'sample_nn_tour.json'

    tour_data = {
        'tour': tour,
        'cost': cost,
        'algorithm': 'Nearest Neighbor',
        'start_station': start_station,
        'num_stations': len(tour)
    }

    print(f"\n3. Saving tour to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(tour_data, f, indent=2)

    print(f"   ✓ Saved!")

    # Print sample of tour
    print(f"\n4. Tour preview (first 20 stations):")
    for i, station_id in enumerate(tour[:20], 1):
        print(f"   {i:3d}. {station_id}")
    if len(tour) > 20:
        print(f"   ... and {len(tour) - 20} more")

    print("\n" + "=" * 70)
    print("✓ Sample tour generated successfully!")
    print("=" * 70)
    print(f"\nNext step: Render the tour onto the SVG map:")
    print(f"  python scripts/render_tour_to_svg.py {output_file}")


if __name__ == '__main__':
    main()
