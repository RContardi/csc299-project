# GitHub Copilot Instructions for Task Management System

## Project Context

This is a **spec-kit driven task management system** built using Python 3.8+ with SQLite for persistence. All development follows the specification documents in `specs/001-task-manager/` and adheres to principles in `.specify/memory/constitution.md`.

## Architecture

```
TaskManager/
├── task_manager/     # Core package
│   ├── models.py     # Task dataclass with validation
│   ├── db.py         # Database operations
│   └── cli.py        # Command-line interface
├── tests/            # Unit tests (>80% coverage required)
├── main.py           # Entry point
└── gui.py            # Optional GUI interface
```

### Layer Responsibilities

**Models Layer** (`models.py`)
- Task dataclass with fields: id, title, description, completed, created_at
- Validation: title ≤200 chars, description ≤1000 chars
- Serialization methods: `from_db_row()`, `to_dict()`

**Database Layer** (`db.py`)
- SQLite3 connection management
- Functions: `init_db()`, `add_task()`, `list_tasks()`, `get_task()`, `complete_task()`, `search_tasks()`
- Use context managers for connections
- Proper error handling

**CLI Layer** (`cli.py`)
- Argparse command parser
- Commands: add, list, complete, search, say
- Formatted output for user display
- Error messages with helpful suggestions

## Development Guidelines

### Code Style
- **PEP 8** compliance mandatory
- **Type hints** for all function signatures
- **Docstrings** for all public functions (Google style)
- **Comments** for complex logic only
- **Max line length**: 100 characters
- **Naming**: snake_case for functions/variables, PascalCase for classes

### Testing Requirements (Constitutional)
- **TDD mandatory**: Write tests BEFORE implementation
- **Coverage**: >80% required for all modules
- **Test files**: Mirror source structure in `tests/`
- **Assertions**: Use unittest.TestCase methods
- **Isolation**: Each test must be independent

### Database Operations
- **Always use context managers** for connections:
  ```python
  with sqlite3.connect("tasks.db") as conn:
      cursor = conn.cursor()
      # operations here
  ```
- **Parameterized queries** to prevent SQL injection
- **Error handling** for constraint violations
- **Commit explicitly** after write operations

### Command-Line Interface
- **Help text** for all commands and arguments
- **Exit codes**: 0 for success, 1 for user error, 2 for system error
- **Output format**: Clear, concise, user-friendly
- **Error messages**: Actionable suggestions

## Specification References

When generating code, reference requirements:

**Functional Requirements** (from `specs/001-task-manager/spec.md`):
- FR-001: Add tasks with title and optional description
- FR-002: Assign unique sequential IDs
- FR-003: Persist tasks in SQLite
- FR-004: List all tasks with status
- FR-005: Mark tasks complete
- FR-006: Search tasks by keyword
- FR-007: Display formatted task list
- FR-008: Distinguish pending vs completed
- FR-009: Clear error messages
- FR-010: Command-line access

**Non-Functional Requirements**:
- NFR-001: Operations complete within 1 second
- NFR-002: Database in local directory
- NFR-003: PEP 8 compliance
- NFR-004: Complete docstrings
- NFR-005: Installable CLI tool

## Common Patterns

### Adding a New Command

1. **Update spec** (if new requirement)
2. **Write test** in `tests/test_cli.py`:
   ```python
   def test_new_command(self):
       """Test new command functionality."""
       # Arrange
       # Act
       # Assert
   ```
3. **Add CLI handler** in `cli.py`:
   ```python
   def handle_new_command(args):
       """Handle new command.
       
       Args:
           args: Parsed command-line arguments
           
       Returns:
           int: Exit code (0=success, 1=error)
       """
       pass
   ```
4. **Update argparse** subparser
5. **Update README** with usage example

### Adding Database Function

1. **Update data-model.md** if schema changes
2. **Write test** in `tests/test_db.py`
3. **Implement function** with proper error handling:
   ```python
   def new_operation(conn, param: str) -> Optional[Task]:
       """Perform new database operation.
       
       Args:
           conn: SQLite connection object
           param: Description of parameter
           
       Returns:
           Task object if found, None otherwise
           
       Raises:
           sqlite3.IntegrityError: If constraint violated
       """
       try:
           cursor = conn.cursor()
           cursor.execute("SELECT ...", (param,))
           # Process results
       except sqlite3.Error as e:
           raise
   ```

## Technology Constraints (from Constitution)

✅ **Allowed**:
- Python standard library modules
- SQLite3 (built-in)
- argparse (built-in)
- unittest (built-in)

❌ **Not Allowed** (without spec amendment):
- External dependencies (requests, flask, etc.)
- ORM frameworks (SQLAlchemy, etc.)
- CLI frameworks (click, typer, etc.)
- Web frameworks
- Cloud services

## Quality Checklist

Before suggesting code, verify:
- [ ] Requirement traced to spec.md
- [ ] Test written and fails
- [ ] Type hints included
- [ ] Docstring present (Google style)
- [ ] Error handling appropriate
- [ ] PEP 8 compliant
- [ ] No external dependencies
- [ ] Context manager for DB connections
- [ ] Exit code correct for CLI commands

## Helpful Commands

```powershell
# Run tests
python -m unittest discover -v

# Run specific test file
python -m unittest tests.test_cli -v

# Install in development mode
python -m pip install -e .

# Run task manager
task-manager add "Example task"
task-manager list

# Check PEP 8 compliance
python -m pylint task_manager/
```

## AI Assistant Behavior

When assisting with this project:
1. **Always check specs first** - Reference requirement numbers
2. **Suggest tests before implementation** - TDD is constitutional
3. **Keep it simple** - YAGNI principle applies
4. **Follow existing patterns** - Consistency matters
5. **Update docs** - README and docstrings alongside code
6. **Validate against constitution** - No violations without justification

## Quick Reference

**Main entry point**: `main.py:main()`  
**Database file**: `tasks.db` (auto-created)  
**Test command**: `python -m unittest discover -v`  
**Install command**: `python -m pip install -e .`  
**CLI command**: `task-manager [add|list|complete|search|say]`

---

*Last Updated: 2025-11-24*  
*Spec-Kit Version: 1.0.0*  
*Project Phase: Implementation Complete*
