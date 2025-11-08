# Vartakuni Vihāram (వర్తకుని విహారం): A TSP Solver for Metro Networks

**Travel every station, optimize the journey**

A Traveling Salesman Problem (TSP) solver for metro networks that generates optimal routes visiting all stations in a city's transit system. Currently focused on Singapore's MRT/LRT network.

## Project Goal

Given any starting station in a metro network, calculate the shortest possible route (by time) that visits every station exactly once and returns to the starting point.

## Features (Planned)

- **Multiple TSP Algorithms**: Nearest Neighbor, 2-opt, Simulated Annealing, Genetic Algorithm
- **Interactive Visualization**: Metro map with route overlay
- **User-Selectable Start Points**: Choose any station as your starting point
- **Walking Network Support**: Model transfers between lines and nearby stations
- **Static Website**: Deployed via Quarto to GitHub Pages

## Current Status

**Phase 1: MVP Development**
- [x] Project specification complete
- [ ] Data collection (Singapore MRT/LRT)
- [ ] Graph builder implementation
- [ ] TSP algorithms
- [ ] Visualization
- [ ] Quarto site deployment

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

*(Coming soon after implementation)*

```python
from src.graph.builder import build_network
from src.solvers.simulated_annealing import solve_tsp

# Load Singapore MRT network
network = build_network("data/processed/singapore_mrt.json")

# Solve TSP starting from Raffles Place
route = solve_tsp(network, start_station="RP_NSL")

# Visualize
from src.visualization.map import plot_route
plot_route(network, route)
```

## Supported Cities

- **Singapore** (MRT/LRT) - In Progress
- *(Future cities TBD)*

## Documentation

- [Project Specification](PROJECT_SPEC.md) - Comprehensive functional and technical specs
- [Data Schema](docs/data_schema.md) - *(Coming soon)*
- [Algorithm Documentation](docs/algorithms.md) - *(Coming soon)*

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
