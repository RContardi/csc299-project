# Spec-Kit Workflow Diagram

This document provides visual representations of the spec-kit methodology used in tasks5.

## 1. Overall Spec-Kit Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC-KIT METHODOLOGY                         │
└─────────────────────────────────────────────────────────────────┘

    Natural Language Input
           ↓
    ┌──────────────┐
    │   SPECIFY    │  → specs/NNN-feature/spec.md
    └──────────────┘     • User Scenarios
           ↓             • Functional Requirements (FR-XXX)
                         • Non-Functional Requirements (NFR-XXX)
    ┌──────────────┐     • Success Criteria
    │     PLAN     │  → specs/NNN-feature/plan.md
    └──────────────┘     • Technology Stack
           ↓             • Architecture Design
                         • Component Structure
    ┌──────────────┐     • Implementation Phases
    │    MODEL     │  → specs/NNN-feature/data-model.md
    └──────────────┘     • Entity Definitions
           ↓             • Database Schema
                         • Validation Rules
    ┌──────────────┐     • Query Patterns
    │     TASK     │  → specs/NNN-feature/tasks.md
    └──────────────┘     • Implementation Tasks (T001, T002...)
           ↓             • Dependencies
                         • Phase Organization
    ┌──────────────┐     • Verification Checklist
    │  IMPLEMENT   │  → TaskManager/ (source code)
    └──────────────┘     • Models Layer
           ↓             • Database Layer
                         • CLI Layer
    ┌──────────────┐     • Tests
    │   VALIDATE   │  → Quality Assurance
    └──────────────┘     • Verify Requirements
           ↓             • Run Tests (>80% coverage)
                         • Check Constitution
    Production Ready      • User Acceptance
```

## 2. Project Directory Structure

```
tasks5/
│
├── specs/                          # Specification Documents
│   └── 001-task-manager/
│       ├── spec.md                 # Feature specification
│       ├── plan.md                 # Technical plan
│       ├── data-model.md           # Data structures
│       └── tasks.md                # Implementation tasks
│
├── .github/                        # Spec-Kit Infrastructure
│   ├── agents/                     # AI Agent Definitions
│   │   ├── speckit.specify.agent.md
│   │   ├── speckit.plan.agent.md
│   │   ├── speckit.tasks.agent.md
│   │   ├── speckit.implement.agent.md
│   │   └── copilot-instructions.md ⭐ NEW
│   └── prompts/                    # Agent Prompts
│       ├── speckit.specify.prompt.md
│       ├── speckit.plan.prompt.md
│       └── ...
│
├── .specify/                       # Spec-Kit Configuration
│   ├── memory/
│   │   └── constitution.md         ⭐ UPDATED
│   ├── templates/                  # Document Templates
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   └── ...
│   └── scripts/                    # Helper Scripts
│       └── bash/
│           ├── check-prerequisites.sh
│           ├── create-new-feature.sh
│           └── ...
│
├── TaskManager/                    # Implementation
│   ├── task_manager/               # Source Code
│   │   ├── __init__.py
│   │   ├── models.py               # Data Models
│   │   ├── db.py                   # Database Layer
│   │   └── cli.py                  # CLI Layer
│   ├── tests/                      # Unit Tests
│   │   ├── test_models.py
│   │   ├── test_db.py
│   │   └── test_cli.py
│   ├── main.py                     # Entry Point
│   ├── gui.py                      # GUI Interface
│   ├── pyproject.toml              # Package Config
│   └── README.md                   # User Docs
│
├── README.md                       ⭐ UPDATED (Project Overview)
├── SPEC-KIT.md                     ⭐ NEW (Methodology Guide)
├── WORKFLOW.md                     ⭐ NEW (Process Guide)
├── SUMMARY.md                      ⭐ UPDATED (Retrospective)
├── CHECKLIST.md                    ⭐ NEW (Verification)
└── video.txt                       ⭐ UPDATED (Demo Script)

