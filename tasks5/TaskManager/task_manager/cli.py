"""Command-line interface for the task manager.

This module exposes a `run` function that accepts an argv list and an optional
database path to make the CLI easily unit-testable.
"""
import argparse
import os
import sqlite3
import sys
from typing import List, Optional

from . import db as db_module
try:
    from . import ai as ai_module
except Exception:
    ai_module = None

import re


DEFAULT_DB = "tasks.db"


def _get_conn(db_path: str) -> sqlite3.Connection:
    """Open and initialize the database connection.

    Args:
        db_path: Path to the SQLite database file.
    Returns:
        An initialized sqlite3.Connection.
    """
    conn = sqlite3.connect(db_path)
    db_module.initialize(conn)
    return conn


def _cmd_add(args: argparse.Namespace, conn: sqlite3.Connection) -> int:
    task = db_module.add_task(conn, args.title, args.description)
    print(f"Added task {task.id}: {task.title}")
    return 0


def _cmd_list(args: argparse.Namespace, conn: sqlite3.Connection) -> int:
    tasks = db_module.list_tasks(conn)
    if not tasks:
        print("No tasks.")
        return 0
    use_color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    def _color(text: str, code: str) -> str:
        if not use_color:
            return text
        return f"\x1b[{code}m{text}\x1b[0m"

    for t in tasks:
        status_char = "✓" if t.completed else " "
        # green for completed, dim for pending when colors enabled
        if t.completed:
            status = _color(status_char, "32")
        else:
            status = _color(status_char, "2")
        desc = f" - {t.description}" if t.description else ""
        print(f"[{status}] {t.id}: {t.title}{desc}")
    return 0


def _cmd_search(args: argparse.Namespace, conn: sqlite3.Connection) -> int:
    tasks = db_module.search_tasks(conn, args.keyword)
    if not tasks:
        print("No matches.")
        return 0
    use_color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    def _color(text: str, code: str) -> str:
        if not use_color:
            return text
        return f"\x1b[{code}m{text}\x1b[0m"

    for t in tasks:
        status_char = "✓" if t.completed else " "
        status = _color(status_char, "32") if t.completed else _color(status_char, "2")
        print(f"[{status}] {t.id}: {t.title}")
    return 0


def parse_natural_text(text: str) -> tuple[str, Optional[str]]:
    """Parse a simple natural-language task description into title and description.
    """
    # Normalize whitespace
    s = text.strip()
    s = re.sub(r"\s+", " ", s)

    # Work with a lowercase copy for matching but preserve original for capitalization
    s_lower = s.lower()

    # Common leading verbs/phrases we expect the user to use — capture content after them
    lead_re = r"^(?:please\s+)?(?:put|add|please put|please add|remind me to|remind me|create|i want to|i'd like to|i want|add to my list)\s+"

    content = None
    m = re.search(rf"{lead_re}(.+?)\s+(?:to|on)\s+(?:my\s+)?tasks\b", s_lower)
    if m:
        content = m.group(1).strip()
    else:
        m2 = re.search(rf"{lead_re}(.+)$", s_lower)
        if m2:
            content = m2.group(1).strip()

    # If no leading verb matched, try to strip trailing 'on my tasks' etc.
    if content is None:
        content = re.sub(r"\s+(?:to|on)\s+(?:my\s+)?tasks\b", "", s_lower).strip()

    # Extract quantity/measure phrases for description
    description: Optional[str] = None
    qty_match = re.search(r"(\d+\s*(?:liters|liter|l|ml|grams|g|kg|oz|ounce|ounces|packs|pack))", content)
    if qty_match:
        description = qty_match.group(1)
        content = (content[:qty_match.start()] + content[qty_match.end():]).strip()
        # remove trailing punctuation left over after removing quantity
        content = re.sub(r"[\,\;:\s]+$", "", content)

    # If a comma separates a short description, use that
    if "," in content and description is None:
        parts = [p.strip() for p in content.split(",", 1)]
        if parts[1]:
            content, description = parts[0], parts[1]

    # Remove leading articles
    content = re.sub(r"^(a |an |the )", "", content).strip()

    # Capitalize each major word for the title
    title = " ".join(w.capitalize() for w in content.split()) if content else ""

    # Final cleanup: if title empty, fallback to original trimmed sentence
    if not title:
        title = s.strip().capitalize()

    return title, description
