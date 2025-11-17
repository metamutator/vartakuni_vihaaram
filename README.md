# Vartakuni Vihāram (వర్తకుని విహారం): A TSP Solver for Metro Networks

**Travel every station, optimize the journey**

A Traveling Salesman Problem (TSP) solver for metro networks that generates optimal routes visiting all stations in a city's transit system. Currently focused on Singapore's MRT/LRT network.

## Project Goal

Given any starting station in a metro network, calculate the shortest possible route (by time) that visits every station exactly once and returns to the starting point.

## Features (Planned)

- **Multiple TSP Algorithms**: Nearest Neighbor, 2-opt, Simulated Annealing, Genetic Algorithm (all operate on metric closure)
- **Interactive Visualization**: Metro map with route overlay
- **User-Selectable Start Points**: Choose any station as your starting point
- **Walking Network Support**: Model transfers between lines and nearby stations
- **Static Website**: Deployed via Quarto to GitHub Pages

## Current Status

**Phase 1: MVP Development**
- [x] Project specification complete
- [x] **Epic 1: Data Foundation** - Singapore MRT/LRT network data (214 stations, 277 connections)
- [x] **Epic 2: Graph Infrastructure** - NetworkX graph builder with validation 
- [x] **Epic 3: TSP algorithms**
- [ ] Visualization (Epic 4, 8) - _Ongoing_ 
- [ ] Website site deployment (Epic 5)

### Completed Milestones

