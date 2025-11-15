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

- [x] CSV file contains all direct station connections
- [x] Each connection includes: from/to station IDs, travel time (minutes), connection type (train)
- [x] Data sourced from official schedules or validated estimates
- [x] Bidirectional connections properly represented (undirected graph)

**Story Points:** 13
**Priority:** High

**Status:** ✅ Completed. Generated `connections.csv` with 554 connections (398 train + 156 walking) covering all station pairs (commit c2ccb37). Travel times calculated using distance/speed estimates with methodology documented in `data/raw/CONNECTIONS_SOURCE.md`. Bidirectional connections properly represented.


---

## US-103: Walking Network Data

**Labels:** data-collection, phase-1, epic-1, priority-medium

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**
I want to **identify and measure walking connections between stations/platforms**
So that **users can transfer between lines and nearby stations realistically**

**Acceptance Criteria**

- [x] Transfer times within multi-line stations recorded (platform-to-platform)
- [x] Walking connections between nearby stations identified (< 10 min walk)
- [x] Walking times sourced from mapping APIs or manual measurement
- [x] Connection type labeled as "walk_transfer" or "walk_between_stations"

**Story Points:** 8
**Priority:** Medium

**Status:** ✅ Completed. Added 156 walking connections to `connections.csv` (commit 87d54d5). Includes 72 walk_transfer connections for interchange stations and 84 walk_between_stations for nearby stations. Walking times sourced from Google Maps and documented in `data/raw/WALKING_CONNECTIONS_SOURCE.md`.


---

## US-104: Line Metadata

**Labels:** data-collection, phase-1, epic-1, priority-low

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**
I want to **document metadata for each MRT/LRT line**
So that **visualizations can display correct colors and labels**

**Acceptance Criteria**

- [x] CSV with line codes, full names, official color codes, line type
- [x] Covers all MRT and LRT lines
- [x] Colors match official LTA branding

**Story Points:** 2
**Priority:** Low

**Status:** ✅ Completed. Created `data/raw/lines.csv` with metadata for all 15 lines (commit e2b979a). Includes line codes, full names, official hex color codes matching LTA branding, and line types (MRT/LRT).


---

## US-105: Verify Interchange Station Coordinates

**Labels:** enhancement, data-collection, phase-1, epic-1, priority-medium

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**  
I want to **verify and update coordinates for interchange stations with physically separated platforms**  
So that **the TSP model accurately reflects walking distances between platforms**

**Acceptance Criteria**

- [ ] Identify interchange stations where platforms are physically separated (e.g., Tampines DT/EW requiring fare gate exit)
- [ ] Source actual platform coordinates from OpenStreetMap or LTA data
- [ ] Update stations.csv with platform-specific coordinates where applicable
- [ ] Document stations with significant inter-platform walking distances (>5 min)
- [ ] Validation script confirms coordinate accuracy

**Story Points:** 5  
**Priority:** Medium

**Notes:** Some interchange stations like Tampines require tapping out, walking ~10 minutes through external areas (e.g., markets), then re-entering. Current data shows identical coordinates for both platforms, which doesn't reflect this reality.

**Status:** Analysis complete (29 interchanges identified, 2 confirmed separations). See `data/raw/INTERCHANGE_COORDINATE_ANALYSIS.md` for details.


---

## US-106: Fix Edge Cases in Connection Generation

**Labels:** bug, data-collection, phase-1, epic-1, priority-medium

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**  
I want to **handle special station code formats in the connection generator**  
So that **all station connections are properly generated including terminus stations**

**Acceptance Criteria**

- [ ] Connection generator handles station codes without numbers (e.g., CG, STC, PTC)
- [ ] Terminus and special stations properly connected in connections.csv
- [ ] Validation script confirms all stations have at least one connection
- [ ] Unit tests for edge cases

**Story Points:** 3  
**Priority:** Medium

**Technical Details:** Current issue: Station ID "CG" (Tanah Merah on CG line) not processed by generate_connections.py. Missing connection: CG → CG1 (Tanah Merah to Expo). Similar issues may exist for PTC, STC stations.

**Status:** ✅ Completed. Fixed in PR #33 (commit 1641ce9). Train connections increased from 386 to 388.


---

## US-107: Travel Time Calibration Based on Field Measurements

**Labels:** enhancement, data-collection, phase-1, epic-1, priority-low

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**  
I want to **calibrate travel time estimates using real-world measurements**  
So that **the TSP solver uses accurate travel times for route optimization**

**Acceptance Criteria**

- [ ] Analysis script compares observed vs estimated travel times
- [ ] Documentation of calibration methodology and findings
- [ ] Speed/dwell parameters adjusted if error > 15%
- [ ] Validation report shows <10% average error after calibration

**Story Points:** 3  
**Priority:** Low

**Technical Details:** Current measurements show 9.14% average absolute error (acceptable). Dwell time parameter (0.5 min) is well-calibrated. Analysis script: scripts/analyze_observations.py. Field data: data/raw/observations.md.

**Status:** ✅ Completed. Analysis script created (commit 626c31d). Parameters validated, no adjustments needed.


---

## US-108: Fix Disconnected LRT and TE Extension Connections

**Labels:** data-collection, data-fix, phase-1, epic-1, priority-high

**Milestone:** Epic 1: Data Foundation

**User Story**

As a **developer**
I want to **add missing connections between LRT hub stations and loop stations, and fix TE line gaps**
So that **the network graph is fully connected and TSP algorithms can traverse all stations**

**Acceptance Criteria**

