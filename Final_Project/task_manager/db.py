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
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS deleted_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            deleted_at TEXT NOT NULL
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
    
    # Check if database is empty and reset autoincrement if needed
    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]
    if count == 0:
        # Reset the autoincrement counter to 1
        cur.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    
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
    """Delete a task from the database and reorder remaining task IDs.
    Saves the task to deleted_tasks table before deletion for potential restoration.

    Args:
        conn: SQLite3 connection.
        task_id: ID of the task to delete.
    Returns:
        True if a row was deleted, False otherwise.
    """
    cur = conn.cursor()
    
    # First, save the task to deleted_tasks for potential restoration
    cur.execute("SELECT id, title, description, completed, created_at FROM tasks WHERE id = ?", (task_id,))
    task_data = cur.fetchone()
    
    if task_data:
        deleted_at = datetime.now(timezone.utc).isoformat()
        cur.execute("""
            INSERT INTO deleted_tasks (original_id, title, description, completed, created_at, deleted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_data[0], task_data[1], task_data[2], task_data[3], task_data[4], deleted_at))
    
    # Now delete from tasks
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    
    if cur.rowcount > 0:
        # Reorder all tasks with IDs greater than the deleted one
        cur.execute("""
            UPDATE tasks 
            SET id = id - 1 
            WHERE id > ?
        """, (task_id,))
        conn.commit()
        return True
    
    conn.commit()
    return False


def reorder_task_ids(conn: sqlite3.Connection) -> None:
    """Reorder all task IDs to be sequential starting from 1.
    
    Args:
        conn: SQLite3 connection.
    """
    cur = conn.cursor()
    
    # Get all tasks ordered by current ID
    cur.execute("SELECT id FROM tasks ORDER BY id")
    old_ids = [row[0] for row in cur.fetchall()]
    
    # Create a temporary table
    cur.execute("""
        CREATE TEMPORARY TABLE tasks_temp AS 
        SELECT * FROM tasks ORDER BY id
    """)
    
    # Clear original table
    cur.execute("DELETE FROM tasks")
    
    # Reinsert with new sequential IDs
    cur.execute("""
        INSERT INTO tasks (id, title, description, completed, created_at)
        SELECT ROW_NUMBER() OVER (ORDER BY id) as new_id, title, description, completed, created_at
        FROM tasks_temp
    """)
    
    # Drop temporary table
    cur.execute("DROP TABLE tasks_temp")
    
    conn.commit()


def list_deleted_tasks(conn: sqlite3.Connection, limit: int = 10) -> List[tuple]:
    """Get recently deleted tasks.
    
    Args:
        conn: SQLite3 connection.
        limit: Maximum number of deleted tasks to return.
    Returns:
        List of tuples (id, title, description, completed, deleted_at).
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, description, completed, deleted_at 
        FROM deleted_tasks 
        ORDER BY deleted_at DESC 
        LIMIT ?
    """, (limit,))
    return cur.fetchall()


def restore_deleted_task(conn: sqlite3.Connection, deleted_task_id: int) -> bool:
    """Restore a deleted task back to the tasks table.
    
    Args:
        conn: SQLite3 connection.
        deleted_task_id: ID of the task in deleted_tasks table.
    Returns:
        True if restored, False otherwise.
    """
    cur = conn.cursor()
    
    # Get the deleted task
    cur.execute("""
        SELECT title, description, completed, created_at 
        FROM deleted_tasks 
        WHERE id = ?
    """, (deleted_task_id,))
    
    task_data = cur.fetchone()
    if not task_data:
        return False
    
    # Add it back to tasks (will get new ID)
    title, description, completed, created_at = task_data
    cur.execute("""
        INSERT INTO tasks (title, description, completed, created_at)
        VALUES (?, ?, ?, ?)
    """, (title, description, completed, created_at))
    
    # Remove from deleted_tasks
    cur.execute("DELETE FROM deleted_tasks WHERE id = ?", (deleted_task_id,))
    
    conn.commit()
    return True


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
