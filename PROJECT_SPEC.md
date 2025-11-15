# Metro TSP Solver - Project Specification

**Project Name:** Metro Route Optimizer  
**Version:** 1.0  
**Date:** November 8, 2025  
**Target City (Phase 1):** Singapore MRT/LRT Network

---

## 1. Problem Statement

### Overview
Develop a Traveling Salesman Problem (TSP) solver for metro networks that generates an optimal route visiting all stations in a city's metro system exactly once, returning to the starting station. The solution should provide both algorithmic optimization and interactive visualization, initially targeting Singapore's MRT/LRT network with ~189 stations.

### Business Context
This is a hobbyist project aimed at metro enthusiasts who want to explore theoretical "complete network traversal" routes. The project serves both educational purposes (demonstrating NP-hard problem solving) and entertainment value for transit aficionados.

### Key Objectives
1. **Primary Goal:** Calculate the shortest possible route (by time) that visits every station in Singapore's MRT/LRT network exactly once and returns to the starting point
2. **User Experience:** Allow users to select any station as their starting point
3. **Visualization:** Present the optimal route on an interactive metro-map-style visualization
4. **Extensibility:** Design architecture to support future cities and additional features (schedules, wait times, etc.)

---

## 2. Functional Requirements

### 2.1 Core Features (MVP - Phase 1)

#### FR-1: Network Data Model
- **FR-1.1:** Represent metro network as an undirected weighted graph
  - Nodes: Individual stations (including platform duplicates for multi-line stations)
  - Edges: Direct connections between stations (train links)
  - Weights: Time in minutes to traverse each edge
  
- **FR-1.2:** Support "walking network" for inter-platform transfers
  - Multi-line stations modeled as separate nodes per line
  - Walking edges connect platforms within same station (transfer time)
  - Walking edges connect nearby stations where walking is faster than train routing
  
- **FR-1.3:** Include all active Singapore MRT/LRT lines
  - North-South Line (NSL)
  - East-West Line (EWL)
  - Circle Line (CCL)
  - Downtown Line (DTL)
  - Thomson-East Coast Line (TEL)
  - North East Line (NEL)
  - All LRT lines (Bukit Panjang, Sengkang, Punggol)
  - Stations currently under construction (as per 2025 status)

#### FR-2: TSP Solver
- **FR-2.1:** Implement multiple TSP solving algorithms
  - Exact algorithms (for benchmarking on smaller subsets)
  - Heuristic approaches (Nearest Neighbor, 2-opt, Christofides)
  - Metaheuristics (Genetic Algorithm, Simulated Annealing)
  
- **FR-2.2:** Algorithm comparison framework
  - Ability to run multiple algorithms on same dataset
  - Compare solution quality (total time/distance)
  - Compare computation time
  
- **FR-2.3:** User-selectable starting station
  - Any station in network can be designated as start/end point
  - Solution must form complete cycle returning to start

#### FR-3: Visualization
- **FR-3.1:** Interactive metro map display
  - Geographically representative station layout
  - Color-coded lines matching official MRT colors
  - Station markers with labels
  
- **FR-3.2:** Route visualization
  - Highlight optimal route on map
  - Show route sequence (station order)
  - Display total journey time
  - Show algorithm used and computation time
  
- **FR-3.3:** User interaction
  - Click/select starting station
  - Display route details (list view + map view)
  - Export route as text/CSV

#### FR-4: Web Deployment
- **FR-4.1:** Static site generation via Quarto
  - Python computation backend embedded in Quarto document
  - Interactive visualizations (Observable.js/Plotly)
  - Deployable to GitHub Pages
  
- **FR-4.2:** No server-side computation required for MVP
  - Pre-computed routes for common starting stations, OR
  - Client-side computation using PyScript/WASM if feasible

### 2.2 Future Enhancements (Phase 2+)