def _cmd_complete(args: argparse.Namespace, conn: sqlite3.Connection) -> int:
    ok = db_module.complete_task(conn, args.task_id)
    if ok:
        print(f"Task {args.task_id} marked complete.")
        return 0
    print(f"Task {args.task_id} not found.")
    return 1
    print(f"Task {args.task_id} not found.")
    return 1


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser for the CLI.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(prog="task-manager")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add a task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("--description", help="Task description", default=None)

    sub.add_parser("list", help="List all tasks")

    p_search = sub.add_parser("search", help="Search tasks by keyword")
    p_search.add_argument("keyword", help="Search keyword")

    p_complete = sub.add_parser("complete", help="Mark task complete")
    p_complete.add_argument("task_id", type=int, help="ID of task to mark complete")

    p_say = sub.add_parser("say", help="Add a task using natural language")
    p_say.add_argument("text", nargs="+", help="Natural language text describing the task")

    sub.add_parser("shell", help="Start interactive shell (one-line multiple commands allowed)")

    return parser


def run(argv: Optional[List[str]] = None, db_path: Optional[str] = None) -> int:
    """Run the CLI.

    Args:
        argv: Optional list of command-line arguments (for testing).
        db_path: Optional path to the SQLite database file.
    Returns:
        Exit code integer.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    if db_path is None:
        db_path = DEFAULT_DB
    conn = _get_conn(db_path)
    try:
        if args.command == "add":
            return _cmd_add(args, conn)
        if args.command == "list":
            return _cmd_list(args, conn)
        if args.command == "search":
            return _cmd_search(args, conn)
        if args.command == "complete":
            return _cmd_complete(args, conn)
        if args.command == "say":
            # join the text tokens into a single sentence
            text = " ".join(args.text)
            use_ai = bool(os.environ.get("TASK_MANAGER_USE_AI")) and ai_module is not None
            title = description = None
            if use_ai:
                try:
                    parsed = ai_module.parse_with_ai(text)
                    if parsed and parsed.get("title"):
                        title = parsed.get("title")
                        description = parsed.get("description")
                except Exception:
                    title = None
            if not title:
                title, description = parse_natural_text(text)
            # mimic add args
            class A: pass

            a = A()
            a.title = title
            a.description = description
            return _cmd_add(a, conn)
        if args.command == "shell":
            return run_shell(conn)
        parser.print_help()
        return 0
    finally:
        conn.close()


def process_line(line: str, conn: sqlite3.Connection) -> None:
    """Process a single-line containing one or more semicolon-separated commands.

    Supported commands: add, remove/delete, complete, list, search, say
    Examples:
      add Buy milk, 2 liters; remove 3
      list; add Do homework
    """
    parts = [p.strip() for p in line.split(";") if p.strip()]
    for cmd in parts:
        # split command name
        if not cmd:
            continue
        tokens = cmd.split()
        verb = tokens[0].lower()
        rest = cmd[len(tokens[0]):].strip()

        if verb in ("add",):
            # allow comma to separate title and description
            title = rest
            description = None
            if "," in rest:
                tparts = [p.strip() for p in rest.split(",", 1)]
                title, description = tparts[0], tparts[1]
            # delegate to db
            task = db_module.add_task(conn, title, description)
            print(f"Added task {task.id}: {task.title}")

        elif verb in ("remove", "delete"):
            try:
                tid = int(rest.split()[0])
            except Exception:
                print(f"Invalid id for remove: '{rest}'")
                continue
            ok = db_module.delete_task(conn, tid)
            if ok:
                print(f"Removed task {tid}.")
            else:
                print(f"Task {tid} not found.")

        elif verb == "complete":
            try:
                tid = int(rest.split()[0])
            except Exception:
                print(f"Invalid id for complete: '{rest}'")
                continue
            ok = db_module.complete_task(conn, tid)
            if ok:
                print(f"Task {tid} marked complete.")
            else:
                print(f"Task {tid} not found.")

        elif verb == "list":
            _cmd_list(argparse.Namespace(), conn)

        elif verb == "search":
            # rest is keyword
            _cmd_search(argparse.Namespace(keyword=rest), conn)

        elif verb == "say":
            title, description = parse_natural_text(rest)
            t = db_module.add_task(conn, title, description)
            print(f"Added task {t.id}: {t.title}")

        else:
            print(f"Unknown command: {verb}")


def run_shell(conn: sqlite3.Connection) -> int:
    """Run a simple REPL shell that accepts semicolon-separated commands."""
    try:
        while True:
            try:
                line = input("task-manager> ")
            except EOFError:
                print()
                break
            cmd = line.strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit"):
                break
            process_line(cmd, conn)
    except KeyboardInterrupt:
        print()
    return 0
