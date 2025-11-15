#!/bin/bash

# Script to create GitHub issues using GitHub CLI
# Prerequisite: Install GitHub CLI (https://cli.github.com/)
# Usage: ./scripts/create_github_issues.sh

set -e

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

echo 'Creating GitHub issues...'
echo ""

echo 'Creating US-101: US-101: Station Data Collection...'
gh issue create \
  --title "US-101: Station Data Collection" \
  --body "**User Story**

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
" \
  --label "data-collection,phase-1,epic-1,priority-high"
echo ""

echo 'Creating US-102: US-102: Inter-Station Travel Time Data...'
gh issue create \
  --title "US-102: Inter-Station Travel Time Data" \
  --body "**User Story**

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
" \
  --label "data-collection,phase-1,epic-1,priority-high"
echo ""

echo 'Creating US-103: US-103: Walking Network Data...'
gh issue create \
  --title "US-103: Walking Network Data" \
  --body "**User Story**

As a **developer**  
I want to **identify and measure walking connections between stations/platforms**  
So that **users can transfer between lines and nearby stations realistically**

**Acceptance Criteria**

- [ ] Transfer times within multi-line stations recorded (platform-to-platform)
- [ ] Walking connections between nearby stations identified (< 10 min walk)
- [ ] Walking times sourced from mapping APIs or manual measurement
- [ ] Connection type labeled as \"walk_transfer\" or \"walk_between_stations\"

**Story Points:** 8  
**Priority:** Medium
" \
  --label "data-collection,phase-1,epic-1,priority-medium"
echo ""

echo 'Creating US-104: US-104: Line Metadata...'
gh issue create \
  --title "US-104: Line Metadata" \
  --body "**User Story**

As a **developer**  
I want to **document metadata for each MRT/LRT line**  
So that **visualizations can display correct colors and labels**

**Acceptance Criteria**

- [ ] CSV with line codes, full names, official color codes, line type
- [ ] Covers all MRT and LRT lines
- [ ] Colors match official LTA branding

**Story Points:** 2  
**Priority:** Low
" \
  --label "data-collection,phase-1,epic-1,priority-low"
echo ""

echo 'Creating US-201: US-201: Graph Builder Module...'
gh issue create \
  --title "US-201: Graph Builder Module" \
  --body "**User Story**

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
" \
  --label "backend,graph,phase-1,epic-2,priority-high"
echo ""

echo 'Creating US-202: US-202: Data Validation Pipeline...'
gh issue create \
  --title "US-202: Data Validation Pipeline" \
  --body "**User Story**

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
" \
  --label "backend,validation,phase-1,epic-2,priority-medium"
echo ""

echo 'Creating US-301: US-301: Nearest Neighbor Heuristic...'
gh issue create \
  --title "US-301: Nearest Neighbor Heuristic" \
  --body "**User Story**

As a **developer**  
I want to **implement a Nearest Neighbor TSP algorithm**  
So that **I can quickly generate a baseline solution**

**Acceptance Criteria**



**Story Points:** 5  
**Priority:** High
" \
  --label "algorithm,phase-1,epic-3,priority-high"
echo ""

echo 'Creating US-302: US-302: 2-Opt Local Search...'
gh issue create \
  --title "US-302: 2-Opt Local Search" \
  --body "**User Story**

As a **developer**  
I want to **implement 2-opt improvement on TSP tours**  
So that **I can optimize solutions from constructive heuristics**

**Acceptance Criteria**



**Story Points:** 8  
**Priority:** High
" \
  --label "algorithm,phase-1,epic-3,priority-high"
echo ""

echo 'Creating US-303: US-303: Simulated Annealing Solver...'
gh issue create \
  --title "US-303: Simulated Annealing Solver" \
  --body "**User Story**

As a **developer**  
I want to **implement Simulated Annealing for TSP**  
So that **I can explore more of the solution space**

**Acceptance Criteria**



**Story Points:** 13  
**Priority:** Medium
" \
  --label "algorithm,phase-1,epic-3,priority-medium"
echo ""

echo 'Creating US-304: US-304: Genetic Algorithm Solver (Optional)...'
gh issue create \
  --title "US-304: Genetic Algorithm Solver (Optional)" \
  --body "**User Story**

As a **developer**  
I want to **implement a Genetic Algorithm for TSP**  
So that **I can compare population-based optimization**

**Acceptance Criteria**



**Story Points:** 13  
**Priority:** Low
" \
  --label "algorithm,phase-1,optional,epic-3,priority-low"
echo ""

echo 'Creating US-305: US-305: Algorithm Comparison Framework...'
gh issue create \
  --title "US-305: Algorithm Comparison Framework" \
  --body "**User Story**

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
" \
  --label "algorithm,analysis,phase-1,epic-3,priority-medium"
echo ""

echo 'Creating US-401: US-401: Research Visualization Libraries...'
gh issue create \
  --title "US-401: Research Visualization Libraries" \
  --body "**User Story**

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
" \
  --label "visualization,research,phase-1,epic-4,priority-high"
echo ""

echo 'Creating US-402: US-402: Network Map Visualization...'
gh issue create \
  --title "US-402: Network Map Visualization" \
  --body "**User Story**

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
" \
  --label "visualization,frontend,phase-1,epic-4,priority-high"
