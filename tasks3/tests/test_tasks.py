# tasks3/tests/test_tasks.py

import pytest
    
# Import the functions directly from the package
from tasks3.src.__init__ import get_db_connection, add_task

# --- Fixture to create an isolated, in-memory DB for every test ---
@pytest.fixture
def mock_db_connection():
    # This calls your modified function with the in-memory flag
    conn = get_db_connection(db_name=':memory:') 
    return conn

# --- Test 1: Test Adding a Task (Required Test) ---
def test_add_task_creates_entry(mock_db_connection):
    """Tests that a task is correctly added and stored in the database."""
    
    # Action: Add the task using the mock connection
    add_task("Verify basic task functionality", conn=mock_db_connection)
    
    # Verification: Check if the task exists in the database
    cursor = mock_db_connection.execute("SELECT description, done FROM tasks WHERE id = 1")
    result = cursor.fetchone()
    
    # Assertions
    assert result is not None
    assert result[0] == "Verify basic task functionality" # Description check
    assert result[1] == 0 # Default 'done' status check

# --- Test 2: Test Database Integrity (Required Test) ---
def test_database_table_exists_and_is_clean(mock_db_connection):
    """Tests that the database connection initializes the required table structure."""
    
    # Verification: Attempt to query the required columns
    cursor = mock_db_connection.execute("PRAGMA table_info(tasks);")
    columns = [row[1] for row in cursor.fetchall()] # Get column names
    
    # Assertions
    assert 'id' in columns
    assert 'description' in columns
    assert 'done' in columns
    assert len(columns) == 3 # Ensure only the required columns exist
