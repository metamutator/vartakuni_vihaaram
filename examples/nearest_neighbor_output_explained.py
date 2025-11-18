"""
Example: Understanding nearest_neighbor_tsp() output
=====================================================

This script demonstrates what you get when you run:
    nn_path = nearest_neighbor_tsp(G, start_station='BP10')

For detailed explanation, see: docs/understanding_nearest_neighbor_output.md
For interactive exploration, see: notebooks/understanding_nearest_neighbor_output.ipynb
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import load_default_graph
from src.solvers import nearest_neighbor_tsp
import time


def main():
    print("=" * 80)
    print("Understanding nearest_neighbor_tsp() Output")
    print("=" * 80)
    print()
    
    # Load the Singapore MRT/LRT network
    print("Loading Singapore MRT/LRT network...")
    G = load_default_graph()
    print(f"✓ Loaded {G.number_of_nodes()} stations, {G.number_of_edges()} connections")
    print()
    
    # Run nearest neighbor from BP10
    print("Running: nn_path = nearest_neighbor_tsp(G, start_station='BP10')")
    print()
    
    start_time = time.time()
    nn_path = nearest_neighbor_tsp(G, start_station='BP10')
    elapsed = time.time() - start_time
    
    print(f"✓ Completed in {elapsed:.4f} seconds")
    print()
    
    # Explain the output structure
    print("-" * 80)
    print("WHAT YOU GET:")
    print("-" * 80)
    print()
    
    print(f"nn_path is a {type(nn_path).__name__} with {len(nn_path)} elements:")
    print()
    
    # Element 0: The tour
    print("1️⃣  Element 0 (nn_path[0]) - THE TOUR")
    print(f"   Type: {type(nn_path[0]).__name__}")
    print(f"   Contents: List of {len(nn_path[0])} station IDs")
    print(f"   First station: {nn_path[0][0]}")
    print(f"   Last station: {nn_path[0][-1]}")
    print(f"   First 5: {nn_path[0][:5]}")
    print(f"   Last 5: {nn_path[0][-5:]}")
    print()
    
    # Element 1: The cost
    print("2️⃣  Element 1 (nn_path[1]) - THE COST")
    print(f"   Type: {type(nn_path[1]).__name__}")
    print(f"   Value: {nn_path[1]:.2f} minutes")
    print(f"   Value: {nn_path[1]/60:.2f} hours")
    print(f"   Average: {nn_path[1]/len(nn_path[0]):.2f} minutes per station")
    print()
    
    print("-" * 80)
    print("HOW TO USE IT:")
    print("-" * 80)
    print()
    
    print("✅ RECOMMENDED: Unpack immediately")
    print("   tour, cost = nearest_neighbor_tsp(G, start_station='BP10')")
    print()
    
    # Demonstrate unpacking
    tour, cost = nn_path  # or run again
    
    print(f"Now you have:")
    print(f"  • tour: list of {len(tour)} stations")
    print(f"  • cost: {cost:.2f} minutes")
    print()
    
    print("-" * 80)
    print("TOUR DETAILS:")
    print("-" * 80)
    print()
    
    print(f"Starting station: {tour[0]} ({G.nodes[tour[0]]['name']})")
    print()
    
    print("First 10 stations in tour:")
    for i in range(min(10, len(tour))):
        station_id = tour[i]
        station_name = G.nodes[station_id]['name']
        line_code = G.nodes[station_id]['line_code']
        print(f"  {i+1:3d}. {station_id:5s} ({line_code:2s} Line) - {station_name}")
    
    print()
    print("... (visits all 214 stations) ...")
    print()
    
    print("Last 5 stations before returning to start:")
    for i in range(len(tour)-5, len(tour)):
        station_id = tour[i]
        station_name = G.nodes[station_id]['name']
        line_code = G.nodes[station_id]['line_code']
        print(f"  {i+1:3d}. {station_id:5s} ({line_code:2s} Line) - {station_name}")
    
    print()
    print(f"Then returns to: {tour[0]} ({G.nodes[tour[0]]['name']})")
    print()
    
    print("-" * 80)
    print("KEY POINTS:")
    print("-" * 80)
    print()
    
    print("✓ The tour is a LIST of station IDs (strings)")
    print("✓ The cost is a FLOAT representing total minutes")
    print("✓ The tour visits ALL 214 stations exactly once")
    print("✓ The tour implicitly returns to the starting station")
    print("✓ The cost includes the return journey")
    print("✓ Uses shortest paths between stations (metric closure)")
    print()
    
    print("-" * 80)
    print("NEXT STEPS:")
    print("-" * 80)
    print()
    
    print("📚 Read: docs/understanding_nearest_neighbor_output.md")
    print("🔬 Explore: notebooks/understanding_nearest_neighbor_output.ipynb")
    print("🚀 Try: Different starting stations to compare results")
    print("⚡ Improve: Use improve_tour_2opt() to optimize further")
    print()


if __name__ == "__main__":
    main()
