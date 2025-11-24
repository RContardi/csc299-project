# Spec-Kit Integration Guide

This document explains how tasks5 uses GitHub's spec-kit framework for specification-driven development.

## What is Spec-Kit?

**Spec-Kit** is a methodology and toolset developed by GitHub for structured software development. It emphasizes creating comprehensive specifications before implementation, using AI agents to guide each phase of development.

### Core Philosophy

1. **Specification First** - Define what to build before building it
2. **Structured Process** - Follow consistent phases (Specify → Plan → Model → Task → Implement)
3. **AI-Assisted** - Use agents to maintain consistency and quality
4. **Traceability** - Every line of code traces back to a documented requirement
5. **Living Documentation** - Specs evolve with the project

## Spec-Kit Components in This Project

### 1. Specification Documents (`specs/001-task-manager/`)

#### spec.md
Complete feature specification including:
- **User Scenarios**: Real-world usage examples with expected behaviors
- **Functional Requirements**: Numbered requirements (FR-001 through FR-010)
- **Non-Functional Requirements**: Performance, quality, standards (NFR-001 through NFR-005)
- **Success Criteria**: Measurable goals for completion
- **Assumptions**: Project constraints and context
- **Out of Scope**: Features explicitly excluded

Example requirement:
```markdown
FR-001: System MUST allow users to add tasks with a title and optional description
```

#### plan.md
Technical implementation plan with:
- **Technology Stack**: Python 3.8+, SQLite3, argparse (standard library only)
- **Architecture**: 3-layer design (Models → Database → CLI)
- **Project Structure**: Directory layout and module organization
- **Database Schema**: Table definitions with indexes
- **API Design**: Internal function signatures
- **Implementation Phases**: Step-by-step build sequence

#### data-model.md
Data structure documentation:
- **Entity Definitions**: Task entity with 5 fields
- **Validation Rules**: Length limits, required fields, constraints
- **State Transitions**: Task lifecycle (pending → completed)
- **Database Schema**: SQL CREATE statements
- **Query Patterns**: Common SELECT/UPDATE operations

#### tasks.md
Implementation breakdown:
- **45 Tasks** organized into 8 phases
- **Dependencies** mapped between tasks
- **Verification Checklist** for quality gates
- **Task Format**: T001, T002, etc. with descriptions

### 2. Spec-Kit Infrastructure

#### .github/agents/
AI agent definitions for each development phase:

- **speckit.specify.agent.md** - Creates feature specifications from natural language
- **speckit.plan.agent.md** - Generates technical plans from specs
- **speckit.tasks.agent.md** - Breaks plans into implementation tasks
- **speckit.implement.agent.md** - Guides implementation process
- **speckit.analyze.agent.md** - Reviews code against specs
- **speckit.checklist.agent.md** - Validates completeness
- **copilot-instructions.md** - GitHub Copilot context for coding

#### .github/prompts/
Prompt templates for each agent:

- **speckit.specify.prompt.md** - Template for specification generation
- **speckit.plan.prompt.md** - Template for planning phase
- **speckit.tasks.prompt.md** - Template for task breakdown
- (Additional prompts for other agents)

#### .specify/
Spec-kit configuration and utilities:

```
.specify/
├── memory/
│   └── constitution.md        # Project principles and standards
├── templates/
│   ├── spec-template.md       # Specification document template
│   ├── plan-template.md       # Plan document template
│   ├── tasks-template.md      # Task breakdown template
│   ├── data-model-template.md # Data model template
│   └── checklist-template.md  # Validation checklist
└── scripts/
    └── bash/
        ├── check-prerequisites.sh     # Validate environment
        ├── create-new-feature.sh      # Initialize feature branch
        ├── setup-plan.sh              # Setup planning phase
        └── update-agent-context.sh    # Update AI context
```

### 3. Constitution (`.specify/memory/constitution.md`)

The project constitution defines non-negotiable principles:

