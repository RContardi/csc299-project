"""
Automated test suite for Stride AI and Task Manager synchronization.
Tests various commands and verifies task manager stays in sync with Stride's state.
"""

import sqlite3
import time
from typing import List, Tuple

def get_tasks_from_db(db_path: str = "tasks.db") -> List[Tuple]:
    """Get current tasks from database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, title, completed FROM tasks ORDER BY id")
    tasks = cur.fetchall()
    conn.close()
    return tasks

def print_task_state(label: str, tasks: List[Tuple]):
    """Print current task state."""
    print(f"\n{label}:")
    if not tasks:
        print("  No tasks")
    else:
        for task_id, title, completed in tasks:
            status = "✓" if completed else "○"
            print(f"  {task_id}. {status} {title}")

def wait_for_user_action(test_name: str, command: str):
    """Prompt user to perform action in Stride."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Please type in Stride: \"{command}\"")
    input("Press ENTER after Stride responds and task manager updates...")

def verify_sync(test_name: str, expected_count: int = None, expected_completed: int = None):
    """Verify task manager state after action."""
    tasks = get_tasks_from_db()
    print_task_state("Task Manager State", tasks)
    
    total = len(tasks)
    completed = sum(1 for _, _, c in tasks if c)
    pending = total - completed
    
    print(f"\nStatistics: {total} total, {completed} completed, {pending} pending")
    
    if expected_count is not None and total != expected_count:
        print(f"❌ FAIL: Expected {expected_count} tasks, found {total}")
        return False
    
    if expected_completed is not None and completed != expected_completed:
        print(f"❌ FAIL: Expected {expected_completed} completed, found {completed}")
        return False
    
    print(f"✅ PASS: {test_name}")
    return True

def run_test_suite():
    """Run comprehensive test suite."""
    print("="*60)
    print("STRIDE AI + TASK MANAGER SYNCHRONIZATION TEST SUITE")
    print("="*60)
    print("\nThis test will verify that the task manager always matches")
    print("Stride's internal task list after every command.\n")
    input("Press ENTER to start testing...")
    
    # Test 1: Clear all tasks
    wait_for_user_action("Clear All Tasks", "remove all tasks")
    if not verify_sync("Clear All Tasks", expected_count=0):
        return False
    
    # Test 2: Add 10 random tasks
    wait_for_user_action("Add 10 Random Tasks", "add 10 random tasks")
    if not verify_sync("Add 10 Random Tasks", expected_count=10, expected_completed=0):
        return False
    
    # Test 3: Complete 3 tasks
    wait_for_user_action("Complete 3 Tasks", "complete 3 random tasks")
    if not verify_sync("Complete 3 Tasks", expected_count=10, expected_completed=3):
        return False
    
    # Test 4: Complete all tasks
    wait_for_user_action("Complete All Tasks", "complete all tasks")
    if not verify_sync("Complete All Tasks", expected_count=10, expected_completed=10):
        return False
    
    # Test 5: Uncomplete 5 tasks
    wait_for_user_action("Uncomplete 5 Tasks", "uncomplete 5 tasks")
    if not verify_sync("Uncomplete 5 Tasks", expected_count=10, expected_completed=5):
        return False
    
    # Test 6: Delete 3 tasks
    wait_for_user_action("Delete 3 Tasks", "delete 3 random tasks")
    if not verify_sync("Delete 3 Tasks", expected_count=7):
        return False
    
    # Test 7: Add single task
    wait_for_user_action("Add Single Task", "add buy groceries")
    if not verify_sync("Add Single Task", expected_count=8):
        return False
    
    # Test 8: Complete specific task
    wait_for_user_action("Complete Specific Task", "complete task 1")
    tasks = get_tasks_from_db()
    task1_completed = any(t[0] == 1 and t[2] == 1 for t in tasks)
    if not task1_completed:
        print("❌ FAIL: Task 1 should be completed")
        return False
    print("✅ PASS: Complete Specific Task")
    
    # Test 9: Uncomplete all
    wait_for_user_action("Uncomplete All Tasks", "uncomplete all tasks")
    if not verify_sync("Uncomplete All Tasks", expected_completed=0):
        return False
    
    # Test 10: Remove all
    wait_for_user_action("Remove All Tasks", "remove all tasks")
    if not verify_sync("Remove All Tasks", expected_count=0):
        return False
    
    # Test 11: Add 5 tasks with descriptions
    wait_for_user_action("Add Tasks with Descriptions", "add 5 tasks with detailed descriptions")
    tasks = get_tasks_from_db()
    if len(tasks) != 5:
        print(f"❌ FAIL: Expected 5 tasks, found {len(tasks)}")
        return False
    print("✅ PASS: Add Tasks with Descriptions")
    
    # Test 12: Complete half
    wait_for_user_action("Complete Half", "complete half of the tasks")
    tasks = get_tasks_from_db()
    completed = sum(1 for _, _, c in tasks if c)
    if completed < 2 or completed > 3:
        print(f"❌ FAIL: Expected 2-3 completed, found {completed}")
        return False
    print("✅ PASS: Complete Half")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✅")
    print("="*60)
    print("Task manager successfully stays in sync with Stride AI!")
    return True

if __name__ == "__main__":
    try:
        success = run_test_suite()
        if not success:
            print("\n⚠️  TESTS FAILED - Fix required before retesting")
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
