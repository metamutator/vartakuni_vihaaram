# GitHub Issues for Metro TSP Solver

Copy each issue section below to create GitHub issues manually.

---

## US-101: Station Data Collection

**Labels:** data-collection, phase-1, epic-1, priority-high

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**  
I want to **compile a complete list of all Singapore MRT/LRT stations with metadata**  
So that **I can build an accurate network model**

**Acceptance Criteria**

- [ ] CSV file contains all 189+ active/under-construction stations
- [ ] Each station has: unique ID, name, line code(s), lat/long, operational status
- [ ] Multi-line stations have separate entries per platform
- [ ] Data validated against official LTA sources

**Story Points:** 5  
**Priority:** High


---

## US-102: Inter-Station Travel Time Data

**Labels:** data-collection, phase-1, epic-1, priority-high

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**  
I want to **collect travel times between all connected stations**  
So that **the TSP solver can calculate optimal routes**

**Acceptance Criteria**

- [ ] CSV file contains all direct station connections
- [ ] Each connection includes: from/to station IDs, travel time (minutes), connection type (train)
- [ ] Data sourced from official schedules or validated estimates
- [ ] Bidirectional connections properly represented (undirected graph)

**Story Points:** 13  
**Priority:** High


---

## US-103: Walking Network Data

**Labels:** data-collection, phase-1, epic-1, priority-medium

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**  
I want to **identify and measure walking connections between stations/platforms**  
So that **users can transfer between lines and nearby stations realistically**

**Acceptance Criteria**

- [ ] Transfer times within multi-line stations recorded (platform-to-platform)
- [ ] Walking connections between nearby stations identified (< 10 min walk)
- [ ] Walking times sourced from mapping APIs or manual measurement
- [ ] Connection type labeled as "walk_transfer" or "walk_between_stations"

**Story Points:** 8  
**Priority:** Medium


---

## US-104: Line Metadata

**Labels:** data-collection, phase-1, epic-1, priority-low

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**  
I want to **document metadata for each MRT/LRT line**  
So that **visualizations can display correct colors and labels**

**Acceptance Criteria**

- [ ] CSV with line codes, full names, official color codes, line type
- [ ] Covers all MRT and LRT lines
- [ ] Colors match official LTA branding

**Story Points:** 2  
**Priority:** Low


---

## US-201: Graph Builder Module

**Labels:** backend, graph, phase-1, epic-2, priority-high

**Milestone:** Epic 2: Graph Infrastructure

**User Story**

As a **developer**  
I want to **parse CSV data and construct a NetworkX graph**  
So that **I can run graph algorithms on the metro network**

**Acceptance Criteria**

- [ ] Python module reads stations, connections, and lines CSVs
- [ ] Constructs undirected weighted graph (weight = travel time)
- [ ] Validates graph connectivity (all stations reachable)
- [ ] Handles multi-line stations as separate nodes with walking edges
- [ ] Includes unit tests

**Story Points:** 8  
**Priority:** High


---

## US-202: Data Validation Pipeline

**Labels:** backend, validation, phase-1, epic-2, priority-medium

**Milestone:** Epic 2: Graph Infrastructure

**User Story**

As a **developer**  
I want to **validate the metro network data for errors**  
So that **the TSP solver doesn't fail due to bad data**

**Acceptance Criteria**

- [ ] Check for disconnected components in graph
- [ ] Verify all station IDs in connections exist in stations file
- [ ] Flag missing or negative travel times
- [ ] Report duplicate connections
- [ ] Generate validation report

**Story Points:** 5  
**Priority:** Medium


---

## US-301: Nearest Neighbor Heuristic

**Labels:** algorithm, phase-1, epic-3, priority-high

**Milestone:** Epic 3: TSP Solver Implementation

**User Story**

As a **developer**  
I want to **implement a Nearest Neighbor TSP algorithm**  
So that **I can quickly generate a baseline solution**

**Acceptance Criteria**



**Story Points:** 5  
**Priority:** High


---

## US-302: 2-Opt Local Search

**Labels:** algorithm, phase-1, epic-3, priority-high

**Milestone:** Epic 3: TSP Solver Implementation

**User Story**

As a **developer**  
I want to **implement 2-opt improvement on TSP tours**  
So that **I can optimize solutions from constructive heuristics**

**Acceptance Criteria**



**Story Points:** 8  
**Priority:** High


---

## US-303: Simulated Annealing Solver

