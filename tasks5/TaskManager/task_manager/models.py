"""Models for the task manager.

This module defines the Task data structure used by the application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a task stored in the database.

    Attributes:
        id: The database ID of the task (None if not persisted yet).
        title: Short title of the task.
        description: Optional longer description.
        completed: Whether the task is complete.
        created_at: Timestamp when the task was created.
    """

    id: Optional[int]
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