**Epic 1: Data Foundation** 
- [US-101](https://github.com/metamutator/vartakuni_vihaaram/issues/1): Station data collection (214 entries, 181 unique stations)
- [US-102](https://github.com/metamutator/vartakuni_vihaaram/issues/2): Inter-station travel times (199 train connections, estimated)
- [US-103](https://github.com/metamutator/vartakuni_vihaaram/issues/3): Walking network data (78 walking connections)
- [US-104](https://github.com/metamutator/vartakuni_vihaaram/issues/4): Line metadata (15 MRT/LRT lines with official colours)
- [US-106](https://github.com/metamutator/vartakuni_vihaaram/issues/31): Fixed disconnected LRT loops and TE extension
- [US-107](https://github.com/metamutator/vartakuni_vihaaram/issues/32): Travel Time Calibration Based on Field Measurements 

**Epic 2: Graph Infrastructure** 
- [US-201](https://github.com/metamutator/vartakuni_vihaaram/issues/5): Graph builder module 
- [US-202](https://github.com/metamutator/vartakuni_vihaaram/issues/6): Data validation pipeline

**Epic 3: Graph Solvers** 
- [US-301](https://github.com/metamutator/vartakuni_vihaaram/issues/7): Nearest Neighbor Heuristic
- [US-302](https://github.com/metamutator/vartakuni_vihaaram/issues/8): 2-Opt Local Search
- [US-303](https://github.com/metamutator/vartakuni_vihaaram/issues/9): Simulated Annealing Solver
- [US-304](https://github.com/metamutator/vartakuni_vihaaram/issues/10): Genetic Algorithm Solver
- [US-305](https://github.com/metamutator/vartakuni_vihaaram/issues/11): Algorithm Comparison Framework

**Epic ~4~ 8: Visualisation** (_Ongoing_) 
Exploring various ways in which the generated tours can be visualised on an MRT map. Stay tuned!

### Current Findings
We constructed a graph out of the Singapore MRT/LRT system, and ran various algorithms to find the shortest path. 

**Our current finding**: The Nearest Neighbour algorithm with 2-Opt search has given us the best set of results. See the corresponding [Jupyter notebook](https://github.com/metamutator/vartakuni_vihaaram/blob/main/notebooks/epic_3_tsp_solvers_demo.ipynb) for details. 

The fastest path around Singapore involves starting at Harbourfront MRT at travelling through a defined path to return to the station. That will take you roughly 585 minutes. Verifying the results now, stay tuned!

## Project Structure

```
vartakuni_vihaaram/
├── data/
│   ├── raw/              # Original data files (stations, connections, lines)
│   ├── processed/        # Cleaned and validated network data
│   └── solutions/        # Pre-computed optimal routes
├── src/
│   ├── graph/            # Network graph construction and validation
│   ├── solvers/          # TSP algorithm implementations
│   ├── visualization/    # Plotting and map generation
│   └── utils/            # Helper functions
├── notebooks/            # Jupyter notebooks for exploration
├── tests/                # Unit and integration tests
├── docs/                 # Additional documentation
├── quarto/               # Quarto website source
├── scripts/              # Utility scripts (data collection, precomputation)
├── PROJECT_SPEC.md       # Detailed project specification
└── README.md             # This file
```

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **Graph Library**: NetworkX
- **Optimization**: scipy, custom implementations
- **Visualization**: Plotly / Folium / Observable.js (TBD)
- **Website**: Quarto
- **Deployment**: GitHub Pages

## Installation

```bash
# Clone the repository
git clone https://github.com/metamutator/vartakuni_vihaaram.git
cd vartakuni_vihaaram

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Build the Singapore MRT/LRT Graph

```python
from pathlib import Path
from src.graph.builder import build_singapore_metro_graph

# Build the network graph from data files
data_dir = Path('data/raw')
graph = build_singapore_metro_graph(data_dir)

# View graph statistics
print(f"Stations: {graph.number_of_nodes()}")
print(f"Connections: {graph.number_of_edges()}")
```

### Use the Graph Builder API

```python
from src.graph import MetroGraphBuilder

# Create builder instance
builder = MetroGraphBuilder()

# Build graph from CSV files
graph = builder.build_graph(
    stations_csv=Path('data/raw/stations.csv'),
    connections_csv=Path('data/raw/connections.csv'),
    lines_csv=Path('data/raw/lines.csv')
)

# Validate connectivity
is_connected, components = builder.validate_connectivity()
print(f"Graph connected: {is_connected}")

# Get shortest path between stations
path, travel_time = builder.get_shortest_path('NS1', 'EW13')
print(f"Route: {' → '.join(path)}")
print(f"Travel time: {travel_time:.2f} minutes")

# Get graph statistics
stats = builder.get_graph_stats()
print(f"Network diameter: {stats['diameter']} stations")
```

- **TSP Solvers:** Coming in Epic 3
- **Visualization:** Coming in Epic 4

### Metric Closure Design (Epic 3)

All TSP solvers use the **metric closure** of the transit graph: a complete graph where each edge weight equals the shortest-path travel time between two station nodes (including train travel and walking transfers). This provides:
- Guaranteed distance between every pair of stations (no dead-ends / leaf branch pitfalls)
- Consistent cost calculations across heuristics and metaheuristics
- Better comparability of algorithm performance

The reported tour cost therefore represents a theoretical lower bound under assumed transfer times, not necessarily a physically traversable single continuous ride without revisits. Future work may add a "strict traversal" mode using only original edges.

## Supported Cities

- **Singapore** (MRT/LRT) - ✅ Data Complete, Graph Builder Ready
  - 214 stations (181 unique locations)
  - 277 connections (train + walking)
  - 15 lines (8 MRT + 7 LRT)
  - **Note:** TE21 (Marina South) and TE22A (Founders' Memorial) stations are built but not operational - trains skip directly from TE20 to TE22
- *(Future cities TBD)*

## Documentation

- [Project Specification](PROJECT_SPEC.md) - Comprehensive functional and technical specs
- [Data README](data/README.md) - Complete data collection documentation and statistics
- [Data Source Documentation](data/raw/) - Detailed methodology for stations, connections, lines, and fixes
- [Algorithm Documentation](docs/algorithms.md) - *(Coming in Epic 3)*

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Contributing

This is currently a personal hobbyist project. Contributions, ideas, and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contact

**Akshay R.**  
Project Link: [https://github.com/metamutator/vartakuni_vihaaram](https://github.com/metamutator/vartakuni_vihaaram)

---

*"Vartakuni Vihaaram" (వర్తకుని విహారం) - Telugu for "A Seller's Journey"*