**Labels:** algorithm, phase-1, epic-3, priority-medium

**Milestone:** Epic 3: TSP Solver Implementation

**User Story**

As a **developer**  
I want to **implement Simulated Annealing for TSP**  
So that **I can explore more of the solution space**

**Acceptance Criteria**



**Story Points:** 13  
**Priority:** Medium


---

## US-304: Genetic Algorithm Solver (Optional)

**Labels:** algorithm, phase-1, optional, epic-3, priority-low

**Milestone:** Epic 3: TSP Solver Implementation

**User Story**

As a **developer**  
I want to **implement a Genetic Algorithm for TSP**  
So that **I can compare population-based optimization**

**Acceptance Criteria**



**Story Points:** 13  
**Priority:** Low


---

## US-305: Algorithm Comparison Framework

**Labels:** algorithm, analysis, phase-1, epic-3, priority-medium

**Milestone:** Epic 3: TSP Solver Implementation

**User Story**

As a **developer**  
I want to **run multiple algorithms and compare results**  
So that **I can identify the best solver for this problem**

**Acceptance Criteria**

- [ ] Function runs all implemented algorithms on same graph
- [ ] Records solution quality (tour length) and computation time
- [ ] Generates comparison table/chart
- [ ] Saves results to file

**Story Points:** 5  
**Priority:** Medium


---

## US-401: Research Visualization Libraries

**Labels:** visualization, research, phase-1, epic-4, priority-high

**Milestone:** Epic 4: Visualization

**User Story**

As a **developer**  
I want to **evaluate visualization options (Plotly, Folium, Observable)**  
So that **I can choose the best tool for metro map display**

**Acceptance Criteria**

- [ ] Create proof-of-concept with each library
- [ ] Test Quarto integration
- [ ] Evaluate aesthetics, interactivity, development effort
- [ ] Document recommendation

**Story Points:** 8  
**Priority:** High


---

## US-402: Network Map Visualization

**Labels:** visualization, frontend, phase-1, epic-4, priority-high

**Milestone:** Epic 4: Visualization

**User Story**

As a **user**  
I want to **see a map of the entire MRT/LRT network**  
So that **I understand the layout and connections**

**Acceptance Criteria**

- [ ] All stations plotted at geographic coordinates
- [ ] Lines drawn between connected stations
- [ ] Color-coded by line (matching official colors)
- [ ] Station labels visible on hover/click
- [ ] Zoom and pan enabled

**Story Points:** 13  
**Priority:** High


---

## US-403: Route Overlay Visualization

**Labels:** visualization, frontend, phase-1, epic-4, priority-high

**Milestone:** Epic 4: Visualization

**User Story**

As a **user**  
I want to **see the optimal route highlighted on the map**  
So that **I can understand the path visually**

**Acceptance Criteria**

- [ ] Optimal tour drawn as highlighted path over network
- [ ] Station sequence indicated (numbers or arrows)
- [ ] Start/end station clearly marked
- [ ] Legend shows route vs. network

**Story Points:** 8  
**Priority:** High


---

## US-404: Route Details Panel

**Labels:** visualization, frontend, phase-1, epic-4, priority-medium

**Milestone:** Epic 4: Visualization

**User Story**

As a **user**  
I want to **see a list of stations in order with travel times**  
So that **I can follow the route step-by-step**

**Acceptance Criteria**

- [ ] Ordered list of all stations in tour
- [ ] Cumulative time displayed at each step
- [ ] Total journey time prominently shown
- [ ] Algorithm used and computation time noted
- [ ] Exportable as CSV or text

**Story Points:** 5  
**Priority:** Medium


---

## US-405: Starting Station Selector

**Labels:** visualization, frontend, interaction, phase-1, epic-4, priority-high

**Milestone:** Epic 4: Visualization

**User Story**

As a **user**  
I want to **choose which station to start/end at**  
So that **I can plan routes from my preferred location**

**Acceptance Criteria**

- [ ] Dropdown or searchable list of all stations
- [ ] Selecting station triggers route recalculation/display
- [ ] Map and route details update accordingly
- [ ] Performance acceptable (< 3s load time)

**Story Points:** 8  
**Priority:** High


---

## US-501: Quarto Document Structure

**Labels:** quarto, deployment, phase-1, epic-5, priority-high

**Milestone:** Epic 5: Quarto Integration & Deployment

**User Story**

