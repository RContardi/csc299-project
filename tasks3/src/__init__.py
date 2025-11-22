# tasks3/src/__init__.py

import sqlite3
import argparse
import sys

# Define the default database name
DB_NAME = "tasks.db" 

# --- inc function (required by milestone) ---
def inc(n: int) -> int:
    """Increments an integer by 1."""
    return n + 1

# --- Database Setup (MODIFIED FOR TESTING) ---

def get_db_connection(db_name=DB_NAME): 
    """Creates a connection and ensures the tasks table exists."""
    conn = sqlite3.connect(db_name)
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

def add_task(description, conn=None): 
    """Adds a new task to the SQLite database."""
    if conn is None:
        conn = get_db_connection()
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (description) VALUES (?)", 
        (description,)
    )
    task_id = cursor.lastrowid
    conn.commit()
    print(f"Task {task_id} added: '{description}'")

def list_tasks():
    """Lists all stored tasks."""
    conn = get_db_connection()
    tasks = conn.execute("SELECT id, description, done FROM tasks ORDER BY id ASC").fetchall()
    conn.close()
    
    if not tasks:
        print("No tasks found.")
        return
    print("\n--- Current Tasks ---")
    for task_id, desc, done in tasks:
        status = "[DONE]" if done else "[TODO]"
        print(f"[{task_id}] {status} {desc}")
    print("---------------------")

def search_tasks(keyword):
    """Searches tasks by keyword."""
    conn = get_db_connection()
    tasks = conn.execute(
        "SELECT id, description, done FROM tasks WHERE description LIKE ? ORDER BY id ASC",
        (f"%{keyword}%",)
    ).fetchall()
    conn.close()
    
    if not tasks:
        print(f"No tasks found matching '{keyword}'.")
        return
    print(f"\n--- Search Results for '{keyword}' ---")
    for task_id, desc, done in tasks:
        status = "[DONE]" if done else "[TODO]"
        print(f"[{task_id}] {status} {desc}")
    print("--------------------------------------")

def main():
    """Entry point for 'uv run tasks3'."""
    parser = argparse.ArgumentParser(description="Tasks3 PKMS/task manager with pytest.")
    subparsers = parser.add_subparsers(dest='command')

    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('description', type=str, help='The task description')

    subparsers.add_parser('list', help='List all tasks')

    parser_search = subparsers.add_parser('search', help='Search tasks by keyword')
    parser_search.add_argument('keyword', type=str, help='The keyword to search for')

    args = parser.parse_args()

    if args.command == 'add':
        add_task(args.description)
    elif args.command == 'list':
        list_tasks()
    elif args.command == 'search':
        search_tasks(args.keyword)
    elif args.command is None:
        parser.print_help()
