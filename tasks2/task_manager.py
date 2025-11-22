# tasks2/task_manager.py
# Iteration on tasks1: migrated from JSON to SQLite for better scalability

import sqlite3
import argparse
import os

DB_NAME = "tasks.db"

def get_db_connection():
    """Creates a connection to the SQLite database and initializes the schema."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        );
    ''')
    conn.commit()
    return conn

def add_task(description):
    """Adds a new task."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
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
    """Handles command-line arguments."""
    parser = argparse.ArgumentParser(description="SQLite-based task manager (Tasks 2 iteration).")
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

if __name__ == '__main__':
    main()