As a **developer**  
I want to **create a Quarto document that integrates Python and visualizations**  
So that **I can generate a cohesive website**

**Acceptance Criteria**

- [ ] `.qmd` file with sections: Introduction, Methodology, Interactive Map, Results
- [ ] Python code cells execute graph building and TSP solving
- [ ] Visualizations embedded correctly
- [ ] Renders to HTML without errors

**Story Points:** 8  
**Priority:** High


---

## US-502: Pre-computation Pipeline

**Labels:** backend, deployment, phase-1, epic-5, priority-high

**Milestone:** Epic 5: Quarto Integration & Deployment

**User Story**

As a **developer**  
I want to **pre-compute optimal routes for all starting stations**  
So that **the static site loads quickly**

**Acceptance Criteria**

- [ ] Script iterates through all stations
- [ ] Runs best-performing algorithm for each
- [ ] Saves results to JSON/CSV
- [ ] Quarto document loads pre-computed data
- [ ] Total computation time < 6 hours

**Story Points:** 8  
**Priority:** High


---

## US-503: GitHub Pages Deployment

**Labels:** deployment, devops, phase-1, epic-5, priority-high

**Milestone:** Epic 5: Quarto Integration & Deployment

**User Story**

As a **developer**  
I want to **deploy the Quarto site to GitHub Pages**  
So that **users can access it online**

**Acceptance Criteria**

- [ ] GitHub Actions workflow builds Quarto site
- [ ] Publishes to `gh-pages` branch
- [ ] Site accessible at custom URL
- [ ] Updates automatically on push to main

**Story Points:** 5  
**Priority:** High


---

## US-504: Documentation & README

**Labels:** documentation, phase-1, epic-5, priority-medium

**Milestone:** Epic 5: Quarto Integration & Deployment

**User Story**

As a **user/developer**  
I want to **understand how to use and contribute to the project**  
So that **I can explore routes or add new cities**

**Acceptance Criteria**

- [ ] README.md with project description, features, usage instructions
- [ ] Data schema documentation
- [ ] Developer setup guide
- [ ] Contribution guidelines
- [ ] License file

**Story Points:** 5  
**Priority:** Medium


---

## US-601: Unit Tests for Graph Builder

**Labels:** testing, phase-1, epic-6, priority-medium

**Milestone:** Epic 6: Testing & Validation

**User Story**

As a **developer**  
I want to **ensure graph construction is correct**  
So that **downstream algorithms work properly**

**Acceptance Criteria**

- [ ] Test CSV parsing
- [ ] Test graph connectivity
- [ ] Test edge weight assignment
- [ ] Test multi-line station splitting
- [ ] Achieve > 90% code coverage

**Story Points:** 5  
**Priority:** Medium


---

## US-602: Algorithm Correctness Tests

**Labels:** testing, algorithm, phase-1, epic-6, priority-high

**Milestone:** Epic 6: Testing & Validation

**User Story**

As a **developer**  
I want to **validate TSP algorithms produce valid tours**  
So that **I know solutions are correct**

**Acceptance Criteria**

- [ ] Test on small known graphs (< 10 nodes)
- [ ] Verify tour visits each node exactly once
- [ ] Verify tour returns to starting node
- [ ] Compare against known optimal solutions
- [ ] Test edge cases (disconnected nodes, single node)

**Story Points:** 8  
**Priority:** High


---

## US-603: End-to-End Workflow Test

**Labels:** testing, integration, phase-1, epic-6, priority-medium

**Milestone:** Epic 6: Testing & Validation

**User Story**

As a **developer**  
I want to **test the full pipeline from data to visualization**  
So that **I catch integration issues**

**Acceptance Criteria**

- [ ] Automated test runs full workflow
- [ ] Verifies output files generated
- [ ] Checks visualization renders
- [ ] Runs in CI/CD pipeline

**Story Points:** 8  
**Priority:** Medium


---

## US-701: Schedule Integration

**Labels:** phase-2, enhancement, epic-7, priority-low

**Milestone:** Epic 7: Future Enhancements (Phase 2)

**User Story**

As a **user**  
I want to **account for real train schedules and wait times**  
So that **routes reflect actual feasible journeys**

**Acceptance Criteria**



**Story Points:** 21  
**Priority:** Low


---

## US-702: Multi-City Support

**Labels:** phase-2, enhancement, epic-7, priority-low

**Milestone:** Epic 7: Future Enhancements (Phase 2)

**User Story**