#### Core Principles
1. **Spec-First Development** - No code without specifications
2. **Modular Architecture** - Clean separation of concerns
3. **Test-Driven Development** - TDD mandatory, >80% coverage
4. **Command-Line First** - CLI-accessible features
5. **Simplicity & YAGNI** - Standard library, minimal dependencies

#### Technical Standards
- PEP 8 compliance
- Type hints on all functions
- Docstrings for all public APIs
- Maximum cyclomatic complexity: 15

#### Development Workflow
- Feature branches: `NNN-feature-name`
- Commit messages reference requirements
- Pull requests include tests and coverage
- Quality gates enforced

## How Spec-Kit Was Used

### Initial Feature Development

**Step 1: Natural Language Input**
```
"Create a command-line task management system with SQLite persistence"
```

**Step 2: Specification (speckit.specify)**
Generated `specs/001-task-manager/spec.md` with:
- 4 user scenarios (add, list, complete, search)
- 10 functional requirements
- 5 non-functional requirements
- Clear success criteria

**Step 3: Planning (speckit.plan)**
Generated `specs/001-task-manager/plan.md` with:
- Python + SQLite technology choice
- 3-layer architecture design
- Database schema with indexes
- 8-phase implementation plan

**Step 4: Data Modeling**
Generated `specs/001-task-manager/data-model.md` with:
- Task entity definition
- Validation rules
- SQL schema
- Query patterns

**Step 5: Task Breakdown (speckit.tasks)**
Generated `specs/001-task-manager/tasks.md` with:
- 45 implementation tasks
- Dependency mapping
- Phase organization

**Step 6: Implementation**
Built `TaskManager/` following:
- TDD approach (tests first)
- Layer-by-layer implementation
- Continuous validation against specs
- >80% test coverage achieved

**Step 7: Validation**
Verified against specifications:
- All FR requirements implemented
- All NFR requirements met
- User scenarios work end-to-end
- Constitution principles followed

## Using Spec-Kit for New Features

### Example: Adding Task Priorities

**1. Create Feature Spec**
```markdown
# specs/002-task-priorities/spec.md

## User Scenarios
- User adds high-priority task
- User filters tasks by priority level

## Functional Requirements
- FR-011: Tasks have priority field (HIGH/MEDIUM/LOW)
- FR-012: Add command accepts --priority flag
- FR-013: List command accepts --priority filter

## Success Criteria
- Users can set priority on new tasks
- Tasks default to MEDIUM priority
- List command filters by priority
```

**2. Generate Plan**
```markdown
# specs/002-task-priorities/plan.md

## Architecture Changes
- Update Task model: Add priority field (enum)
- Update database: ALTER TABLE with priority column
- Update CLI: Add --priority argument
- Update tests: Test all priority levels

## Implementation Phases
1. Data model update
2. Database migration
3. CLI argument parsing
4. Filtering logic
5. Testing
```

**3. Break Down Tasks**
```markdown
# specs/002-task-priorities/tasks.md

- [ ] T001: Update Task dataclass with priority field
- [ ] T002: Add priority validation (HIGH/MEDIUM/LOW)
- [ ] T003: Create database migration script
- [ ] T004: Update add_task() function
- [ ] T005: Add --priority to CLI parser
- [ ] T006: Implement filter logic
- [ ] T007: Write unit tests
- [ ] T008: Update README
```

**4. Implement with TDD**
```python
# Write test (RED)
def test_add_task_with_priority(self):
    """Test FR-011: Add task with priority."""
    task_id = add_task(self.conn, "Urgent", priority="HIGH")
    task = get_task(self.conn, task_id)
    self.assertEqual(task.priority, "HIGH")

# Implement (GREEN)
def add_task(conn, title, description="", priority="MEDIUM"):
    """Add task with priority (FR-011)."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)",
        (title, description, priority)
    )
    return cursor.lastrowid

# Commit: "FR-011: Add task priority support"
```

## Benefits Realized

### ✅ Clarity and Communication
- Specifications provide shared understanding
- No ambiguity about requirements
- New team members onboard quickly by reading specs

