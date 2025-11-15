"""Pytest configuration ensuring project root is on sys.path.

This allows tests to import the `src` package without requiring an
editable install or manual PYTHONPATH export. Keeps environment reuse
simple for the existing `tsp-izer` conda env.
"""

import sys
from pathlib import Path

# Project root (parent of tests directory)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
