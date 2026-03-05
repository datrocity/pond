# pond

`pond` is a library to keep scientists from losing their minds.

It provides storage, versioning, and lineage of research artifacts like data, tables, figures, etc.

## Development

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (Python package manager and virtualenv tool)

### Setup

1. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository and set up the development environment:
   ```bash
   git clone <repo-url>
   cd pond
   make setup
   ```

This creates a virtual environment in `.venv/` and installs all dependencies including development tools.

### Running Tests

```bash
make test
```

Run a single test:
```bash
uv run pytest tests/path/to/test_file.py::TestClass::test_method -v
```

### Linting and Type Checking

```bash
make lint
```

This runs both `flake8` for style checking and `mypy --strict` for type checking.

### Watching Tests

For development, watch tests automatically re-run on file changes:
```bash
make watch
```

### Dependencies

- **Core**: numpy, pandas, pillow, matplotlib, joblib, pyyaml
- **Optional**: GitPython (for git metadata), dask (for distributed arrays)
- **Dev**: flake8, mypy, pytest, jupyter, sphinx, yapf
