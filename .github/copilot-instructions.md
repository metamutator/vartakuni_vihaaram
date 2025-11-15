# Copilot Instructions for Vartakuni Vihāram

## Project Overview
TSP solver for metro networks, generating optimal routes visiting all stations. Currently focused on Singapore's MRT/LRT network (214 stations, 277 connections). Goal: Calculate shortest cycle visiting every station exactly once.

## Architecture & Key Concepts

### Graph Model Pattern
**Multi-node interchange stations** - Critical design decision:
- Interchange stations like "Dhoby Ghaut" are modeled as **separate nodes per line**: `NS24`, `NE6`, `CC1`
- Connected by `walk_transfer` edges (transfer times: 2-5 min)
- Ensures TSP visits each platform (more realistic for transit enthusiasts)
- Implemented in: `src/graph/builder.py::MetroGraphBuilder.load_stations()`

### Data Flow
```
data/raw/*.csv → MetroGraphBuilder → NetworkX Graph → TSP Solvers → Visualization
```

**Critical files:**
- `data/raw/stations.csv` - 214 station entries with line codes, coordinates
- `data/raw/connections.csv` - 554 connections (train + walking)
- `data/raw/lines.csv` - 15 lines with official colors

### Connection Types (see `connections.csv`)
- `train` - Rail connections between sequential stations (weight = travel time)
- `walk_transfer` - Platform transfers within interchange stations
- `walk_between_stations` - Walking routes between nearby stations (<10 min)

## Development Workflow

### Building the Graph
```python
from src.graph.builder import build_singapore_metro_graph
from pathlib import Path

graph = build_singapore_metro_graph(Path('data/raw'))
# Auto-validates connectivity, prints stats
```

### Running Tests
```bash
pytest                           # All tests
pytest tests/test_graph_builder.py -v  # Specific module
pytest --cov=src --cov-report=html     # With coverage
```

### Data Validation Pipeline (before graph building)
```python
from src.graph.validator import validate_metro_data

report = validate_metro_data(Path('data/raw'))
report.print_report()  # Check for errors before proceeding
```

### Utility Scripts (executable from project root)
- `scripts/validate_stations.py` - Check station data quality
- `scripts/validate_connections.py` - Verify connection integrity
- `scripts/fix_disconnected_components.py` - Diagnose connectivity issues

## Project-Specific Conventions

### Data Files - DO NOT modify `data/raw/` directly
All raw data has extensive source documentation (e.g., `CONNECTIONS_SOURCE.md`, `WALKING_CONNECTIONS_SOURCE.md`). If data needs correction:
1. Document in corresponding `*_SOURCE.md` file
2. Update generation script in `scripts/`
3. Regenerate CSV from script

**Travel time estimates** - Currently computed, not official LTA schedules. See `data/raw/CONNECTIONS_SOURCE.md` for methodology.

### Testing Fixtures Pattern
Tests use CSV fixtures via `tmp_path`:
```python
@pytest.fixture
def sample_stations_csv(self, tmp_path):
    stations_file = tmp_path / "stations.csv"
    # Write test data...
    return stations_file
```
See `tests/test_graph_builder.py` for examples.

### User Story Status Tracking
When completing a user story:
1. **In `PROJECT_SPEC.md`:** Check all acceptance criteria boxes `- [x]`, add status line with PR/commit reference
2. **Regenerate artifacts:** Run `python scripts/generate_github_issues.py` to update `issues.json` and `issues.md`
3. **Close GitHub issue:** Link to PR/commit that completed the work
4. **Commit message format:** `"Implements US-XXX: [Story title]"` or `"Fixes US-XXX: [Story title]"`

**Status line format in PROJECT_SPEC.md:**
```markdown
**Status:** ✅ Completed. Fixed in PR #33 (commit 1641ce9). Brief summary of implementation.
```

### Module Structure
- `src/graph/` - NetworkX graph construction and validation
- `src/solvers/` - TSP algorithms (not yet implemented)
- `src/visualization/` - Plotting (planned)
- `scripts/` - One-off utilities for data generation/fixing

## Current Status (Phase 1)
✅ **Epic 1: Data Foundation** - Complete (US-101 through US-108)
✅ **Epic 2: Graph Infrastructure** - US-201 complete, US-202 in progress
⏳ **Epic 3: TSP Solvers** - Not started (Nearest Neighbor, 2-opt, Simulated Annealing)
⏳ **Epic 4: Visualization** - Not started (Plotly/Folium/Observable.js)

See `PROJECT_SPEC.md` for full user stories and acceptance criteria.

