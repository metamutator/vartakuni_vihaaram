# Examples

This directory contains example scripts demonstrating how to use the TSP solvers.

## Available Examples

### `nearest_neighbor_output_explained.py`

**Purpose:** Understand the output from `nearest_neighbor_tsp()`

This script demonstrates what you get when running:
```python
nn_path = nearest_neighbor_tsp(G, start_station='BP10')
```

**Usage:**
```bash
python examples/nearest_neighbor_output_explained.py
```

**What it shows:**
- The structure of the return value (tuple with 2 elements)
- How to interpret the tour (list of station IDs)
- How to interpret the cost (total travel time in minutes)
- How to properly unpack and use the result
- Examples of accessing station information

**Related Resources:**
- **Detailed Guide:** `docs/understanding_nearest_neighbor_output.md`
- **Interactive Notebook:** `notebooks/understanding_nearest_neighbor_output.ipynb`

## Running Examples

All examples can be run from the project root directory:

```bash
# From the project root
cd /path/to/vartakuni_vihaaram
python examples/nearest_neighbor_output_explained.py
```

## Adding New Examples

When adding new examples:
1. Create a descriptive filename (e.g., `algorithm_name_demo.py`)
2. Include a docstring explaining the purpose
3. Add usage instructions in this README
4. Make sure the script is self-contained and runs from project root
5. Add helpful comments and output messages

## Example Template

```python
"""
Example: [Brief Description]
============================

[Longer explanation of what this example demonstrates]

For more information, see: [related docs]
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import load_default_graph
from src.solvers import your_solver

def main():
    print("=" * 80)
    print("Example: [Title]")
    print("=" * 80)
    print()
    
    # Your example code here
    G = load_default_graph()
    
    # ... demonstrate the feature ...
    
    print("✓ Example completed!")

if __name__ == "__main__":
    main()
```
