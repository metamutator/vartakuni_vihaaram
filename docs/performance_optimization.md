# Performance Optimization Guide

## Current Setup
- **Python Version**: 3.14.0
- **Environment**: `TSP-izer` (conda)

## Performance Considerations

### Numba JIT Compilation (Optional)

**Current Status**: Not installed (Python 3.14 incompatibility)

**What is Numba?**
- Just-in-time compiler for Python numerical code
- Can accelerate loops and NumPy operations 10-100x
- Particularly useful for iterative algorithms like TSP solvers

**When to Enable Numba:**
- TSP computation time exceeds acceptable limits (>2 minutes per solution)
- Need to process multiple starting points in batch
- Testing with larger networks (>200 stations)

**How to Enable Numba:**

1. **Downgrade Python to 3.13:**
   ```bash
   # Remove current environment
   conda deactivate
   conda remove -n TSP-izer --all -y
   
   # Create new environment with Python 3.13
   conda create -n TSP-izer python=3.13 -y
   conda activate TSP-izer
   ```

2. **Uncomment numba in requirements.txt:**
   ```bash
   # Edit requirements.txt and uncomment:
   # numba>=0.57.0
   ```

3. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add `@jit` decorators to performance-critical functions:**
   ```python
   from numba import jit
   
   @jit(nopython=True)
   def compute_tour_length(tour, distance_matrix):
       total = 0
       for i in range(len(tour) - 1):
           total += distance_matrix[tour[i], tour[i+1]]
       return total
   ```

## Other Optimization Strategies

### Algorithm Selection
- **Nearest Neighbor**: Fast, ~O(n²), good starting heuristic
- **2-opt**: Medium speed, iterative improvement
- **Simulated Annealing**: Slower but better solutions, configurable runtime
- **Genetic Algorithm**: Parallelizable, good for large problems

### Pre-computation
- Calculate all routes offline and store in `data/solutions/`
- Embed pre-computed results in static website
- Update only when network topology changes

### Profiling
```bash
# Profile Python code
python -m cProfile -o profile.stats scripts/solve_tsp.py
python -m pstats profile.stats

# Or use line_profiler
pip install line_profiler
kernprof -l -v scripts/solve_tsp.py
```

### Caching
- Cache distance matrices after first computation
- Store intermediate algorithm states
- Use `@lru_cache` for repeated calculations

## Benchmarking

Expected computation times (without Numba, 189 stations):
- **Nearest Neighbor**: < 1 second
- **2-opt improvement**: 5-30 seconds
- **Simulated Annealing**: 30 seconds - 5 minutes (configurable)
- **Full pre-computation (all 189 starting points)**: 1-6 hours

If these times are unacceptable, enable Numba or explore algorithm optimizations.

## Notes
- Current setup prioritizes compatibility over raw speed
- For Singapore MRT (189 stations), Numba likely not necessary
- Consider Numba if expanding to larger networks or real-time computation
