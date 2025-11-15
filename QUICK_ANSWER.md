# Quick Answer: Understanding `nn_path = nearest_neighbor_tsp(G, start_station='BP10')`

## TL;DR

When you run:
```python
nn_path = nearest_neighbor_tsp(G, start_station='BP10')
```

You get a **tuple with 2 elements**:

```python
nn_path[0]  # List of 214 station IDs (the tour)
nn_path[1]  # Float: total travel time in minutes (the cost)
```

**Best practice:** Unpack immediately:
```python
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')
```

## What You Get

### 1. The Tour (`nn_path[0]`)

```python
type(nn_path[0])  # <class 'list'>
len(nn_path[0])   # 214 (all stations)

# Example values:
nn_path[0][:5]    # ['BP10', 'BP11', 'BP12', 'BP13', 'BP9']
nn_path[0][-5:]   # ['EW1', 'CG2', 'NS8', 'NS7', 'TE1']
```

**What it represents:**
- Ordered list of station IDs to visit
- Starts at 'BP10' (Fajar station)
- Visits all 214 stations exactly once
- Implicitly returns to start (forms a cycle)

### 2. The Cost (`nn_path[1]`)

```python
type(nn_path[1])  # <class 'float'>
nn_path[1]        # ~737-750 minutes (varies slightly)

# Convert to hours:
nn_path[1] / 60   # ~12.3 hours

# Average per station:
nn_path[1] / 214  # ~3.4 minutes
```

**What it represents:**
- Total travel time for the complete tour
- Measured in minutes
- Includes the return journey to starting station
- Based on shortest paths between stations

## Quick Examples

### Unpacking and Using

```python
# Run the algorithm
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')

# Access stations
first_station = tour[0]   # 'BP10'
last_station = tour[-1]   # 'TE1'

# Get station names
print(G.nodes[first_station]['name'])  # 'Fajar'

# Print first 5 stops with names
for i in range(5):
    station_id = tour[i]
    name = G.nodes[station_id]['name']
    print(f"{i+1}. {station_id} - {name}")

# Output:
# 1. BP10 - Fajar
# 2. BP11 - Segar
# 3. BP12 - Jelapang
# 4. BP13 - Senja
# 5. BP9 - Bangkit
```

### Comparing Starting Points

```python
# Different starting points give different results
starts = ['BP10', 'NS1', 'EW1', 'NE1', 'CC1']

for start in starts:
    tour, cost = nearest_neighbor_tsp(G, start_station=start)
    print(f"{start}: {cost:.2f} minutes")
```

### Improving the Solution

```python
from src.solvers import improve_tour_2opt

# Get initial solution
tour, cost = nearest_neighbor_tsp(G, start_station='BP10')
print(f"Initial: {cost:.2f} minutes")

# Improve with 2-opt
improved_tour, old_cost, new_cost = improve_tour_2opt(tour, G)
print(f"Improved: {new_cost:.2f} minutes")
print(f"Savings: {old_cost - new_cost:.2f} minutes")
```

## Important Concepts

### Metric Closure
The algorithm operates on the **metric closure** of the network:
- Not just direct connections
- Uses shortest paths between any two stations
- Ensures every station can reach every other station
- This is why the tour is valid even though the metro network isn't fully connected

### Why Starting Point Matters
Nearest Neighbor is a **greedy algorithm**:
- Makes the locally optimal choice at each step
- Early decisions affect later choices
- Different starting points → different tours → different costs
- Use `nearest_neighbor_multi_start()` to try multiple starting points

## Resources

- **📚 Detailed Guide:** `docs/understanding_nearest_neighbor_output.md`
- **💻 Interactive Demo:** `notebooks/understanding_nearest_neighbor_output.ipynb`
- **🚀 Runnable Script:** `examples/nearest_neighbor_output_explained.py`

Run the script to see live output:
```bash
python examples/nearest_neighbor_output_explained.py
```

## Common Questions

**Q: Is the tour a path in the graph?**
A: No, it's a sequence of station IDs. The actual paths between consecutive stations are the shortest paths in the network.

**Q: Does it return to the starting station?**
A: Yes, implicitly. The cost includes the return journey from the last station back to the first.

**Q: Can I improve this solution?**
A: Yes! Use `improve_tour_2opt()`, `simulated_annealing_tsp()`, or `genetic_algorithm_tsp()`.

**Q: Why does the cost vary slightly between runs?**
A: With the same starting station, the result is deterministic. Variations only occur with different starting stations or when using stochastic algorithms (SA, GA).
