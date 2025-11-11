# tasks1/task_manager.py

import json
import argparse
import os

DATA_FILE = "tasks.json"

def load_tasks():
    """Loads tasks from the JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    """Saves tasks to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def add_task(description):
    """Adds a new task."""
    tasks = load_tasks()
    # Find the next available ID
    new_id = max([t['id'] for t in tasks] + [0]) + 1
    tasks.append({'id': new_id, 'description': description, 'done': False})
    save_tasks(tasks)
    print(f"Task {new_id} added: '{description}'")

def list_tasks():
    """Lists all stored tasks."""
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    print("\n--- Current Tasks ---")
    for task in tasks:
        status = "[DONE]" if task['done'] else "[TODO]"
        print(f"[{task['id']}] {status} {task['description']}")
    print("---------------------")

def search_tasks(keyword):
    """Searches tasks by keyword."""
    tasks = load_tasks()
    # Filter tasks where the keyword appears in the description
    results = [t for t in tasks if keyword.lower() in t['description'].lower()]
    
    if not results:
        print(f"No tasks found matching '{keyword}'.")
        return
    print(f"\n--- Search Results for '{keyword}' ---")
    for task in results:
        status = "[DONE]" if task['done'] else "[TODO]"
        print(f"[{task['id']}] {status} {task['description']}")
    print("--------------------------------------")

def main():
    """Handles command-line arguments."""
    parser = argparse.ArgumentParser(description="A basic JSON-based task manager prototype.")
    subparsers = parser.add_subparsers(dest='command')

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('description', type=str, help='The task description')

    # List command
    subparsers.add_parser('list', help='List all tasks')

    # Search command
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
