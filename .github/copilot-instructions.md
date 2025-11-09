# Copilot Instructions: Vartakuni Vihāram (Metro TSP Solver)

## Project Overview

This is a **Traveling Salesman Problem (TSP) solver for metro networks** that calculates optimal routes visiting all stations exactly once. The primary target is Singapore's MRT/LRT network (~189 stations). This is an **early-stage project** - most implementation modules are empty stubs.

**Core Architecture:** CSV data → NetworkX graph → TSP solvers → Interactive visualization → Quarto static site → GitHub Pages

## Critical Design Patterns

### Multi-Platform Station Modeling
Multi-line interchange stations are **modeled as separate nodes per platform** (e.g., Dhoby Ghaut becomes `DG_NSL`, `DG_CCL`, `DG_NEL`). This is essential for TSP realism:
- Each platform node must be visited once
- Walking edges connect platforms (transfer times)
- When implementing graph builder in `src/graph/`, ensure this multi-node pattern
- See `PROJECT_SPEC.md` Section 3.4 Decision 3 for rationale

### Data Schema (Critical for Graph Construction)
Three CSV files in `data/raw/`:
- `stations.csv`: `station_id, station_name, line_code, latitude, longitude, operational_status`
  - Example: `NS1_EWL,Jurong East,EWL,1.3330,103.7421,active`
- `connections.csv`: `connection_id, from_station_id, to_station_id, connection_type, travel_time_minutes, distance_meters`
  - `connection_type`: `train`, `walk_transfer`, `walk_between_stations`
- `lines.csv`: `line_code, line_name, color_hex, line_type`

**Edge weights are travel times in minutes** (not distance). This affects all algorithm implementations.

## Development Workflows

### Environment Setup
```bash
# Currently using Python 3.14 with conda environment 'TSP-izer'
conda activate TSP-izer
pip install -r requirements.txt
```

**Important:** Numba (JIT compiler) is **intentionally disabled** due to Python 3.14 incompatibility. Only enable if TSP computation >2 minutes (see `docs/performance_optimization.md` for downgrade steps to Python 3.13).

### Testing Strategy
```bash
# Run tests with pytest
pytest                              # All tests
pytest --cov=src --cov-report=html  # With coverage (target >80%)
pytest -m "not slow"                # Skip integration tests
```

Test structure mirrors `src/` layout. Use `@pytest.mark.slow` for expensive tests.

### Pre-computation Pipeline
Final deployment uses **pre-computed routes** for all 189 starting stations (static site constraint):
1. Run solver for each station: `scripts/solve_all_starts.py` (to be implemented)
2. Save results to `data/solutions/routes_all_starts.json`
3. Quarto site loads pre-computed data (no client-side computation)

Expected computation time: 1-6 hours total. See `PROJECT_SPEC.md` Section 3.4 Decision 1.

## Module Implementation Guidelines

### `src/graph/` - Network Graph Builder
**Status:** Empty stub. High priority (Epic 2 in `PROJECT_SPEC.md`).

Key functions to implement:
- `build_network(data_dir: Path) -> nx.Graph`: Parse CSVs, construct NetworkX graph
- `validate_topology(G: nx.Graph) -> bool`: Check connectivity, weight sanity
- Handle multi-platform splitting: one `stations.csv` row → multiple graph nodes

Output: NetworkX graph with:
- Nodes: `station_id` from CSVs (e.g., `NS1_EWL`)
- Edges: `travel_time_minutes` as weights
- Node attributes: `latitude`, `longitude`, `line_code`, `station_name`

### `src/solvers/` - TSP Algorithms
**Status:** Empty stub. Core feature (Epic 3).

Implement multiple algorithms (comparative analysis is goal):
1. **Nearest Neighbor** (baseline, ~O(n²), fast)
2. **2-opt Local Search** (iterative improvement)
3. **Simulated Annealing** (primary solver, configurable runtime)
4. **Genetic Algorithm** (optional, marked low priority)

Each solver signature:
```python
def solve_tsp(G: nx.Graph, start_station: str, **kwargs) -> List[str]:
    """Returns ordered list of station_ids forming complete tour."""
```

**Critical:** Tours must return to `start_station` (cycle constraint). Validate in tests that `tour[0] == tour[-1] == start_station`.

### `src/visualization/` - Map Generation
**Status:** Empty stub (Epic 4).

**Decision pending:** Visualization library choice between Plotly, Folium, Observable.js. See US-401 in `PROJECT_SPEC.md`. Start with **Plotly** for Quarto integration ease.

Functions to implement:
- `plot_network(G: nx.Graph)`: Show all stations/lines color-coded
- `plot_route(G: nx.Graph, tour: List[str])`: Overlay optimal route on network
- Use official MRT colors from `lines.csv` (`color_hex` column)

## Project-Specific Conventions

### File Naming
- Graph data: `data/processed/network_graph.json` (NetworkX serialized)
- Solutions: `data/solutions/routes_all_starts.json` (pre-computed TSP results)
- Test fixtures: `tests/fixtures/` for small sample networks

### Algorithm Comparison Format
When implementing US-305 (algorithm comparison), output JSON:
```json
{
  "start_station": "NS1",
  "algorithms": {
    "nearest_neighbor": {"tour_length_min": 450.2, "compute_time_sec": 0.05},
    "simulated_annealing": {"tour_length_min": 398.7, "compute_time_sec": 45.3}
  }
}
```

### Documentation Standards
- All user stories referenced by ID (e.g., "implements US-201")
- Algorithm implementations cite papers/sources in docstrings
- Performance notes in `docs/performance_optimization.md`

## External Dependencies & Integration

### Data Sources (Manual Collection Phase)
- **Singapore MRT data:** Land Transport Authority (LTA) schedules - manual entry
- **Transfer times:** Estimated from station maps or Google Maps walking directions
- See `PROJECT_SPEC.md` Section 3.5 for data collection methodology

### Quarto Deployment
Final output is a `.qmd` file in `quarto/` directory:
- Python code cells execute graph loading and visualization
- Renders to static HTML via GitHub Actions
- Deploys to GitHub Pages (US-503)

No FastAPI/backend - this is a **static site only** (MVP constraint).

## Current Project State

**Phase:** MVP Development (Phase 1 of 2)  
**Completed:** Project specification, directory structure, GitHub issue generation scripts  
**Next milestones:**
- M1 (Week 2): Data collection + graph builder
- M2 (Week 4): 2+ TSP algorithms working
- M3 (Week 6): Visualization prototype
- M4 (Week 8): Deployed to GitHub Pages

**Implementation priority:** `src/graph/` → `src/solvers/` → `src/visualization/` → Quarto integration

## Key Files to Reference

- `PROJECT_SPEC.md`: Authoritative source - 911 lines covering all requirements, data schema, user stories
- `docs/performance_optimization.md`: When/how to enable Numba, benchmarking expectations
- `data/README.md`: Data schema details
- `requirements.txt`: All dependencies (note Numba commented out)

## Common Pitfalls to Avoid

1. **Don't use distance as edge weights** - use travel time in minutes
2. **Don't model interchange stations as single nodes** - use multi-platform pattern
3. **Don't assume client-side computation** - pre-compute all routes for static deployment
4. **Don't install Numba on Python 3.14** - it will fail (requires ≤3.13)
5. **Test TSP tours are valid cycles** - must visit each node once and return to start
