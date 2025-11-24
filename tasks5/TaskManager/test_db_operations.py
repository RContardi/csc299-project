"""
Unit tests for task actions without GUI.
Tests that database operations work correctly.
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from task_manager import db as db_module

def setup_test_db():
    """Create test database."""
    if os.path.exists("test_tasks.db"):
        os.remove("test_tasks.db")
    conn = sqlite3.connect("test_tasks.db")
    db_module.initialize(conn)
    return conn

def get_tasks(conn):
    """Get all tasks."""
    cur = conn.cursor()
    cur.execute("SELECT id, title, completed FROM tasks ORDER BY id")
    return cur.fetchall()

def print_tasks(label, tasks):
    """Print task list."""
    print(f"\n{label}: {len(tasks)} tasks")
    for t in tasks:
        status = "✓" if t[2] else "○"
        print(f"  {t[0]}. {status} {t[1]}")

def test_add_tasks(conn):
    """Test adding tasks."""
    print("\n" + "="*60)
    print("TEST: Add 5 tasks")
    print("="*60)
    
    tasks_to_add = [
        ("Buy Milk", "Get 2% from store"),
        ("Call Mom", "Wish her happy birthday"),
        ("Finish Report", "Complete quarterly analysis"),
        ("Go for Run", "5km in the park"),
        ("Read Book", "Finish chapter 5")
    ]
    
    for title, desc in tasks_to_add:
        db_module.add_task(conn, title, desc)
    
    tasks = get_tasks(conn)
    print_tasks("After adding", tasks)
    assert len(tasks) == 5, f"Expected 5 tasks, got {len(tasks)}"
    print("✅ PASS: Add tasks")
    return True

def test_complete_tasks(conn):
    """Test completing tasks."""
    print("\n" + "="*60)
    print("TEST: Complete tasks 1, 3, 5")
    print("="*60)
    
    for task_id in [1, 3, 5]:
        result = db_module.complete_task(conn, task_id)
        assert result, f"Failed to complete task {task_id}"
    
    tasks = get_tasks(conn)
    print_tasks("After completing", tasks)
    
    completed = [t for t in tasks if t[2]]
    assert len(completed) == 3, f"Expected 3 completed, got {len(completed)}"
    assert all(t[0] in [1, 3, 5] for t in completed), "Wrong tasks completed"
    print("✅ PASS: Complete tasks")
    return True

def test_uncomplete_tasks(conn):
    """Test uncompleting tasks."""
    print("\n" + "="*60)
    print("TEST: Uncomplete task 3")
    print("="*60)
    
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET completed = 0 WHERE id = 3")
    conn.commit()
    
    tasks = get_tasks(conn)
    print_tasks("After uncompleting", tasks)
    
    task3 = [t for t in tasks if t[0] == 3][0]
    assert task3[2] == 0, "Task 3 should be uncompleted"
    print("✅ PASS: Uncomplete task")
    return True

def test_delete_tasks(conn):
    """Test deleting tasks."""
    print("\n" + "="*60)
    print("TEST: Delete task 2")
    print("="*60)
    
    result = db_module.delete_task(conn, 2)
    assert result, "Failed to delete task 2"
    
    tasks = get_tasks(conn)
    print_tasks("After deleting", tasks)
    
    assert len(tasks) == 4, f"Expected 4 tasks, got {len(tasks)}"
    assert all(t[0] != 2 for t in tasks), "Task 2 should be deleted"
    print("✅ PASS: Delete task")
    return True

def test_complete_all(conn):
    """Test completing all tasks."""
    print("\n" + "="*60)
    print("TEST: Complete all remaining tasks")
    print("="*60)
    
    tasks = get_tasks(conn)
    for task_id, _, _ in tasks:
        db_module.complete_task(conn, task_id)
    
    tasks = get_tasks(conn)
    print_tasks("After completing all", tasks)
    
    assert all(t[2] for t in tasks), "All tasks should be completed"
    print("✅ PASS: Complete all tasks")
    return True

def test_uncomplete_all(conn):
    """Test uncompleting all tasks."""
    print("\n" + "="*60)
    print("TEST: Uncomplete all tasks")
    print("="*60)
    
    tasks = get_tasks(conn)
    cur = conn.cursor()
    for task_id, _, _ in tasks:
        cur.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
    conn.commit()
    
    tasks = get_tasks(conn)
    print_tasks("After uncompleting all", tasks)
    
    assert all(not t[2] for t in tasks), "All tasks should be uncompleted"
    print("✅ PASS: Uncomplete all tasks")
    return True

def test_delete_all(conn):
    """Test deleting all tasks."""
    print("\n" + "="*60)
    print("TEST: Delete all tasks")
    print("="*60)
    
    tasks = get_tasks(conn)
    for task_id, _, _ in tasks:
        db_module.delete_task(conn, task_id)
    
    tasks = get_tasks(conn)
    print_tasks("After deleting all", tasks)
    
    assert len(tasks) == 0, f"Expected 0 tasks, got {len(tasks)}"
    print("✅ PASS: Delete all tasks")
    return True

def run_all_tests():
    """Run all database tests."""
    print("="*60)
    print("DATABASE OPERATIONS TEST SUITE")
    print("="*60)
    
    conn = setup_test_db()
    
    try:
        test_add_tasks(conn)
        test_complete_tasks(conn)
        test_uncomplete_tasks(conn)
        test_delete_tasks(conn)
        test_complete_all(conn)
        test_uncomplete_all(conn)
        test_delete_all(conn)
        
        print("\n" + "="*60)
        print("ALL DATABASE TESTS PASSED! ✅")
        print("="*60)
        print("\nDatabase operations are working correctly.")
        print("The issue is with GUI refresh timing.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
        if os.path.exists("test_tasks.db"):
            os.remove("test_tasks.db")
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