### ✅ Quality and Traceability
- Every feature justified by requirement
- Tests validate specifications
- Code reviews verify against documented design

### ✅ Maintainability
- Architectural decisions documented
- Rationale preserved for future reference
- Changes tracked through spec updates

### ✅ AI-Assisted Development
- Agents provide consistent structure
- Templates ensure completeness
- Copilot understands project context

### ✅ Risk Reduction
- Issues caught in specification phase
- Architecture validated before coding
- Scope clearly defined upfront

## Challenges and Solutions

### Challenge 1: Documentation Overhead
**Issue**: Writing specs before coding feels slow  
**Solution**: Specs prevent rework, saving time overall  
**Learning**: 1 hour of planning saves 5 hours of debugging

### Challenge 2: Keeping Specs Updated
**Issue**: Code and specs drift over time  
**Solution**: Update specs as part of feature development  
**Learning**: Treat specs as code (version control, reviews)

### Challenge 3: Template Customization
**Issue**: Generic templates don't fit all projects  
**Solution**: Customize templates in `.specify/templates/`  
**Learning**: Adapt spec-kit to project needs

### Challenge 4: Tool Integration
**Issue**: Bash scripts don't run natively on Windows  
**Solution**: Use Git Bash or WSL for script execution  
**Learning**: Consider PowerShell alternatives for Windows

## Best Practices

### 1. Start Every Feature with a Spec
- Write spec.md before any code
- Review and approve specifications
- Use specs as contract between stakeholders

### 2. Keep Specs Concise but Complete
- Include all requirements
- Avoid implementation details in specs
- Focus on "what" not "how" in specifications

### 3. Use Requirement IDs Consistently
- FR-XXX for functional requirements
- NFR-XXX for non-functional requirements
- Reference IDs in commits and code comments

### 4. Follow Constitutional Principles
- Validate decisions against constitution
- Document exceptions with justification
- Update constitution when principles change

### 5. Maintain Traceability
- Code → Tests → Requirements → Specs
- Every feature has a "why" documented
- Changes update all linked documents

### 6. Leverage AI Agents
- Use agents for consistency
- Provide good context to agents
- Review agent output critically

## Resources

### Documentation
- **README.md** - Project overview and setup
- **WORKFLOW.md** - Step-by-step spec-kit process
- **SUMMARY.md** - Development retrospective
- **constitution.md** - Project principles

### Specifications
- **specs/001-task-manager/spec.md** - Feature requirements
- **specs/001-task-manager/plan.md** - Technical design
- **specs/001-task-manager/data-model.md** - Data structures
- **specs/001-task-manager/tasks.md** - Implementation tasks

### Templates
- **.specify/templates/** - Reusable document templates
- **.github/agents/** - AI agent definitions
- **.github/prompts/** - Agent prompt templates

## Quick Reference

### Spec-Kit Phases
```
1. Specify  → Create spec.md
2. Plan     → Create plan.md
3. Model    → Create data-model.md
4. Task     → Create tasks.md
5. Implement → Build features with TDD
6. Validate  → Verify against specs
```

### File Locations
```
specs/NNN-feature/     # Feature documentation
├── spec.md            # Requirements
├── plan.md            # Technical design
├── data-model.md      # Data structures
└── tasks.md           # Task breakdown

.specify/              # Spec-kit configuration
├── memory/constitution.md
├── templates/
└── scripts/

.github/agents/        # AI agent definitions
└── copilot-instructions.md
```

### Commands
```powershell
# View specifications
cat specs\001-task-manager\spec.md

# Check constitution
cat .specify\memory\constitution.md

# Run tests
python -m unittest discover -v

# Install application
python -m pip install -e .
```

## Further Reading

- **GitHub Spec-Kit Documentation**: [Official docs link]
- **WORKFLOW.md**: Detailed process guide
- **SUMMARY.md**: Project retrospective
- **TaskManager/README.md**: Implementation docs

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-24  
**Status**: Active

This document explains how tasks5 integrates GitHub's spec-kit methodology. For practical application, see WORKFLOW.md.
