# Tasks 2: SQLite Task Manager (Iteration)

This is an iteration on the Tasks 1 prototype, migrated from JSON to SQLite for better scalability and query performance, as required by the [2025-11-03 Mon] milestone.

## Requirements
- Python 3.7+
- No external dependencies (uses Python's built-in `sqlite3`)

## Usage

Ensure you are in the `tasks2` directory.

### 1. Add a Task
```bash
python task_manager.py add "Implement search with SQL LIKE"
```

### 2. List All Tasks
```bash
python task_manager.py list
```

### 3. Search Tasks by Keyword
```bash
python task_manager.py search "SQL"
```

## Features
- **SQLite storage**: Replaces JSON with a relational database
- **Auto-increment IDs**: Uses SQLite's `PRIMARY KEY AUTOINCREMENT`
- **Efficient search**: SQL `LIKE` queries for substring matching
- **Schema management**: Automatically creates the `tasks` table on first run
- **Portable**: Works on Windows, macOS, and Linux

## Data Storage
Tasks are stored in `tasks.db` (SQLite database) in the same directory as the script.

## Improvements over Tasks 1
- Better scalability for large task lists
- More efficient searching with indexed queries
- Foundation for advanced features (joins, aggregations, etc.)