echo ""

echo 'Creating US-403: US-403: Route Overlay Visualization...'
gh issue create \
  --title "US-403: Route Overlay Visualization" \
  --body "**User Story**

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
" \
  --label "visualization,frontend,phase-1,epic-4,priority-high"
echo ""

echo 'Creating US-404: US-404: Route Details Panel...'
gh issue create \
  --title "US-404: Route Details Panel" \
  --body "**User Story**

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
" \
  --label "visualization,frontend,phase-1,epic-4,priority-medium"
echo ""

echo 'Creating US-405: US-405: Starting Station Selector...'
gh issue create \
  --title "US-405: Starting Station Selector" \
  --body "**User Story**

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
" \
  --label "visualization,frontend,interaction,phase-1,epic-4,priority-high"
echo ""

echo 'Creating US-501: US-501: Quarto Document Structure...'
gh issue create \
  --title "US-501: Quarto Document Structure" \
  --body "**User Story**

As a **developer**  
I want to **create a Quarto document that integrates Python and visualizations**  
So that **I can generate a cohesive website**

**Acceptance Criteria**

- [ ] \`.qmd\` file with sections: Introduction, Methodology, Interactive Map, Results
- [ ] Python code cells execute graph building and TSP solving
- [ ] Visualizations embedded correctly
- [ ] Renders to HTML without errors

**Story Points:** 8  
**Priority:** High
" \
  --label "quarto,deployment,phase-1,epic-5,priority-high"
echo ""

echo 'Creating US-502: US-502: Pre-computation Pipeline...'
gh issue create \
  --title "US-502: Pre-computation Pipeline" \
  --body "**User Story**

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
" \
  --label "backend,deployment,phase-1,epic-5,priority-high"
echo ""

echo 'Creating US-503: US-503: GitHub Pages Deployment...'
gh issue create \
  --title "US-503: GitHub Pages Deployment" \
  --body "**User Story**

As a **developer**  
I want to **deploy the Quarto site to GitHub Pages**  
So that **users can access it online**

**Acceptance Criteria**

- [ ] GitHub Actions workflow builds Quarto site
- [ ] Publishes to \`gh-pages\` branch
- [ ] Site accessible at custom URL
- [ ] Updates automatically on push to main

**Story Points:** 5  
**Priority:** High
" \
  --label "deployment,devops,phase-1,epic-5,priority-high"
echo ""

echo 'Creating US-504: US-504: Documentation & README...'
gh issue create \
  --title "US-504: Documentation & README" \
  --body "**User Story**

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
" \
  --label "documentation,phase-1,epic-5,priority-medium"
echo ""

echo 'Creating US-601: US-601: Unit Tests for Graph Builder...'
gh issue create \
  --title "US-601: Unit Tests for Graph Builder" \
  --body "**User Story**

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
" \
  --label "testing,phase-1,epic-6,priority-medium"
echo ""

echo 'Creating US-602: US-602: Algorithm Correctness Tests...'
gh issue create \
  --title "US-602: Algorithm Correctness Tests" \
  --body "**User Story**

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
" \
  --label "testing,algorithm,phase-1,epic-6,priority-high"
echo ""

echo 'Creating US-603: US-603: End-to-End Workflow Test...'
gh issue create \
  --title "US-603: End-to-End Workflow Test" \
  --body "**User Story**

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
" \
  --label "testing,integration,phase-1,epic-6,priority-medium"
echo ""

echo 'Creating US-701: US-701: Schedule Integration...'
gh issue create \
  --title "US-701: Schedule Integration" \
  --body "**User Story**

As a **user**  
I want to **account for real train schedules and wait times**  
So that **routes reflect actual feasible journeys**

**Acceptance Criteria**



**Story Points:** 21  
**Priority:** Low
" \
  --label "phase-2,enhancement,epic-7,priority-low"
echo ""

echo 'Creating US-702: US-702: Multi-City Support...'
gh issue create \
  --title "US-702: Multi-City Support" \
  --body "**User Story**

As a **user**  
I want to **solve TSP for other cities' metro networks**  
So that **I can explore different systems**

**Acceptance Criteria**



**Story Points:** 21  
**Priority:** Low
" \
  --label "phase-2,enhancement,epic-7,priority-low"
echo ""

echo 'Creating US-703: US-703: OpenStreetMap Automation...'
gh issue create \
  --title "US-703: OpenStreetMap Automation" \
  --body "**User Story**

As a **developer**  
I want to **automatically fetch metro network data from OSM**  
So that **I don't have to manually collect data for new cities**

**Acceptance Criteria**



**Story Points:** 13  
**Priority:** Low
" \
  --label "phase-2,automation,epic-7,priority-low"
echo ""

echo 'Creating US-704: US-704: Non-Circular Routes...'
gh issue create \
  --title "US-704: Non-Circular Routes" \
  --body "**User Story**

As a **user**  
I want to **generate routes that don't return to the start**  
So that **I have more flexibility in planning**

**Acceptance Criteria**



**Story Points:** 8  
**Priority:** Low
" \
  --label "phase-2,enhancement,epic-7,priority-low"
echo ""

echo ""
echo "✓ All issues created!"
