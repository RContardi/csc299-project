"""Database access layer for the task manager.

Uses SQLite for persistence. All functions are written to be unit-testable and
accept an optional `connection` parameter for injection/mocking.
"""
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from .models import Task


def initialize(conn: sqlite3.Connection) -> None:
    """Create required tables if they don't exist.

    Args:
        conn: SQLite3 connection.
    """
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def add_task(conn: sqlite3.Connection, title: str, description: Optional[str] = None) -> Task:
    """Add a new task to the database and return the created Task.

    Args:
        conn: SQLite3 connection.
        title: Task title.
        description: Optional description.
    Returns:
        The persisted Task with assigned id.
    """
    # Use timezone-aware UTC timestamps to avoid deprecation warnings
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, completed, created_at) VALUES (?, ?, 0, ?)",
        (title, description, now),
    )
    conn.commit()
    task_id = cur.lastrowid
    return Task(id=task_id, title=title, description=description, completed=False, created_at=datetime.fromisoformat(now))


def list_tasks(conn: sqlite3.Connection) -> List[Task]:
    """Return all tasks from the database.

    Args:
        conn: SQLite3 connection.
    """
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, completed, created_at FROM tasks ORDER BY created_at DESC")
    rows = cur.fetchall()
    return [_row_to_task(r) for r in rows]


def search_tasks(conn: sqlite3.Connection, keyword: str) -> List[Task]:
    """Search tasks by keyword in title or description.

    Args:
        conn: SQLite3 connection.
        keyword: Keyword to search for.
    """
    cur = conn.cursor()
    like = f"%{keyword}%"
    cur.execute(
        "SELECT id, title, description, completed, created_at FROM tasks WHERE title LIKE ? OR description LIKE ? ORDER BY created_at DESC",
        (like, like),
    )
    rows = cur.fetchall()
    return [_row_to_task(r) for r in rows]


def complete_task(conn: sqlite3.Connection, task_id: int) -> bool:
    """Mark a task as complete.

    Args:
        conn: SQLite3 connection.
        task_id: ID of the task to mark complete.
    Returns:
        True if a row was updated, False otherwise.
    """
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    return cur.rowcount > 0


def delete_task(conn: sqlite3.Connection, task_id: int) -> bool:
    """Delete a task from the database.

    Args:
        conn: SQLite3 connection.
        task_id: ID of the task to delete.
    Returns:
        True if a row was deleted, False otherwise.
    """
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_task(row) -> Task:
    """Convert a DB row to a Task instance.

    Args:
        row: Tuple matching the SELECT columns.
    """
    task_id, title, description, completed, created_at = row
    return Task(
        id=task_id,
        title=title,
        description=description,
        completed=bool(completed),
        created_at=datetime.fromisoformat(created_at),
    )