#### FR-5: Schedule Integration
- Incorporate actual train schedules
- Account for wait times at stations
- Time-of-day dependent routing

#### FR-6: Multi-City Support
- Generalized data ingestion from OpenStreetMap
- Support for other cities' metro networks
- Automated data pipeline

#### FR-7: Advanced Visualizations
- Animated route playback
- 3D network visualization
- Custom map styling

#### FR-8: Route Variants
- Non-circular routes (start anywhere, end anywhere)
- Subset routing (visit only specific lines)
- Multi-objective optimization (time vs. transfers)

---

## 3. Technical Specification

### 3.1 Technology Stack

#### Backend/Computation
- **Language:** Python 3.11+
- **Graph Library:** NetworkX
- **Optimization:** 
  - `scipy.optimize`
  - `python-tsp` (if suitable)
  - Custom implementations
- **Data Processing:** Pandas, NumPy

#### Data Acquisition
- **Manual Entry:** Initial dataset via CSV
- **APIs (Future):**
  - OpenStreetMap (Overpass API) for network topology
  - Google Maps Distance Matrix API for travel times
  - OneMap API (Singapore-specific) for local accuracy

#### Visualization
- **Options to Evaluate:**
  1. **Plotly:** Python-based, good Quarto integration
  2. **Observable.js:** Rich interactivity, excellent for maps
  3. **Folium:** Python library for Leaflet.js maps
  4. **D3.js:** Maximum customization, steeper learning curve

#### Deployment
- **Site Generator:** Quarto
- **Hosting:** GitHub Pages
- **Alternative (if dynamic needed):** FastAPI + React (future consideration)

### 3.2 Data Schema

#### Stations Table (`stations.csv`)
```
station_id, station_name, line_code, latitude, longitude, operational_status
```

#### Connections Table (`connections.csv`)
```
connection_id, from_station_id, to_station_id, connection_type, travel_time_minutes, distance_meters
```
- `connection_type`: `train`, `walk_transfer`, `walk_between_stations`

#### Lines Metadata (`lines.csv`)
```
line_code, line_name, color_hex, line_type
```
- `line_type`: `mrt`, `lrt`