⭐ = Files created/updated in this integration
```

## 3. Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                                                             │
│   task-manager add "Task"  →  CLI Parser (argparse)        │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   CLI LAYER (cli.py)                        │
│                                                             │
│  • Command handlers (add, list, complete, search)          │
│  • Argument parsing and validation                         │
│  • Output formatting                                       │
│  • Error handling                                          │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                DATABASE LAYER (db.py)                       │
│                                                             │
│  • init_db()       - Create tables                         │
│  • add_task()      - Insert task                           │
│  • list_tasks()    - Query all tasks                       │
│  • get_task()      - Query by ID                           │
│  • complete_task() - Update status                         │
│  • search_tasks()  - Query by keyword                      │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  MODELS LAYER (models.py)                   │
│                                                             │
│  Task Dataclass:                                           │
│    • id: int                                               │
│    • title: str (max 200 chars)                           │
│    • description: str (max 1000 chars)                    │
│    • completed: bool                                       │
│    • created_at: datetime                                  │
│                                                             │
│  Validation & Serialization Methods                        │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  DATA STORAGE (SQLite)                      │
│                                                             │
│  tasks.db:                                                 │
│    CREATE TABLE tasks (                                    │
│      id INTEGER PRIMARY KEY,                               │
│      title TEXT NOT NULL,                                  │
│      description TEXT,                                     │
│      completed INTEGER DEFAULT 0,                          │
│      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        │
│    );                                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 4. Test-Driven Development Cycle

```
┌──────────────────────────────────────────────────────────┐
│                   TDD WORKFLOW                           │
└──────────────────────────────────────────────────────────┘

    Pick Task from tasks.md
           ↓
    ┌──────────────┐
    │  WRITE TEST  │ ← Reference FR-XXX requirement
    │     (RED)    │
    └──────────────┘
           ↓
    Run: python -m unittest
           ↓
    ❌ Test FAILS (expected)
           ↓
    ┌──────────────┐
    │  IMPLEMENT   │ ← Minimum code to pass
    │   (GREEN)    │
    └──────────────┘
           ↓
    Run: python -m unittest
           ↓
    ✅ Test PASSES
           ↓
    ┌──────────────┐
    │   REFACTOR   │ ← Clean up code
    │   (CLEAN)    │
    └──────────────┘
           ↓
    Run: python -m unittest
           ↓
    ✅ Still PASSES
           ↓
    Commit: "FR-XXX: Feature description"
           ↓
    Mark task complete in tasks.md
           ↓
    Continue to next task
```

## 5. Requirement Traceability Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  TRACEABILITY CHAIN                          │
└──────────────────────────────────────────────────────────────┘

User Scenario (spec.md)
  "User adds a task with title and description"
           ↓
Functional Requirement (spec.md)
  FR-001: System MUST allow users to add tasks
           ↓
Architecture Decision (plan.md)
  CLI: add command with --description argument
  Database: add_task(title, description) function
           ↓
Data Model (data-model.md)
  Task entity with title and description fields
  Validation: title max 200 chars, description max 1000 chars
           ↓
Implementation Task (tasks.md)
  T012: Implement add_task(conn, title, description) function
           ↓
Test Case (tests/test_db.py)
  def test_add_task_with_description():
      """Test FR-001: Add task with description."""
           ↓
Implementation (task_manager/db.py)
  def add_task(conn, title: str, description: str = "") -> int:
      """Add task to database (FR-001)."""
           ↓
Commit Message
  "FR-001: Implement add_task function with description support"
           ↓
Validation (test run)
  ✅ test_add_task_with_description PASSED
           ↓
User Acceptance
  ✅ Can add tasks with descriptions via CLI
```

## 6. Constitution Compliance Check

```
┌──────────────────────────────────────────────────────────────┐
│              CONSTITUTIONAL PRINCIPLES                       │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│  Spec-First Dev     │  ✅ All specs written before code
└─────────────────────┘
┌─────────────────────┐
│ Modular Architecture│  ✅ 3-layer design implemented
└─────────────────────┘
┌─────────────────────┐
│  Test-Driven Dev    │  ✅ >80% coverage achieved
└─────────────────────┘
┌─────────────────────┐
│ Command-Line First  │  ✅ All features in CLI
└─────────────────────┘
┌─────────────────────┐
│ Simplicity & YAGNI  │  ✅ Zero external dependencies
└─────────────────────┘

    ↓ All Principles Met ↓

┌──────────────────────────────────────────────────────────────┐
│             CONSTITUTION COMPLIANT ✅                        │
└──────────────────────────────────────────────────────────────┘
```

## 7. Feature Development Timeline

