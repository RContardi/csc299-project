# Tasks: Task Management System

**Input**: Design documents from `/specs/001-task-manager/`
**Prerequisites**: plan.md, spec.md, data-model.md

## Phase 1: Project Setup

- [ ] **T001** Create project directory structure (task_manager/, tests/)
- [ ] **T002** Create `task_manager/__init__.py` with version info
- [ ] **T003** Create `pyproject.toml` with project metadata and entry point
- [ ] **T004** Create basic README.md with installation and usage instructions

## Phase 2: Data Model Implementation

- [ ] **T005** Implement `task_manager/models.py` with Task dataclass
- [ ] **T006** Add Task validation methods (title length, description length)
- [ ] **T007** Add Task `from_db_row()` class method
- [ ] **T008** Add Task `to_dict()` method
- [ ] **T009** Add Task `status` property for display

## Phase 3: Database Layer

- [ ] **T010** Create `task_manager/db.py` with database connection function
- [ ] **T011** Implement `init_db()` to create tasks table with schema
- [ ] **T012** Implement `add_task(conn, title, description)` function
- [ ] **T013** Implement `list_tasks(conn)` function returning Task objects
- [ ] **T014** Implement `get_task(conn, task_id)` function
- [ ] **T015** Implement `complete_task(conn, task_id)` function
- [ ] **T016** Implement `search_tasks(conn, keyword)` function
- [ ] **T017** Add error handling for database operations

## Phase 4: CLI Interface

- [ ] **T018** Create `task_manager/cli.py` with argparse setup
- [ ] **T019** Implement `add` command handler
- [ ] **T020** Implement `list` command handler with formatted output
- [ ] **T021** Implement `complete` command handler
- [ ] **T022** Implement `search` command handler
- [ ] **T023** Add help messages for all commands
- [ ] **T024** Add error handling and user-friendly messages

## Phase 5: Main Entry Point

- [ ] **T025** Create `main.py` that initializes database
- [ ] **T026** Integrate CLI parser with main entry point
- [ ] **T027** Add command routing to appropriate handlers
- [ ] **T028** Test manual execution with `python main.py`

## Phase 6: Testing

- [ ] **T029** Create `tests/__init__.py`
- [ ] **T030** Write `tests/test_models.py` with Task validation tests
- [ ] **T031** Write `tests/test_db.py` with database operation tests
- [ ] **T032** Write `tests/test_cli.py` with CLI command tests
- [ ] **T033** Add integration test for complete workflow
- [ ] **T034** Run all tests and achieve >80% coverage

## Phase 7: Installation & Documentation

- [ ] **T035** Configure pyproject.toml with console_scripts entry point
- [ ] **T036** Create install.ps1 for Windows installation
- [ ] **T037** Test installation with `pip install -e .`
- [ ] **T038** Verify `task-manager` command works after install
- [ ] **T039** Update README with complete usage examples
- [ ] **T040** Add docstrings to all public functions

## Phase 8: Polish

- [ ] **T041** Format code with black or autopep8
- [ ] **T042** Run pylint and fix warnings
- [ ] **T043** Add .gitignore for tasks.db and __pycache__
- [ ] **T044** Create example tasks for demonstration
- [ ] **T045** Final testing on clean environment

## Dependencies

```
T001-T004 (Setup) → T005-T009 (Models)
T005-T009 (Models) → T010-T017 (Database)
T010-T017 (Database) → T018-T024 (CLI)
T018-T024 (CLI) → T025-T028 (Main)
T001-T028 (Core) → T029-T034 (Tests)
T001-T034 (All Core) → T035-T040 (Install)
T001-T040 (Complete) → T041-T045 (Polish)
```

## Verification

After completion:
- [ ] All commands execute without errors
- [ ] Tasks persist across restarts
- [ ] All tests pass
- [ ] Installation successful
- [ ] README is complete and accurate