### 3.3 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ stations.csv │  │connections.csv│  │  lines.csv   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   GRAPH BUILDER                              │
│  • Parse CSV data                                            │
│  • Construct NetworkX graph                                  │
│  • Validate topology (connectivity, weights)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   TSP SOLVER ENGINE                          │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ Nearest        │  │ 2-opt Local    │  │  Simulated   │  │
│  │ Neighbor       │  │ Search         │  │  Annealing   │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │ Genetic        │  │ Christofides   │                     │
│  │ Algorithm      │  │ (if applicable)│                     │
│  └────────────────┘  └────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  SOLUTION FORMATTER                          │
│  • Generate route sequence                                   │
│  • Calculate statistics                                      │
│  • Prepare visualization data                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              VISUALIZATION LAYER (Quarto)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Interactive Map (Plotly/Observable/Folium)          │   │
│  │  • Display network                                    │   │
│  │  • Highlight route                                    │   │
│  │  • Station selector                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Route Details Panel                                  │   │
│  │  • Station sequence                                   │   │
│  │  • Total time/distance                                │   │
│  │  • Algorithm metadata                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    GitHub Pages (Static Site)
```

### 3.4 Key Design Decisions

#### Decision 1: Pre-computation vs. Real-time Computation
**Options:**
- **A:** Pre-compute routes for all 189 starting stations, embed in static site
- **B:** Use PyScript/Pyodide for in-browser Python computation
- **C:** FastAPI backend for on-demand computation

**Recommendation:** Start with Option A (pre-computation) for MVP
- Pros: Fastest user experience, works on static hosting, no backend needed
- Cons: Less flexible, regeneration needed for data updates
- Future: Explore Option B if computation time is reasonable (<30s)

#### Decision 2: Visualization Library
**Evaluation Criteria:**
- Quarto integration quality
- Metro-map aesthetics
- Interactivity (zoom, pan, click)
- Development speed

**Candidates:**
1. **Plotly:** Excellent Quarto support, good for quick prototypes
2. **Folium:** Great for geographic maps, easy Python integration
3. **Observable.js in Quarto:** Best interactivity, requires learning curve

**Recommendation:** Prototype with Plotly, evaluate Observable.js for final version

#### Decision 3: Multi-Line Station Modeling
**Approach:** Treat each platform as separate node
- Station "Dhoby Ghaut" becomes: `DG_NSL`, `DG_CCL`, `DG_NEL`
- Walking edges: `DG_NSL` ↔ `DG_CCL` (3 min), `DG_CCL` ↔ `DG_NEL` (2 min), etc.
- Ensures TSP visits each "platform" once (more realistic for enthusiasts)

**Alternative:** Single node per station (ignoring platform transfers)
- Simpler model, may skip the "platform visit" realism

**Decision:** Use multi-node model for accuracy, provide config flag to toggle

#### Decision 4: Metric Closure for TSP Solvers (Epic 3)
**Problem:** The raw metro graph is sparse, contains branches/leaf termini, and does not generally admit a Hamiltonian cycle using only original train + walking-transfer edges. Greedy constructive heuristics (e.g., Nearest Neighbor) can stall when confined to direct adjacency.

**Decision:** All TSP algorithms (Nearest Neighbor, 2-Opt, Simulated Annealing, Genetic Algorithm) operate on the **metric closure** of the transit graph—a complete graph whose edge weights are shortest-path travel times in the original network.

**Benefits:**
- Eliminates dead-ends for heuristics by ensuring universal adjacency
- Normalizes cost evaluation across algorithms
- Reflects realistic travel time where indirect routing (via transfers) may be faster than direct edges
- Simplifies integration of local search operators (2-opt always valid)

**Trade-offs:**
- Returned tour is an ordering of stations under shortest-path distances, not a literal single-pass traversal strictly following original edges without revisits.
- Some segments in the theoretical tour may correspond to multi-edge paths in the physical network; reconstruction step required for visualization/export.

**Implementation Notes:**
- Utility `build_metric_closure(graph)` added in `src/utils/metric.py`.
- Solvers construct / reuse closure internally; future optimization may cache closure on the graph object.
- Two-Opt reports original graph cost when possible for backward compatibility in tests.

**Future Option:** Provide a configuration toggle for "strict traversal mode" that forces algorithms to work directly on the sparse graph with path-feasibility checks or allows controlled node revisits.

### 3.5 Data Collection Plan

#### Phase 1: Manual Data Entry (Singapore MRT)

**Step 1: Station Inventory**
- Source: Land Transport Authority (LTA) official list
- Tools: Manual compilation into `stations.csv`
- Estimated effort: 4-6 hours
- Deliverable: Complete station list with line assignments

**Step 2: Inter-Station Travel Times**
**Method A - Schedule-Based (Preferred):**
- Source: Official MRT timetables (station-to-station times)
- Tools: Manual entry from LTA websites/apps
- Estimated effort: 10-15 hours
- Accuracy: High

**Method B - Distance-Based Estimation:**
- Formula: `time = distance / avg_speed + dwell_time`
- Average speed: 45-60 km/h for MRT, 30-40 km/h for LRT
- Dwell time: 0.5-1 min per station
- Tools: Calculate from geographic coordinates
- Estimated effort: 6-8 hours
- Accuracy: Medium

**Step 3: Walking Connections**
**Method A - Mapping Services:**
- Use Google Maps walking directions API
- Measure transfer times within stations
- Identify walk-able station pairs (< 10 min walk)
- Tools: API calls + manual verification
- Estimated effort: 8-12 hours

**Method B - Manual Research:**
- Use official station maps for internal transfers
- Estimate nearby station walks from Google Maps
- Tools: Browser + spreadsheet
- Estimated effort: 10-15 hours

**Recommended Approach:** Method A (schedule) + Method A (walking API) with manual verification

#### Phase 2: Automated Ingestion (Future Cities)

**OpenStreetMap Pipeline:**
1. Query Overpass API for railway networks
2. Extract stations and connections
3. Use OSM routing for walking times
4. Validate and supplement with external sources

**Tools to Develop:**
- OSM query builder script
- Data validation pipeline
- Gap-filling heuristics

---

## 4. Success Metrics

### 4.1 MVP Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Network Coverage | 100% of active stations | Count of stations in dataset |
| Solution Quality | Within 15% of theoretical optimum | Compare to lower bounds |
| Computation Time | < 2 minutes per starting station | Runtime benchmarks |
| Visualization Load Time | < 3 seconds | Browser performance tests |
| Route Validity | 100% valid TSP tours | Automated validation |
| User Satisfaction | Positive feedback from 5+ testers | User testing |

### 4.2 Algorithm Performance KPIs

- **Solution Optimality:** Compare multiple algorithms, document best performer
- **Scalability:** Track performance as network size increases
- **Repeatability:** Ensure deterministic results (or controlled randomness)

---

## 5. JIRA-Style User Stories

### Epic 1: Data Foundation

#### US-101: Station Data Collection
**As a** developer  
**I want to** compile a complete list of all Singapore MRT/LRT stations with metadata  
**So that** I can build an accurate network model  

**Acceptance Criteria:**
- [ ] CSV file contains all 189+ active/under-construction stations
- [ ] Each station has: unique ID, name, line code(s), lat/long, operational status
- [ ] Multi-line stations have separate entries per platform
- [ ] Data validated against official LTA sources

**Story Points:** 5  
**Priority:** High  
**Labels:** data-collection, phase-1

---

#### US-102: Inter-Station Travel Time Data
**As a** developer  
**I want to** collect travel times between all connected stations  
**So that** the TSP solver can calculate optimal routes  

**Acceptance Criteria:**
- [ ] CSV file contains all direct station connections
- [ ] Each connection includes: from/to station IDs, travel time (minutes), connection type (train)
- [ ] Data sourced from official schedules or validated estimates
- [ ] Bidirectional connections properly represented (undirected graph)

**Story Points:** 13  
**Priority:** High  
**Labels:** data-collection, phase-1

---

#### US-103: Walking Network Data
**As a** developer  
**I want to** identify and measure walking connections between stations/platforms  
**So that** users can transfer between lines and nearby stations realistically  

**Acceptance Criteria:**
- [ ] Transfer times within multi-line stations recorded (platform-to-platform)
- [ ] Walking connections between nearby stations identified (< 10 min walk)
- [ ] Walking times sourced from mapping APIs or manual measurement
- [ ] Connection type labeled as "walk_transfer" or "walk_between_stations"

**Story Points:** 8  
**Priority:** Medium  
**Labels:** data-collection, phase-1

---

#### US-104: Line Metadata
**As a** developer  
**I want to** document metadata for each MRT/LRT line  
**So that** visualizations can display correct colors and labels  

**Acceptance Criteria:**
- [ ] CSV with line codes, full names, official color codes, line type
- [ ] Covers all MRT and LRT lines
- [ ] Colors match official LTA branding

**Story Points:** 2  
**Priority:** Low  
**Labels:** data-collection, phase-1

---

### Epic 2: Graph Infrastructure

#### US-201: Graph Builder Module
**As a** developer  
**I want to** parse CSV data and construct a NetworkX graph  
**So that** I can run graph algorithms on the metro network  

**Acceptance Criteria:**
- [ ] Python module reads stations, connections, and lines CSVs
- [ ] Constructs undirected weighted graph (weight = travel time)
- [ ] Validates graph connectivity (all stations reachable)
- [ ] Handles multi-line stations as separate nodes with walking edges
- [ ] Includes unit tests

**Story Points:** 8  
**Priority:** High  
**Labels:** backend, graph, phase-1

---

#### US-202: Data Validation Pipeline
**As a** developer  
**I want to** validate the metro network data for errors  
**So that** the TSP solver doesn't fail due to bad data  

**Acceptance Criteria:**
- [ ] Check for disconnected components in graph
- [ ] Verify all station IDs in connections exist in stations file
- [ ] Flag missing or negative travel times
- [ ] Report duplicate connections
- [ ] Generate validation report

**Story Points:** 5  
**Priority:** Medium  
**Labels:** backend, validation, phase-1

---

### Epic 3: TSP Solver Implementation

#### US-301: Nearest Neighbor Heuristic
**As a** developer  
**I want to** implement a Nearest Neighbor TSP algorithm  
**So that** I can quickly generate a baseline solution  

**Acceptance Criteria:**
- [x] Function accepts graph and starting station
- [x] Returns tour (ordered list of stations) and total time
- [x] Deterministic results
- [x] Runs in < 5 seconds for 189 nodes
- [x] Unit tested

**Story Points:** 5  
**Priority:** High  
**Labels:** algorithm, phase-1

**Status:** ✅ Completed. Implemented in commit d98469b and demo added in 8265463. Includes single-start nearest neighbor algorithm with comprehensive unit tests (29 tests). Runs in <1 second for 189 nodes. Multi-start variant and combined NN+2-Opt workflow also implemented.

---

#### US-302: 2-Opt Local Search
**As a** developer  
**I want to** implement 2-opt improvement on TSP tours  
**So that** I can optimize solutions from constructive heuristics  

**Acceptance Criteria:**
- [x] Function accepts initial tour and graph
- [x] Iteratively improves tour by reversing segments
- [x] Configurable iteration limit or convergence threshold
- [x] Returns improved tour and time savings
- [x] Unit tested

**Story Points:** 8  
**Priority:** High  
**Labels:** algorithm, phase-1

**Status:** ✅ Completed. Merged to main in PR #34 (commit 17631e3). Includes standard and fast 2-opt implementations with 25 comprehensive tests. Supports configurable max iterations and improvement thresholds. Integrates seamlessly with NN algorithm. Demo notebook showcases combined workflow.

---

#### US-303: Simulated Annealing Solver
**As a** developer  
**I want to** implement Simulated Annealing for TSP  
**So that** I can explore more of the solution space  

**Acceptance Criteria:**
- [x] Configurable cooling schedule
- [x] Random neighbor generation (2-opt swaps)
- [x] Accepts or rejects moves based on SA criteria
- [x] Returns best tour found
- [x] Benchmarked against other algorithms

**Story Points:** 13  
**Priority:** Medium  
**Labels:** algorithm, phase-1

**Status:** ✅ Completed. Implemented in commit 027cab5. Probabilistic metaheuristic with three cooling schedules (linear, exponential, logarithmic). Includes adaptive variant for automatic parameter tuning. 30 comprehensive unit tests with 100% coverage. Can escape local optima through probabilistic acceptance. Works with both random and warm starts.

---

#### US-304: Genetic Algorithm Solver (Optional)
**As a** developer  
**I want to** implement a Genetic Algorithm for TSP  
**So that** I can compare population-based optimization  

**Acceptance Criteria:**
- [x] Configurable population size, generations, mutation rate
- [x] Crossover operator for TSP tours (e.g., order crossover)
- [x] Mutation operator (swap, reverse)
- [x] Returns best tour from final population

**Story Points:** 13  
**Priority:** Low  
**Labels:** algorithm, phase-1, optional

**Status:** ✅ Completed. Implemented in commit 027cab5. Population-based evolutionary metaheuristic with Order Crossover (OX) and Partially Mapped Crossover (PMX). Swap and reverse (2-opt) mutation operators. Tournament and rank selection methods. 31 comprehensive unit tests. Includes adaptive variant with convergence detection and parameter adjustment.

---

#### US-305: Algorithm Comparison Framework
**As a** developer  
**I want to** run multiple algorithms and compare results  
**So that** I can identify the best solver for this problem  

**Acceptance Criteria:**
- [ ] Function runs all implemented algorithms on same graph
- [ ] Records solution quality (tour length) and computation time
- [ ] Generates comparison table/chart
- [ ] Saves results to file

**Story Points:** 5  
**Priority:** Medium  
**Labels:** algorithm, analysis, phase-1

---

### Epic 4: Visualization

#### US-401: Research Visualization Libraries
**As a** developer  
**I want to** evaluate visualization options (Plotly, Folium, Observable)  
**So that** I can choose the best tool for metro map display  

**Acceptance Criteria:**
- [ ] Create proof-of-concept with each library
- [ ] Test Quarto integration
- [ ] Evaluate aesthetics, interactivity, development effort
- [ ] Document recommendation

**Story Points:** 8  
**Priority:** High  
**Labels:** visualization, research, phase-1

---

#### US-402: Network Map Visualization
**As a** user  
**I want to** see a map of the entire MRT/LRT network  
**So that** I understand the layout and connections  

**Acceptance Criteria:**
- [ ] All stations plotted at geographic coordinates
- [ ] Lines drawn between connected stations
- [ ] Color-coded by line (matching official colors)
- [ ] Station labels visible on hover/click
- [ ] Zoom and pan enabled

**Story Points:** 13  
**Priority:** High  
**Labels:** visualization, frontend, phase-1

---

#### US-403: Route Overlay Visualization
**As a** user  
**I want to** see the optimal route highlighted on the map  
**So that** I can understand the path visually  

**Acceptance Criteria:**
- [ ] Optimal tour drawn as highlighted path over network
- [ ] Station sequence indicated (numbers or arrows)
- [ ] Start/end station clearly marked
- [ ] Legend shows route vs. network

**Story Points:** 8  
**Priority:** High  
**Labels:** visualization, frontend, phase-1

---

#### US-404: Route Details Panel
**As a** user  
**I want to** see a list of stations in order with travel times  
**So that** I can follow the route step-by-step  

**Acceptance Criteria:**
- [ ] Ordered list of all stations in tour
- [ ] Cumulative time displayed at each step
- [ ] Total journey time prominently shown
- [ ] Algorithm used and computation time noted
- [ ] Exportable as CSV or text

**Story Points:** 5  
**Priority:** Medium  
**Labels:** visualization, frontend, phase-1

---

#### US-405: Starting Station Selector
**As a** user  
**I want to** choose which station to start/end at  
**So that** I can plan routes from my preferred location  

**Acceptance Criteria:**
- [ ] Dropdown or searchable list of all stations
- [ ] Selecting station triggers route recalculation/display
- [ ] Map and route details update accordingly
- [ ] Performance acceptable (< 3s load time)

**Story Points:** 8  
**Priority:** High  
**Labels:** visualization, frontend, interaction, phase-1

---

### Epic 5: Quarto Integration & Deployment

#### US-501: Quarto Document Structure
**As a** developer  
**I want to** create a Quarto document that integrates Python and visualizations  
**So that** I can generate a cohesive website  

**Acceptance Criteria:**
- [ ] `.qmd` file with sections: Introduction, Methodology, Interactive Map, Results
- [ ] Python code cells execute graph building and TSP solving
- [ ] Visualizations embedded correctly
- [ ] Renders to HTML without errors

**Story Points:** 8  
**Priority:** High  
**Labels:** quarto, deployment, phase-1

---

#### US-502: Pre-computation Pipeline
**As a** developer  
**I want to** pre-compute optimal routes for all starting stations  
**So that** the static site loads quickly  

**Acceptance Criteria:**
- [ ] Script iterates through all stations
- [ ] Runs best-performing algorithm for each
- [ ] Saves results to JSON/CSV
- [ ] Quarto document loads pre-computed data
- [ ] Total computation time < 6 hours

**Story Points:** 8  
**Priority:** High  
**Labels:** backend, deployment, phase-1

---

#### US-503: GitHub Pages Deployment
**As a** developer  
**I want to** deploy the Quarto site to GitHub Pages  
**So that** users can access it online  

**Acceptance Criteria:**
- [ ] GitHub Actions workflow builds Quarto site
- [ ] Publishes to `gh-pages` branch
- [ ] Site accessible at custom URL
- [ ] Updates automatically on push to main

**Story Points:** 5  
**Priority:** High  
**Labels:** deployment, devops, phase-1

---

#### US-504: Documentation & README
**As a** user/developer  
**I want to** understand how to use and contribute to the project  
**So that** I can explore routes or add new cities  

**Acceptance Criteria:**
- [ ] README.md with project description, features, usage instructions
- [ ] Data schema documentation
- [ ] Developer setup guide
- [ ] Contribution guidelines
- [ ] License file

**Story Points:** 5  
**Priority:** Medium  
**Labels:** documentation, phase-1

---

### Epic 6: Testing & Validation

#### US-601: Unit Tests for Graph Builder
**As a** developer  
**I want to** ensure graph construction is correct  
**So that** downstream algorithms work properly  

**Acceptance Criteria:**
- [ ] Test CSV parsing
- [ ] Test graph connectivity
- [ ] Test edge weight assignment
- [ ] Test multi-line station splitting
- [ ] Achieve > 90% code coverage

**Story Points:** 5  
**Priority:** Medium  
**Labels:** testing, phase-1

---

#### US-602: Algorithm Correctness Tests
**As a** developer  
**I want to** validate TSP algorithms produce valid tours  
**So that** I know solutions are correct  

**Acceptance Criteria:**
- [ ] Test on small known graphs (< 10 nodes)
- [ ] Verify tour visits each node exactly once
- [ ] Verify tour returns to starting node
- [ ] Compare against known optimal solutions
- [ ] Test edge cases (disconnected nodes, single node)

**Story Points:** 8  
**Priority:** High  
**Labels:** testing, algorithm, phase-1

---

#### US-603: End-to-End Workflow Test
**As a** developer  
**I want to** test the full pipeline from data to visualization  
**So that** I catch integration issues  

**Acceptance Criteria:**
- [ ] Automated test runs full workflow
- [ ] Verifies output files generated
- [ ] Checks visualization renders
- [ ] Runs in CI/CD pipeline

**Story Points:** 8  
**Priority:** Medium  
**Labels:** testing, integration, phase-1

---

### Epic 7: Future Enhancements (Phase 2)

#### US-701: Schedule Integration
**As a** user  
**I want to** account for real train schedules and wait times  
**So that** routes reflect actual feasible journeys  

**Acceptance Criteria:**
- TBD (Phase 2)

**Story Points:** 21  
**Priority:** Low  
**Labels:** phase-2, enhancement

---

#### US-702: Multi-City Support
**As a** user  
**I want to** solve TSP for other cities' metro networks  
**So that** I can explore different systems  

**Acceptance Criteria:**
- TBD (Phase 2)

**Story Points:** 21  
**Priority:** Low  
**Labels:** phase-2, enhancement

---

#### US-703: OpenStreetMap Automation
**As a** developer  
**I want to** automatically fetch metro network data from OSM  
**So that** I don't have to manually collect data for new cities  

**Acceptance Criteria:**
- TBD (Phase 2)

**Story Points:** 13  
**Priority:** Low  
**Labels:** phase-2, automation

---

#### US-704: Non-Circular Routes
**As a** user  
**I want to** generate routes that don't return to the start  
**So that** I have more flexibility in planning  

**Acceptance Criteria:**
- TBD (Phase 2)

**Story Points:** 8  
**Priority:** Low  
**Labels:** phase-2, enhancement

---

## 6. Development Roadmap

### Phase 1: MVP (Core TSP Solver + Visualization)
**Duration:** 6-8 weeks  
**Epics:** 1, 2, 3, 4, 5, 6

**Milestones:**
- **M1 (Week 2):** Data collection complete, graph builder working
- **M2 (Week 4):** At least 2 TSP algorithms implemented and tested
- **M3 (Week 6):** Visualization prototype functional
- **M4 (Week 8):** Quarto site deployed to GitHub Pages

### Phase 2: Enhancements (Schedules, Multi-City)
**Duration:** TBD  
**Epics:** 7

**Milestones:**
- TBD based on Phase 1 learnings

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data collection takes longer than expected | Medium | High | Start with subset (1-2 lines) for prototyping |
| TSP computation too slow for 189 nodes | Medium | High | Pre-compute all routes; evaluate approximation algorithms |
| Visualization library doesn't integrate well with Quarto | Low | Medium | Early PoC with top candidates; fallback to simpler option |
| Network topology more complex than anticipated | Low | Medium | Flexible graph model; iterative refinement |
| User interest lower than expected | Medium | Low | Focus on learning goals; document for portfolio |

---

## 8. Open Questions & Decisions Needed

### Q1: Visualization Library Choice
**Decision Point:** After US-401 research spike  
**Options:** Plotly, Folium, Observable.js  
**Decision Maker:** Developer (you)

### Q2: Pre-computation vs. Client-Side Computation
**Decision Point:** After initial algorithm benchmarking  
**Criteria:** If computation < 30s, consider PyScript; else pre-compute  
**Decision Maker:** Developer (you)

### Q3: Multi-Line Station Modeling Granularity
**Decision Point:** During graph builder implementation  
**Options:** Single node per station vs. node per platform  
**Decision Maker:** Developer (you)  
**Recommendation:** Start with node per platform, add config flag to simplify

### Q4: Data Collection Strategy
**Decision Point:** Before US-102  
**Options:** Full manual entry vs. API-assisted  
**Decision Maker:** Developer (you)  
**Recommendation:** Hybrid approach (schedule manual, walking API)

---

## 9. Appendices

### Appendix A: Singapore MRT Lines (as of 2025)
- North-South Line (NSL) - Red
- East-West Line (EWL) - Green
- Circle Line (CCL) - Yellow/Orange
- Downtown Line (DTL) - Blue
- Thomson-East Coast Line (TEL) - Brown
- North East Line (NEL) - Purple
- Bukit Panjang LRT (BPLRT) - Grey
- Sengkang LRT (SKLRT) - Grey
- Punggol LRT (PGLRT) - Grey

### Appendix B: Useful Resources
- **LTA DataMall:** https://datamall.lta.gov.sg/
- **Singapore MRT Map:** https://www.lta.gov.sg/content/ltagov/en/map/train.html
- **NetworkX Documentation:** https://networkx.org/
- **TSP Algorithms Overview:** https://en.wikipedia.org/wiki/Travelling_salesman_problem
- **Quarto Documentation:** https://quarto.org/

### Appendix C: Glossary
- **TSP:** Traveling Salesman Problem
- **MRT:** Mass Rapid Transit
- **LRT:** Light Rail Transit
- **Node:** A station in the graph representation
- **Edge:** A connection between two stations (train or walk)
- **Weight:** Travel time on an edge
- **Tour:** A complete route visiting all stations once and returning to start
- **Heuristic:** An algorithm that finds good (but not necessarily optimal) solutions quickly
- **2-opt:** A local search method that improves tours by swapping edges

---

**Document Status:** Draft v1.0  
**Next Review:** After Phase 1 M1  
**Owner:** Akshay R.
