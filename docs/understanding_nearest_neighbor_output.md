# Understanding the Output from `nearest_neighbor_tsp()`

## Quick Summary

When you run:
```python
nn_path = nearest_neighbor_tsp(G, start_station='BP10')
```

You get a **tuple** containing two elements:
1. **`nn_path[0]`** - The tour (list of station IDs)
2. **`nn_path[1]`** - The total cost (float, in minutes)

## Detailed Breakdown

### Return Value Structure

```python
nn_path = nearest_neighbor_tsp(G, start_station='BP10')
# nn_path is a tuple: (tour, total_cost)
```

| Element | Type | Description | Example Value |
|---------|------|-------------|---------------|
| `nn_path[0]` | `list[str]` | Ordered list of station IDs representing the tour | `['BP10', 'BP11', 'BP12', ..., 'TE1']` |
| `nn_path[1]` | `float` | Total travel time in minutes for the complete tour | `749.77` |

### Element 1: The Tour (`nn_path[0]`)

The **tour** is a list of 214 station IDs in the order they should be visited.

**Key Properties:**
- **Length:** 214 stations (all stations in Singapore's MRT/LRT network)
- **Format:** List of station codes (e.g., `'BP10'`, `'NS1'`, `'EW12'`)
- **Order:** Starts with your specified starting station (`'BP10'` = Fajar)
- **Completeness:** Visits every station exactly once
- **Cycle:** Implicitly returns to the starting station (forms a complete cycle)

**Example output:**
```python
nn_path[0][:10]  # First 10 stations
# ['BP10', 'BP11', 'BP12', 'BP13', 'BP9', 'BP8', 'BP7', 'BP6', 'BP5', 'BP4']

nn_path[0][-10:]  # Last 10 stations
# ['NE3', 'NE4', 'NE5', 'EW3', 'EW2', 'EW1', 'CG2', 'NS8', 'NS7', 'TE1']
```

**How to use it:**
```python
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')

# Access individual stations
first_station = tour[0]  # 'BP10'
second_station = tour[1]  # 'BP11'
last_station = tour[-1]   # 'TE1'

# Iterate through the tour
for i, station_id in enumerate(tour):
    station_name = G.nodes[station_id]['name']
    print(f"Stop {i+1}: {station_id} - {station_name}")
```

### Element 2: The Total Cost (`nn_path[1]`)

The **cost** represents the total travel time for the complete tour.

**Key Properties:**
- **Units:** Minutes
- **Type:** Float (decimal number)
- **Calculation:** Sum of shortest-path travel times between consecutive stations in the tour
- **Includes:** The implicit return journey from the last station back to the starting station

**Example output:**
```python
nn_path[1]
# 749.77  (minutes)
```

**How to interpret it:**
```python
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')

# Total time in different units
print(f"Total time: {cost:.2f} minutes")           # 749.77 minutes
print(f"Total time: {cost/60:.2f} hours")          # 12.50 hours
print(f"Average per station: {cost/len(tour):.2f} min")  # 3.50 minutes

# This is the total time to:
# BP10 → BP11 → BP12 → ... → TE1 → BP10 (back to start)
```

## What the Algorithm Does

The **Nearest Neighbor Heuristic** is a greedy algorithm that constructs the tour as follows:

1. **Start** at station `'BP10'` (Fajar)
2. **Repeat** until all stations are visited:
   - Look at all unvisited stations
   - Find the nearest one (shortest travel time from current station)
   - Move to that station
   - Mark it as visited
3. **Return** to the starting station (implicitly, to complete the cycle)

**Time Complexity:** O(n²) where n = 214 stations  
**Execution Time:** ~0.11 seconds

## Important Concepts

### Metric Closure

The algorithm operates on the **metric closure** of the graph, not the raw network graph:

- **Raw Graph:** 214 nodes, 277 edges (only direct train/walking connections)
- **Metric Closure:** 214 nodes, 22,791 edges (complete graph with shortest-path distances)

**Why?** The metro network is not a complete graph. Some station pairs have no direct connection, so we use the shortest path between any two stations. This ensures:
- Every station can reach every other station
- The TSP solution is valid (Hamiltonian cycle exists)
- Travel times are realistic (based on actual shortest paths)

### Tour Validation

The returned tour is automatically validated to ensure:
- ✓ Visits exactly 214 stations (complete)
- ✓ No duplicate stations
- ✓ All stations exist in the graph
- ✓ All consecutive station pairs are connected (in the metric closure)
- ✓ Forms a valid Hamiltonian cycle

## Practical Examples

### Example 1: Unpacking the Result

```python
# Most common usage - unpack immediately
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')

print(f"Found a tour visiting {len(tour)} stations")
print(f"Total travel time: {cost:.2f} minutes")
```

### Example 2: Accessing Specific Stations

```python
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')

# Get station names for first 5 stops
print("First 5 stops:")
for i in range(5):
    station_id = tour[i]
    station_name = G.nodes[station_id]['name']
    line_code = G.nodes[station_id]['line_code']
    print(f"  {i+1}. {station_id} ({line_code} Line) - {station_name}")

# Output:
#   1. BP10 (BP Line) - Fajar
#   2. BP11 (BP Line) - Segar
#   3. BP12 (BP Line) - Jelapang
#   4. BP13 (BP Line) - Senja
#   5. BP9 (BP Line) - Pending
```

### Example 3: Calculating Segment Costs

```python
from src.utils import calculate_tour_cost

tour, total_cost = nearest_neighbor_tsp(G, start_station='BP10')

# Cost of first 10 stations
partial_tour = tour[:10]
partial_cost = calculate_tour_cost(partial_tour + [partial_tour[0]], G)
print(f"First 10 stations cost: {partial_cost:.2f} minutes")
```

### Example 4: Comparing Different Starting Points

```python
# Try different starting stations
starts = ['BP10', 'NS1', 'EW1', 'NE1', 'CC1']

for start in starts:
    tour, cost = nearest_neighbor_tsp(G, start_station=start)
    print(f"Starting from {start}: {cost:.2f} minutes")

# The starting point affects the solution quality!
# That's why nearest_neighbor_multi_start() exists
```

## Common Misconceptions

❌ **"The tour is a path in the graph"**  
✓ The tour is an **ordered sequence of stations**. The actual paths between consecutive stations are the shortest paths in the network (which may involve multiple hops).

❌ **"The cost is the number of stations"**  
✓ The cost is the **total travel time in minutes**, not a count of stations.

❌ **"The tour doesn't return to start"**  
✓ The tour **implicitly returns** to the starting station. The cost includes the return journey (`tour[-1]` → `tour[0]`).

❌ **"I can improve this manually by reordering stations"**  
✓ While possible, use **2-opt local search** (`improve_tour_2opt`) instead - it systematically finds improvements.

## Next Steps

### Improve the Solution

The Nearest Neighbor heuristic is a **constructive algorithm** that builds a reasonable (but not optimal) initial solution. You can improve it with:

```python
from src.solvers import improve_tour_2opt, simulated_annealing_tsp

# Method 1: Local search (2-opt)
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')
improved_tour, old_cost, new_cost = improve_tour_2opt(tour, G)
print(f"Improved from {old_cost:.2f} to {new_cost:.2f} minutes")

# Method 2: Metaheuristic (Simulated Annealing)
sa_tour, sa_cost, history = simulated_annealing_tsp(
    G, 
    initial_tour=tour,  # Start from NN solution
    max_iterations=10000
)
print(f"SA found: {sa_cost:.2f} minutes")
```

### Try Multiple Starting Points

```python
from src.solvers import nearest_neighbor_multi_start

# Try 10 different starting points and keep the best
best_tour, best_cost, best_start = nearest_neighbor_multi_start(G, num_starts=10)
print(f"Best starting station: {best_start}")
print(f"Best cost: {best_cost:.2f} minutes")
```

### Visualize the Tour

```python
import matplotlib.pyplot as plt

tour, cost = nearest_neighbor_tsp(G, start_station='BP10')

# Extract coordinates
lats = [G.nodes[station]['latitude'] for station in tour]
lons = [G.nodes[station]['longitude'] for station in tour]

# Plot the tour
plt.figure(figsize=(10, 10))
plt.plot(lons, lats, 'b-', alpha=0.3, linewidth=0.5)
plt.plot(lons, lats, 'ro', markersize=3)
plt.title(f"Nearest Neighbor Tour (Cost: {cost:.2f} min)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()
```

## References

- **Source Code:** `src/solvers/nearest_neighbor.py`
- **Algorithm Description:** Lines 29-63 (docstring)
- **Metric Closure:** `src/utils/metric.py`
- **Tour Utilities:** `src/utils/tour.py`
- **Demo Notebook:** `notebooks/epic_3_tsp_solvers_demo.ipynb`

## Quick Reference Card

```python
# Basic usage
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')

# What you get:
tour   # list[str]: ['BP10', 'BP11', ..., 'TE1']  - 214 stations
cost   # float: 749.77  - Total minutes

# Common operations:
len(tour)              # 214 (number of stations)
tour[0]                # 'BP10' (starting station)
tour[-1]               # 'TE1' (last station before returning to start)
cost / len(tour)       # 3.50 (average minutes per station)
cost / 60              # 12.50 (total hours)

# Get station info:
G.nodes[tour[0]]['name']       # 'Fajar'
G.nodes[tour[0]]['line_code']  # 'BP'
G.nodes[tour[0]]['latitude']   # 1.38455
```