- [x] Sengkang LRT connected: STC hub ↔ SE1 (East Loop) and STC hub ↔ SW1 (West Loop)
- [x] Punggol LRT connected: PTC hub ↔ PE1 (East Loop) and PTC hub ↔ PW1 (West Loop)
- [x] Thomson-East Coast Line connected: TE20 ↔ TE22 (fill TE21 gap or direct connection)
- [x] All connections bidirectional with appropriate travel times
- [x] Graph connectivity validation passes (single connected component)
- [x] Connection type properly labeled (train for LRT loops, appropriate for TE gap)

**Background**

Graph builder (US-201) identified 6 disconnected components:
1. Main network (179 stations) - ✅ connected
2. SE (Sengkang East Loop) - 5 stations, disconnected from STC
3. SW (Sengkang West Loop) - 8 stations, disconnected from STC
4. PE (Punggol East Loop) - 7 stations, disconnected from PTC
5. PW (Punggol West Loop) - 7 stations, disconnected from PTC
6. TE22-TE29 extension - 8 stations, gap between TE20 and TE22

**Technical Details**

Missing connections identified:
- STC (at NE16 Sengkang) exists with walk_transfer to NE16, but no train connections to SE1/SW1
- PTC (at NE17 Punggol) exists with walk_transfer to NE17, but no train connections to PE1/PW1
- TE20 (Marina Bay) exists, TE22 (Gardens by the Bay) exists, but no TE21 or direct link

**Story Points:** 5
**Priority:** High

**Status:** ✅ Completed. Added missing LRT hub connections and TE line gap connection (commit dce8cee). Network is now fully connected with single component. All 4 LRT loops properly connected to their hub stations, and TE line gap bridged with TE21 station. Graph validation confirms full connectivity.


---

## US-201: Graph Builder Module

**Labels:** backend, graph, phase-1, epic-2, priority-high

**Milestone:** Epic 2: Graph Infrastructure

**User Story**

As a **developer**
I want to **parse CSV data and construct a NetworkX graph**
So that **I can run graph algorithms on the metro network**

**Acceptance Criteria**

- [x] Python module reads stations, connections, and lines CSVs
- [x] Constructs undirected weighted graph (weight = travel time)
- [x] Validates graph connectivity (all stations reachable)
- [x] Handles multi-line stations as separate nodes with walking edges
- [x] Includes unit tests

**Story Points:** 8
**Priority:** High

**Status:** ✅ Completed. Full implementation in `src/graph/builder.py` with `MetroGraphBuilder` class (commit 61dceba). Comprehensive unit tests with 30+ test cases. Successfully loads 214 stations and 277 connections. Graph is fully connected.


---

## US-202: Data Validation Pipeline

**Labels:** backend, validation, phase-1, epic-2, priority-medium

**Milestone:** Epic 2: Graph Infrastructure

**User Story**

As a **developer**
I want to **validate the metro network data for errors**
So that **the TSP solver doesn't fail due to bad data**

**Acceptance Criteria**

- [x] Check for disconnected components in graph
- [x] Verify all station IDs in connections exist in stations file
- [x] Flag missing or negative travel times
- [x] Report duplicate connections
- [x] Generate validation report

**Story Points:** 5
**Priority:** Medium

**Status:** ✅ Completed. Full validation pipeline in `src/graph/validator.py` with `MetroDataValidator` class (commit 11ad251). Validates all data integrity checks, detects errors, warnings, and info messages. Includes comprehensive unit tests in `tests/test_validator.py`. Working demo in `notebooks/graph_infrastructure_demo.ipynb`.


---

## US-301: Nearest Neighbor Heuristic

**Labels:** algorithm, phase-1, epic-3, priority-high

**Milestone:** Epic 3: TSP Solver Implementation

**User Story**

As a **developer**
I want to **implement a Nearest Neighbor TSP algorithm**
So that **I can quickly generate a baseline solution**

**Acceptance Criteria**

- [x] Function accepts graph and starting station
- [x] Returns tour (ordered list of stations) and total time
- [x] Deterministic results
- [x] Runs in < 5 seconds for 189 nodes
- [x] Unit tested

**Story Points:** 5
**Priority:** High

**Status:** ✅ Completed. Implemented greedy nearest neighbor TSP algorithm in `src/solvers/nearest_neighbor.py` (commit d98469b). Algorithm visits nearest unvisited station until all visited, then returns to start. Deterministic results, runs in < 0.5s for 214 stations. Comprehensive unit tests with 17 test cases covering functionality, performance, determinism, and edge cases. All tests passing.


---

## US-302: 2-Opt Local Search

**Labels:** algorithm, phase-1, epic-3, priority-high

**Milestone:** Epic 3: TSP Solver Implementation

**User Story**

As a **developer**  
I want to **implement 2-opt improvement on TSP tours**  
So that **I can optimize solutions from constructive heuristics**

**Acceptance Criteria**

- [ ] Function accepts initial tour and graph
- [ ] Iteratively improves tour by reversing segments
- [ ] Configurable iteration limit or convergence threshold
- [ ] Returns improved tour and time savings
- [ ] Unit tested

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

- [ ] Configurable cooling schedule
- [ ] Random neighbor generation (2-opt swaps)
- [ ] Accepts or rejects moves based on SA criteria
- [ ] Returns best tour found
- [ ] Benchmarked against other algorithms

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

- [ ] Configurable population size, generations, mutation rate
- [ ] Crossover operator for TSP tours (e.g., order crossover)
- [ ] Mutation operator (swap, reverse)
- [ ] Returns best tour from final population

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