As a **user**  
I want to **solve TSP for other cities' metro networks**  
So that **I can explore different systems**

**Acceptance Criteria**



**Story Points:** 21  
**Priority:** Low


---

## US-703: OpenStreetMap Automation

**Labels:** phase-2, automation, epic-7, priority-low

**Milestone:** Epic 7: Future Enhancements (Phase 2)

**User Story**

As a **developer**  
I want to **automatically fetch metro network data from OSM**  
So that **I don't have to manually collect data for new cities**

**Acceptance Criteria**



**Story Points:** 13  
**Priority:** Low


---

## US-704: Non-Circular Routes

**Labels:** phase-2, enhancement, epic-7, priority-low

**Milestone:** Epic 7: Future Enhancements (Phase 2)

**User Story**

As a **user**  
I want to **generate routes that don't return to the start**  
So that **I have more flexibility in planning**

**Acceptance Criteria**



**Story Points:** 8  
**Priority:** Low


---

## US-801: Pruned SVG Base Map (Operational-Only)

**Labels:** visualization, svg, phase-1, epic-8, priority-high

**Milestone:** Epic 8: SVG Map Integration

**User Story**

As a **developer**  
I want to **prune the base SVG map to only operational stations/lines**  
So that **rendered tours match the dataset and exclude unbuilt lines**

**Acceptance Criteria**

- [ ] Python script `scripts/prune_svg_map.py` reads `data/raw/Singapore_MRT_and_LRT_System_Map.svg`
- [ ] Filters to stations where `status == operational` from `data/raw/stations.csv`
- [ ] Uses optional mapping file `data/processed/svg_name_map.csv` to resolve label/name mismatches
- [ ] Removes or hides non-operational stations and segments from the SVG
- [ ] Writes pruned map to `data/processed/sg_mrt_lrt_built_only.svg`
- [ ] Preserves CC BY-SA 3.0 attribution within repo and in the output SVG metadata
- [ ] Generates a report/list of unmatched SVG labels for mapping updates

**Story Points:** 5  
**Priority:** High


---

## US-802: SVG Name Mapping & Validation

**Labels:** visualization, svg, phase-1, epic-8, priority-medium

**Milestone:** Epic 8: SVG Map Integration

**User Story**

As a **developer**  
I want to **maintain a mapping between SVG labels and station IDs**  
So that **the pruning and overlay scripts can reliably match stations**

**Acceptance Criteria**

- [ ] Create `data/processed/svg_name_map.csv` with columns: `svg_label,station_id`
- [ ] Script `scripts/validate_svg_mapping.py` reports missing/ambiguous mappings and unmatched SVG elements
- [ ] Mapping covers ≥ 95% of operational stations; remaining listed in a TODO section
- [ ] Document how to update the mapping in `docs/visualization/svg_map_integration.md`

**Story Points:** 3  
**Priority:** Medium


---

## US-803: Tour Overlay Renderer (Arrows + Steps)

**Labels:** visualization, svg, phase-1, epic-8, priority-high

**Milestone:** Epic 8: SVG Map Integration

**User Story**

As a **user**  
I want to **render a single TSP tour onto the pruned SVG with directional arrows and step numbers**  
So that **I can visually follow the route station by station**

**Acceptance Criteria**

- [ ] Python script `scripts/render_tour_to_svg.py` accepts: pruned SVG path, ordered tour (station IDs), style options
- [ ] Draws per-segment paths with arrowheads indicating direction
- [ ] Places step numbers along the path or at stations; start/end markers included
- [ ] Outputs static SVG per tour to `data/processed/maps/<tour_name>.svg`
- [ ] Works with tours generated by implemented solvers (NN, 2-opt, SA, GA) via station IDs
- [ ] Legend and basic styles included; single tour per render

**Story Points:** 8  
**Priority:** High


---

## US-804: Export Sample Static SVGs

**Labels:** visualization, svg, phase-1, epic-8, priority-medium

**Milestone:** Epic 8: SVG Map Integration

**User Story**

As a **developer**  
I want to **export example static SVGs for selected tours**  
So that **they can be embedded in notebooks/pages immediately**

**Acceptance Criteria**

- [ ] Generate at least one sample tour using an existing solver
- [ ] Render static SVG to `data/processed/maps/*.svg` using the overlay script
- [ ] Add a short README or doc note with usage and CC BY-SA attribution

**Story Points:** 3  
**Priority:** Medium


---

