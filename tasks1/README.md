# Tasks 1: JSON Task Manager Prototype

This is the initial command-line application prototype for storing, listing, and searching tasks in a simple `tasks.json` file as required by the [2025-10-20 Mon] milestone.

## Requirements
- Python 3.7+
- No external dependencies

## Usage

Ensure you are in the `tasks1` directory.

### 1. Add a Task
```bash
python task_manager.py add "Draft the Tasks 2 SQLite refactor."
```

### 2. List All Tasks
```bash
python task_manager.py list
```

### 3. Search Tasks by Keyword
```bash
python task_manager.py search "SQLite"
```

## Features
- **Add**: Stores a new task with an auto-incremented ID
- **List**: Displays all tasks with their completion status
- **Search**: Finds tasks by substring match (case-insensitive)
- **Portable**: Works on Windows, macOS, and Linux

## Data Storage
Tasks are stored in `tasks.json` in the same directory as the script.