## Dependencies & Environment

**Python:** 3.11+ (3.14 in use; numba disabled due to incompatibility)
**Key libraries:** NetworkX (graph), pytest (testing), pandas/numpy (data processing)

**Numba note:** Optional JIT compiler for performance. If TSP computation becomes slow (>2 min), see `docs/performance_optimization.md` for enabling instructions (requires Python ≤3.13 downgrade).

## Common Tasks

### Adding a new TSP algorithm
1. Create module in `src/solvers/` (e.g., `nearest_neighbor.py`)
2. Accept `nx.Graph` and `start_station_id` as inputs
3. Return `(tour: List[str], total_time: float)`
4. Add tests in `tests/test_solvers/`
5. Update `src/solvers/__init__.py` for imports

### Fixing graph connectivity issues
```bash
python scripts/fix_disconnected_components.py  # Diagnose
# Review output, identify missing connections
# Update connections.csv or walking connections script
```

### Working with notebooks
Notebooks in `notebooks/` for exploration/demos. Best practice: Export stable code to `src/` modules. See `notebooks/graph_infrastructure_demo.ipynb` for graph API examples.

## Important Context

**Project goals:**
- Educational (demonstrate NP-hard problem solving)
- For metro enthusiasts (theoretical "complete traversal" routes)
- Static site deployment via Quarto → GitHub Pages

**Design decisions documented in:**
- Multi-node station model: `PROJECT_SPEC.md` Section 3.4
- Pre-computation vs. real-time: `PROJECT_SPEC.md` Section 3.4
- Data limitations: `data/raw/CONNECTIONS_SOURCE.md`

When implementing features, reference user stories in `PROJECT_SPEC.md` (e.g., "US-301: Nearest Neighbor Heuristic") for acceptance criteria.

## Development Workflows

### Environment Setup
```bash
# Currently using Python 3.14 with conda environment 'TSP-izer'
conda activate TSP-izer
pip install -r requirements.txt
```

**Important:** Numba (JIT compiler) is **intentionally disabled** due to Python 3.14 incompatibility. Only enable if TSP computation >2 minutes (see `docs/performance_optimization.md` for downgrade steps to Python 3.13).

### GitHub Issue Management

**Source of truth:** `PROJECT_SPEC.md` Section 5 contains all user stories with full acceptance criteria.

**Generated artifacts:** When user stories are updated, regenerate:
1. `scripts/github_issues/issues.json` - Machine-readable issue definitions
2. `scripts/github_issues/issues.md` - Human-readable issue descriptions  
3. `scripts/create_github_issues.sh` - GitHub CLI script to create issues

**Workflow for updating completed user stories:**

```bash
# 1. Mark user story complete in PROJECT_SPEC.md
# Find the story (e.g., US-107) and update acceptance criteria checkboxes:
# - [x] All acceptance criteria checked
# Add status line: **Status:** ✅ Completed. [Brief summary]

# 2. Regenerate issue files
python scripts/generate_github_issues.py

# 3. Update GitHub issue (manual step via web UI or CLI)
# Close the issue with reference to PR/commit that completed it
gh issue close <issue-number> --comment "Completed in PR #X (commit abc123). [Summary of what was done]"
```

**Example from codebase:** See US-106 and US-107 in `scripts/github_issues/issues.md` - both show completed status with commit references.

**Critical:** The `generate_github_issues.py` script parses `PROJECT_SPEC.md` and extracts:
- User story ID (e.g., US-201)
- Acceptance criteria (checkboxes)
- Story points, priority, labels
- Epic assignment

When implementing a user story, always reference it by ID in commit messages: `"Implements US-201: Graph Builder Module"`

### Testing Strategy
```bash
# Run tests with pytest
pytest                              # All tests
pytest --cov=src --cov-report=html  # With coverage (target >80%)
pytest -m "not slow"                # Skip integration tests
```

Test structure mirrors `src/` layout. Use `@pytest.mark.slow` for expensive tests.

## Key Files to Reference

- `PROJECT_SPEC.md`: Authoritative source - 911 lines covering all requirements, data schema, user stories (Section 5)
- `docs/performance_optimization.md`: When/how to enable Numba, benchmarking expectations
- `data/README.md`: Data schema details
- `requirements.txt`: All dependencies (note Numba commented out)
- `scripts/generate_github_issues.py`: Parses PROJECT_SPEC.md → generates issues.json/issues.md/create_github_issues.sh
- `scripts/github_issues/issues.md`: Human-readable list of all user stories with current status
- `scripts/github_issues/issues.json`: Machine-readable issue definitions for automation
