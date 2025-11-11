# tasks3/src/__init__.py

import sqlite3
import argparse
import sys

# Define the default database name
DB_NAME = "tasks.db" 

# --- Database Setup (MODIFIED FOR TESTING) ---

# The function now accepts an optional db_name argument, allowing tests 
# to pass in ':memory:' for a temporary, isolated database.
def get_db_connection(db_name=DB_NAME): 
    """Creates a connection and ensures the tasks table exists."""
    
    conn = sqlite3.connect(db_name)
    
    # Initialize the required tasks table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0 
        );
    ''')
    conn.commit()
    return conn

# --- CRUD Operations ---

# This function is MODIFIED to accept the connection object from tests.
def add_task(description, conn=None): 
    """Adds a new task to the SQLite database."""
    
    # Use provided connection for testing, or establish default connection
    if conn is None:
        conn = get_db_connection()
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (description) VALUES (?)", 
        (description,)
    )
    task_id = cursor.lastrowid
    conn.commit()
    
    # CRITICAL FIX: We removed the faulty conn.database check here.
    # We rely on Pytest to manage the lifespan of the mock connection.
    
    # The requirement asks for console output
    print(f"Task {task_id} added: '{description}'")

def list_tasks():
    """Lists all stored tasks."""
    conn = get_db_connection()
    # ERROR IS HERE: The string must be fully enclosed
    tasks = conn.execute("SELECT id, description, done FROM tasks ORDER BY id ASC").fetchall()
    conn.close()
