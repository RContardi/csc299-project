# Spec-Kit Workflow Guide for Task Management System

This document explains how to use GitHub's spec-kit methodology to develop new features for the task management system.

## Table of Contents

1. [Overview](#overview)
2. [Spec-Kit Phases](#spec-kit-phases)
3. [Agent Workflow](#agent-workflow)
4. [Adding New Features](#adding-new-features)
5. [Best Practices](#best-practices)
6. [Common Scenarios](#common-scenarios)

---

## Overview

Spec-kit is a specification-driven development framework that uses AI agents to guide you through structured phases:

```
Specify → Plan → Model → Task → Implement → Validate
```

Each phase produces documentation that guides the next phase, ensuring traceability from requirements to code.

## Spec-Kit Phases

### Phase 1: Specify (speckit.specify agent)

**Purpose**: Create feature specification with user scenarios and requirements

**Input**: Natural language feature description

**Output**: `specs/NNN-feature-name/spec.md`

**Contents**:
- User scenarios with testing criteria
- Functional requirements (FR-XXX)
- Non-functional requirements (NFR-XXX)
- Success criteria
- Assumptions and out-of-scope items

**Example**:
```
Feature: "I want to add task priority levels (high, medium, low)"

Creates: specs/002-task-priorities/spec.md with:
- User Scenarios:
  - "User adds high-priority task"
  - "User filters tasks by priority"
- Requirements:
  - FR-011: Tasks have priority field (high/medium/low)
  - FR-012: List command supports --priority filter
```

### Phase 2: Plan (speckit.plan agent)

**Purpose**: Design technical architecture and implementation approach

**Input**: Feature specification from Phase 1

**Output**: `specs/NNN-feature-name/plan.md`

**Contents**:
- Technology stack decisions
- Architecture and component design
- Database schema changes
- API design
- Testing strategy
- Implementation phases

**Example**:
```
From spec.md requirements → plan.md:
- Update Task model: Add priority field (enum: HIGH, MEDIUM, LOW)
- Database: ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'MEDIUM'
- CLI: Add --priority argument to 'add' command
- CLI: Add --filter-priority argument to 'list' command
```

### Phase 3: Model (data-model updates)

**Purpose**: Define data structures and database schema

**Input**: Plan from Phase 2

**Output**: `specs/NNN-feature-name/data-model.md`

**Contents**:
- Entity definitions with fields
- Validation rules
- State transitions
- Database schema (SQL)
- Query patterns

**Example**:
```sql
-- Update Task entity
ALTER TABLE tasks ADD COLUMN priority TEXT 
  CHECK(priority IN ('HIGH', 'MEDIUM', 'LOW')) 
  DEFAULT 'MEDIUM';

CREATE INDEX idx_priority ON tasks(priority);
```

### Phase 4: Task Breakdown (speckit.tasks agent)

**Purpose**: Break implementation into discrete, testable tasks

**Input**: Plan and data model

**Output**: `specs/NNN-feature-name/tasks.md`

**Contents**:
- Numbered tasks (T001, T002, ...)
- Task dependencies
- Phase grouping (Setup, Implementation, Testing, Polish)
- Verification checklist

**Example**:
```markdown
## Phase 1: Data Model
- [ ] T001: Update models.py Task dataclass with priority field
- [ ] T002: Add priority validation (HIGH/MEDIUM/LOW only)
- [ ] T003: Update Task.from_db_row() to handle priority

## Phase 2: Database
- [ ] T004: Create migration script for priority column
- [ ] T005: Update init_db() with new schema
- [ ] T006: Update add_task() to accept priority parameter
```

### Phase 5: Implementation

**Purpose**: Build features following TDD approach

**Process**:
1. Pick next task from tasks.md
2. Write test case (RED)
3. Implement minimum code to pass (GREEN)
4. Refactor while keeping tests green
5. Mark task complete in tasks.md
6. Commit with requirement reference

**Example**:
```python
# Test first (RED)
def test_add_task_with_priority(self):
    """Test FR-011: Add task with priority."""
    task_id = add_task(self.conn, "Urgent task", "", priority="HIGH")
    task = get_task(self.conn, task_id)
    self.assertEqual(task.priority, "HIGH")

# Implement (GREEN)
def add_task(conn, title: str, description: str = "", priority: str = "MEDIUM") -> int:
    """Add task with priority (FR-011)."""
    # Implementation here
    pass

# Commit: "FR-011: Add task priority support"
```

### Phase 6: Validation

**Purpose**: Verify implementation against specifications

**Checklist**:
- [ ] All functional requirements implemented
- [ ] All tests passing (>80% coverage)
- [ ] Non-functional requirements met (performance, etc.)
- [ ] User scenarios work end-to-end
- [ ] Documentation updated
- [ ] Constitution principles followed

---

## Agent Workflow

### Using Spec-Kit Agents

Spec-kit provides AI agents for each phase. The agents are defined in `.github/agents/`:

```
.github/agents/
├── speckit.specify.agent.md      # Create specifications
├── speckit.plan.agent.md         # Generate plans
├── speckit.tasks.agent.md        # Break down tasks
├── speckit.implement.agent.md    # Guide implementation
└── copilot-instructions.md       # GitHub Copilot context
```

### Agent Invocation (Conceptual)

```bash
# Note: Actual invocation depends on your AI assistant setup

# Phase 1: Create spec
/speckit.specify "Add task priority levels with high, medium, low options"

# Phase 2: Generate plan
/speckit.plan "Create implementation plan for task priorities"

# Phase 3: Break down tasks
/speckit.tasks "Generate task breakdown for priority feature"

# Phase 4: Get implementation guidance
# Use copilot-instructions.md for context during coding
```

### Manual Workflow (Without Agents)

If agents are not available, follow this manual process:

1. **Copy templates** from `.specify/templates/`
2. **Fill in spec.md** using spec-template.md
3. **Create plan.md** using plan-template.md
4. **Update data-model.md** with schema changes
5. **Write tasks.md** using tasks-template.md
6. **Implement** following TDD approach

---

## Adding New Features

### Step-by-Step Process

#### 1. Define the Feature

Start with a clear, concise feature description:

**Good examples**:
- "Add task priority levels (high, medium, low)"
- "Support task due dates with reminders"
- "Enable task categories/tags"

**Bad examples** (too vague):
- "Make tasks better"
- "Add more features"
- "Improve usability"

#### 2. Create Feature Branch

```powershell
# Fetch latest
git fetch --all --prune

# Find next feature number (check existing specs)
# If highest is specs/001-task-manager, use 002

# Create branch
git checkout -b 002-task-priorities
```

#### 3. Create Spec Directory

```powershell
# Create specs directory for new feature
mkdir specs\002-task-priorities
cd specs\002-task-priorities
```

#### 4. Write Specification

Copy template and fill in:

```powershell
# Copy spec template
cp ..\..\specify\templates\spec-template.md spec.md

# Edit spec.md with:
# - User scenarios
# - Functional requirements (FR-011, FR-012, ...)
# - Non-functional requirements
# - Success criteria
```

#### 5. Create Technical Plan

```powershell
# Copy plan template
cp ..\..\specify\templates\plan-template.md plan.md

# Edit plan.md with:
# - Architecture decisions
# - Database schema changes
# - Component updates
# - Testing approach
```

#### 6. Update Data Model

```powershell
# Copy data model template (if needed)
cp ..\..\specify\templates\data-model-template.md data-model.md

# Document:
# - Entity changes
# - New fields and validation
# - Database migrations
```

#### 7. Generate Task Breakdown

```powershell
# Copy tasks template
cp ..\..\specify\templates\tasks-template.md tasks.md

# Break down into phases:
# - Setup (if needed)
# - Data Model updates
# - Database layer changes
# - CLI layer changes
# - Testing
# - Documentation
```

#### 8. Implement with TDD

For each task in tasks.md:

```powershell
# 1. Write test
# Edit tests/test_*.py with new test case

# 2. Run test (should FAIL)
python -m unittest tests.test_cli -v

# 3. Implement feature
# Edit source files in task_manager/

# 4. Run test (should PASS)
python -m unittest tests.test_cli -v

# 5. Refactor if needed

# 6. Commit with requirement reference
git add .
git commit -m "FR-011: Add task priority field and validation"

# 7. Mark task complete in tasks.md
# Update [ ] to [x] for completed task
```

#### 9. Validate Against Spec

Before merging, verify:

```powershell
# Run all tests
python -m unittest discover -v

# Check coverage (optional, use coverage.py)
pip install coverage
coverage run -m unittest discover
coverage report

# Verify all requirements implemented
# Go through spec.md and check each FR-XXX

# Update README if needed
# Add new commands/features to documentation
```

#### 10. Merge to Main

```powershell
# Push feature branch
git push origin 002-task-priorities

# Create pull request
# Review against spec requirements
# Merge when approved
```

---

## Best Practices

### 1. Start with Specifications

✅ **Do**: Write complete spec before coding  
❌ **Don't**: Code first and document later

### 2. Use Requirement IDs

✅ **Do**: Reference FR-XXX in commits and comments  
❌ **Don't**: Use vague commit messages like "fix stuff"

### 3. Follow TDD

✅ **Do**: Write test → Watch it fail → Implement → Pass  
❌ **Don't**: Write code without tests

### 4. Keep Tasks Small

✅ **Do**: Break into 1-2 hour tasks  
❌ **Don't**: Create "implement entire feature" tasks

### 5. Update Documentation

✅ **Do**: Update README with new features  
❌ **Don't**: Leave documentation outdated

### 6. Check Constitution

✅ **Do**: Verify changes align with `.specify/memory/constitution.md`  
❌ **Don't**: Violate principles without justification

### 7. Trace Everything

✅ **Do**: Every line of code traces to a requirement  
❌ **Don't**: Add undocumented features

---

## Common Scenarios

### Scenario 1: Adding a Simple Field

**Feature**: "Add 'created_by' field to tasks"

**Workflow**:
1. Update `spec.md`: Add FR-013 requirement
2. Update `plan.md`: Database schema change
3. Update `data-model.md`: Add field to Task entity
4. Update `tasks.md`:
   - T001: Update Task model
   - T002: Update database schema
   - T003: Update add_task()
   - T004: Write tests
5. Implement with TDD
6. Update README

### Scenario 2: Adding a New Command

**Feature**: "Add 'delete' command to remove tasks"

**Workflow**:
1. Update `spec.md`:
   - User scenario: "User deletes completed task"
   - FR-014: Support task deletion by ID
   - FR-015: Prevent deletion of active tasks
2. Update `plan.md`:
   - CLI: Add delete subcommand
   - Database: Add delete_task() function
   - Validation: Check task exists and is completed
3. Update `tasks.md`:
   - T001: Add delete_task() to db.py
   - T002: Add handle_delete() to cli.py
   - T003: Update argparse with delete subcommand
   - T004: Write tests for delete_task()
   - T005: Write tests for CLI delete command
   - T006: Update README
4. Implement with TDD
5. Test edge cases (non-existent task, active task)

### Scenario 3: Modifying Existing Behavior

**Feature**: "Change list command to show newest tasks first"

**Workflow**:
1. Update `spec.md`: Modify FR-004 requirement
2. Update `plan.md`: Database query change (ORDER BY created_at DESC)
3. Update `data-model.md`: Update query pattern
4. Update `tasks.md`:
   - T001: Modify list_tasks() query
   - T002: Update tests to expect new order
5. Implement (modify existing code)
6. Verify no regressions

### Scenario 4: Adding External Dependency

**Feature**: "Add natural language parsing with spaCy"

**Workflow**:
1. **STOP**: Check constitution
2. `.specify/memory/constitution.md` says: "Simplicity & YAGNI - Use standard library"
3. **Decision point**:
   - Option A: Reject (violates constitution)
   - Option B: Amend constitution with justification
4. If proceeding:
   - Update constitution.md with amendment
   - Document in `spec.md` assumptions
   - Update `plan.md` with dependency
   - Add to requirements.txt
   - Update installation instructions

---

## Helper Scripts

Spec-kit provides bash scripts in `.specify/scripts/bash/`:

```bash
# Check prerequisites for current feature
.specify/scripts/bash/check-prerequisites.sh --json

# Setup plan for new feature
.specify/scripts/bash/setup-plan.sh --json

# Update agent context with new technologies
.specify/scripts/bash/update-agent-context.sh copilot

# Create new feature branch
.specify/scripts/bash/create-new-feature.sh "feature-name"
```

**Note**: These are bash scripts. On Windows, use Git Bash or WSL:

```powershell
# Using Git Bash
& "C:\Program Files\Git\bin\bash.exe" .specify/scripts/bash/check-prerequisites.sh --json

# Using WSL
wsl bash .specify/scripts/bash/check-prerequisites.sh --json
```

---

## Quick Reference

### File Locations

```
specs/NNN-feature-name/     # Feature documentation
├── spec.md                 # Requirements and scenarios
├── plan.md                 # Technical design
├── data-model.md           # Data structures
└── tasks.md                # Implementation breakdown

.specify/
├── memory/
│   └── constitution.md     # Project principles
├── templates/              # Document templates
└── scripts/                # Helper scripts

.github/agents/             # AI agent definitions
└── copilot-instructions.md # GitHub Copilot context

TaskManager/                # Implementation
├── task_manager/           # Source code
├── tests/                  # Unit tests
└── README.md               # User documentation
```

### Command Cheat Sheet

```powershell
# Run tests
python -m unittest discover -v

# Install in dev mode
python -m pip install -e .

# Run task manager
task-manager list
task-manager add "Task" --description "Details"

# Check for errors
python -m pylint task_manager/

# Format code
python -m black task_manager/
```

### Requirement ID Format

- **FR-XXX**: Functional Requirement (e.g., FR-001, FR-002)
- **NFR-XXX**: Non-Functional Requirement (e.g., NFR-001)
- **T-XXX**: Implementation Task (e.g., T001, T002)

---

## Need Help?

1. **Review existing specs**: Look at `specs/001-task-manager/` for examples
2. **Check templates**: See `.specify/templates/` for structure
3. **Read constitution**: Understand principles in `.specify/memory/constitution.md`
4. **Study implementation**: Compare code to specs for traceability
5. **Ask agents**: Use GitHub Copilot with context from `copilot-instructions.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-24  
**Related**: README.md, SUMMARY.md, constitution.md
