# Tasks 3: PKMS/Task Manager with Pytest

This package integrates the task manager from Tasks 2 with a proper pytest test suite, as required by the [2025-11-05 Wed] milestone.

## Requirements
- Python 3.7+
- `uv` package manager
- `pytest` (installed as dev dependency)

## Setup

This package was created with:
```bash
uv init tasks3 --vcs none --package tasks3
cd tasks3
uv add --dev pytest
```

## Running the Application

From the `tasks3` directory:
```bash
uv run tasks3 add "Write unit tests for search"
uv run tasks3 list
uv run tasks3 search "tests"
```

## Running Tests

Run all tests:
```bash
uv run pytest
```

Run with verbose output:
```bash
uv run pytest -v
```

Run specific test file:
```bash
uv run pytest tests/test_inc.py
```

## Test Coverage

The test suite includes:
1. `test_inc()` - Tests the `inc` function (required example)
2. `test_add_task_creates_entry()` - Verifies task creation in SQLite
3. `test_database_table_exists_and_is_clean()` - Validates schema integrity

All tests use an in-memory SQLite database (`:memory:`) for isolation.

## Features
- **pytest integration**: Comprehensive test suite with fixtures
- **In-memory testing**: Fast, isolated tests using `:memory:` databases
- **uv package management**: Modern Python packaging with `pyproject.toml`
- **Main entrypoint**: Runnable via `uv run tasks3`
- **Portable**: Works on Windows, macOS, and Linux

## Project Structure
```
tasks3/
├── src/
│   └── __init__.py      # Main application code + inc() function
├── tests/
│   ├── test_inc.py      # Test for inc() function
│   └── test_tasks.py    # Tests for task management
├── pyproject.toml       # Package configuration
└── README.md            # This file
```
