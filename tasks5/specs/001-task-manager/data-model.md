# Data Model: Task Management System

**Feature**: Task Management System  
**Created**: 2025-11-24

## Entities

### Task

**Purpose**: Represents a single task or to-do item in the system.

**Fields**:
- `id` (integer, primary key)
  - Auto-incrementing unique identifier
  - Used for referencing and completing tasks
  
- `title` (string, required)
  - Brief description of the task
  - Maximum 200 characters
  - Cannot be empty
  
- `description` (string, optional)
  - Detailed information about the task
  - Maximum 1000 characters
  - Default: empty string
  
- `completed` (boolean)
  - Task completion status
  - Default: false (0 in SQLite)
  - True (1) when marked complete
  
- `created_at` (timestamp)
  - When the task was created
  - Auto-generated on insert
  - Format: ISO 8601 (YYYY-MM-DD HH:MM:SS)

**Relationships**: None (single entity system)

**State Transitions**:
```
[Created] → pending (completed = 0)
[Completed] → completed (completed = 1)
```

**Validation Rules**:
- Title must not be empty
- Title length ≤ 200 characters
- Description length ≤ 1000 characters
- ID must be positive integer
- completed must be boolean (0 or 1)

**Business Rules**:
- Tasks cannot be uncompleted once marked complete
- Task IDs are immutable
- created_at timestamp cannot be modified
- Title is the only required field

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) > 0 AND length(title) <= 200),
    description TEXT CHECK(length(description) <= 1000),
    completed INTEGER DEFAULT 0 CHECK(completed IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_created_at ON tasks(created_at DESC);
```

## Data Access Patterns

### Common Queries

**List all pending tasks**:
```sql
SELECT * FROM tasks WHERE completed = 0 ORDER BY created_at DESC;
```

**List all completed tasks**:
```sql
SELECT * FROM tasks WHERE completed = 1 ORDER BY created_at DESC;
```

**Search tasks by keyword**:
```sql
SELECT * FROM tasks 
WHERE title LIKE ? OR description LIKE ? 
ORDER BY created_at DESC;
```

**Get specific task**:
```sql
SELECT * FROM tasks WHERE id = ?;
```

**Mark task complete**:
```sql
UPDATE tasks SET completed = 1 WHERE id = ?;
```

## Python Data Class

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    """Represents a task in the task management system."""
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    
    @classmethod
    def from_db_row(cls, row: tuple) -> 'Task':
        """Create Task from database row."""
        return cls(
            id=row[0],
            title=row[1],
            description=row[2] or "",
            completed=bool(row[3]),
            created_at=datetime.fromisoformat(row[4])
        )
    
    def to_dict(self) -> dict:
        """Convert Task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }
    
    @property
    def status(self) -> str:
        """Get human-readable status."""
        return "✓ Complete" if self.completed else "○ Pending"
```

## Example Data

```python
# Pending task
Task(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False,
    created_at=datetime(2025, 11, 24, 10, 30, 0)
)

# Completed task
Task(
    id=2,
    title="Write documentation",
    description="Complete the README file",
    completed=True,
    created_at=datetime(2025, 11, 24, 9, 15, 0)
)
```
