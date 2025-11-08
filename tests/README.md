# Tests Directory

Unit and integration tests for the project.

## Structure

```
tests/
├── test_graph/          # Graph builder tests
├── test_solvers/        # Algorithm tests
├── test_visualization/  # Visualization tests
├── test_utils/          # Utility function tests
└── test_integration.py  # End-to-end tests
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_graph/test_builder.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

## Writing Tests

- Use `pytest` framework
- Name test files `test_*.py`
- Name test functions `test_*()`
- Use fixtures for common setup
- Mark slow tests with `@pytest.mark.slow`
- Aim for >80% code coverage

## Test Data

Small test datasets stored in `tests/fixtures/`