```
Timeline: specs/001-task-manager development

Week 1: Specification Phase
├─ Day 1-2: Create spec.md
│   • Define user scenarios
│   • List functional requirements (FR-001 to FR-010)
│   • List non-functional requirements (NFR-001 to NFR-005)
│   • Set success criteria
│
├─ Day 3-4: Create plan.md
│   • Choose technology stack
│   • Design 3-layer architecture
│   • Define database schema
│   • Plan implementation phases
│
└─ Day 5: Create data-model.md & tasks.md
    • Document Task entity
    • Write database schema
    • Break down into 45 tasks

Week 2: Implementation Phase
├─ Day 1: Setup (T001-T004)
│   • Create directory structure
│   • Setup pyproject.toml
│   • Initialize git
│
├─ Day 2: Models Layer (T005-T009)
│   • Implement Task dataclass
│   • Add validation
│   • Write tests
│
├─ Day 3-4: Database Layer (T010-T017)
│   • Implement db.py functions
│   • Write tests
│   • Test with actual SQLite
│
├─ Day 5: CLI Layer (T018-T024)
│   • Implement argparse
│   • Add command handlers
│   • Write tests
│
└─ Day 6: Integration (T025-T028)
    • Create main.py
    • End-to-end testing
    • Fix bugs

Week 3: Testing & Polish
├─ Day 1-2: Testing (T029-T034)
│   • Write comprehensive tests
│   • Achieve >80% coverage
│   • Fix edge cases
│
├─ Day 3: Installation (T035-T040)
│   • Configure pyproject.toml
│   • Test installation
│   • Update documentation
│
└─ Day 4-5: Polish (T041-T045)
    • Code formatting
    • Linting fixes
    • Final review
    • Demo preparation
```

## 8. Adding a New Feature (Example: Task Priorities)

```
┌──────────────────────────────────────────────────────────────┐
│         EXAMPLE: Adding Task Priority Feature               │
└──────────────────────────────────────────────────────────────┘

Step 1: Create Branch
  git checkout -b 002-task-priorities

Step 2: Write Specification
  specs/002-task-priorities/spec.md
    FR-011: Tasks have priority (HIGH/MEDIUM/LOW)
    FR-012: Add command accepts --priority flag
    FR-013: List command filters by priority

Step 3: Create Plan
  specs/002-task-priorities/plan.md
    Database: Add priority column
    Models: Add priority field with validation
    CLI: Add --priority arguments

Step 4: Update Data Model
  specs/002-task-priorities/data-model.md
    ALTER TABLE tasks ADD COLUMN priority TEXT
    CHECK(priority IN ('HIGH', 'MEDIUM', 'LOW'))

Step 5: Break Down Tasks
  specs/002-task-priorities/tasks.md
    T001: Update Task model with priority
    T002: Add priority validation
    T003: Create database migration
    T004: Update add_task() function
    T005: Add --priority to CLI
    T006: Implement list filtering
    T007-T010: Write tests

Step 6: Implement with TDD
  For each task:
    Write test → Fail → Implement → Pass → Refactor → Commit

Step 7: Validate
  Run all tests
  Check coverage
  Verify requirements
  Update documentation

Step 8: Merge
  Create pull request
  Code review
  Merge to main
```

## 9. Spec-Kit Agents Interaction

```
┌──────────────────────────────────────────────────────────────┐
│                   AGENTS WORKFLOW                            │
└──────────────────────────────────────────────────────────────┘

User Input: "Add task priority levels"
           ↓
    ┌──────────────────┐
    │ speckit.specify  │ → Generate spec.md
    │     agent        │    • User scenarios
    └──────────────────┘    • Requirements (FR-XXX)
           ↓                • Success criteria
    ┌──────────────────┐
    │  speckit.plan    │ → Generate plan.md
    │     agent        │    • Architecture
    └──────────────────┘    • Tech decisions
           ↓                • Implementation phases
    ┌──────────────────┐
    │  speckit.tasks   │ → Generate tasks.md
    │     agent        │    • Task breakdown
    └──────────────────┘    • Dependencies
           ↓                • Verification checklist
    ┌──────────────────┐
    │speckit.implement │ → Guide implementation
    │     agent        │    • TDD cycle
    └──────────────────┘    • Code generation
           ↓                • Quality checks
    ┌──────────────────┐
    │ GitHub Copilot   │ → Coding assistance
    │ (copilot-        │    • Code completion
    │  instructions)   │    • Test generation
    └──────────────────┘    • Documentation
           ↓
    Production Code
```

## 10. Documentation Hierarchy

```
tasks5/
│
├─ README.md                    ⭐ START HERE
│   └─ Project overview, quick start
│
├─ SPEC-KIT.md                  📚 Learn Methodology
│   └─ What is spec-kit, how it works
│
├─ WORKFLOW.md                  🔧 Practical Guide
│   └─ Step-by-step feature development
│
├─ SUMMARY.md                   📖 Retrospective
│   └─ Development history, lessons learned
│
├─ CHECKLIST.md                 ✅ Verification
│   └─ Integration checklist, validation steps
│
├─ TaskManager/README.md        📱 User Guide
│   └─ Installation, usage, commands
│
└─ .specify/memory/constitution.md  📜 Principles
    └─ Development standards, quality gates
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-24  
**Purpose**: Visual reference for spec-kit methodology in tasks5

These diagrams provide a comprehensive visual overview of how spec-kit integrates with the task management system development process.
