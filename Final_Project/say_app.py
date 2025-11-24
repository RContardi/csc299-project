"""Small GUI launcher for the Task Manager `say` command.

This script opens a tiny Tkinter window where the user can type a natural
language instruction like "put buy a 2 liter container of milk on my tasks"
and the script will invoke the Python CLI module to add the task.

Run with: python say_app.py
"""
from __future__ import annotations

import subprocess
import sys
import os
import tkinter as tk
from tkinter import messagebox, font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from task_manager import db as db_module
from task_manager import cli as cli_module
try:
    from task_manager import ai as ai_module
except Exception:
    ai_module = None

import json

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".task_manager_config.json")


def send_text_to_cli(text: str) -> tuple[int, str, str]:
    """Invoke the task manager CLI with the `say` subcommand.

    Returns a tuple of (returncode, stdout, stderr).
    """
    if not text.strip():
        return 1, "", "empty input"
    # Call the current Python interpreter to ensure the environment is correct
    proc = subprocess.run([
        sys.executable,
        "-m",
        "main",
        "say",
        text,
    ], capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def on_submit(entry: tk.Entry, title_var: tk.StringVar, desc_var: tk.StringVar, root: tk.Tk) -> None:
    """Add the task using the current preview title and description.

    This writes to the CLI (same behavior as before) and clears the main entry
    on success.
    """
    t = title_var.get().strip()
    d = desc_var.get().strip() or None
    if not t:
        messagebox.showwarning("Empty title", "Task title is empty. Please enter a task.")
        return

    args = [sys.executable, "-m", "main", "add", t]
    if d:
        args += ["--description", d]
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode == 0:
        messagebox.showinfo("Task added", proc.stdout.strip() or "Task added")
        entry.delete(0, tk.END)
        # clear preview
        title_var.set("")
        desc_var.set("")
    else:
        messagebox.showerror("Error", f"Return code {proc.returncode}\n{proc.stderr}")


def main() -> None:
    root = tk.Tk()
    root.title("Task Assistant - Prototype 01")
    # larger, modern size
    root.geometry("640x260")

    # Use ttk for a cleaner look
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=11)

    pad = 12
    container = ttk.Frame(root, padding=pad)
    container.pack(fill="both", expand=True)

    heading_row = ttk.Frame(container)
    heading_row.pack(fill="x")

    heading = ttk.Label(heading_row, text="Task Assistant - Prototype 01", font=(default_font.actual().get("family"), 14, "bold"))
    heading.pack(side="left", anchor="w")

    # Settings button + AI status on the right
    controls = ttk.Frame(heading_row)
    controls.pack(side="right")

    ai_status_var = tk.StringVar(value="AI: disabled")

    def load_config() -> dict:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_config(cfg: dict) -> None:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception as e:
            _ = e  # ignore for now

    def open_settings():
        win = tk.Toplevel(root)
        win.title("Settings")
        win.geometry("520x160")
        ttk.Label(win, text="OpenAI API Key (optional)").pack(anchor="w", padx=12, pady=(12, 0))
        key_var = tk.StringVar()
        existing = None
        if ai_module is not None:
            existing = getattr(ai_module, "OPENAI_KEY", None)
        if not existing:
            cfg = load_config()
            existing = cfg.get("openai_api_key")
        if existing:
            key_var.set(existing)

        entry = ttk.Entry(win, textvariable=key_var, width=80, show="*")
        entry.pack(fill="x", padx=12, pady=(6, 6))

        note = ttk.Label(win, text="The key will be stored in your home directory (~/.task_manager_config.json). Treat it like a secret.")
        note.pack(fill="x", padx=12, pady=(0, 8))

        btns = ttk.Frame(win)
        btns.pack(fill="x", padx=12, pady=(8, 12))

        def on_save():
            k = key_var.get().strip() or None
            if ai_module is not None:
                try:
                    ai_module.set_api_key(k)
                except Exception:
                    pass
            cfg = load_config()
            if k:
                cfg["openai_api_key"] = k
            else:
                cfg.pop("openai_api_key", None)
            save_config(cfg)
            ai_status_var.set("AI: enabled" if k else "AI: disabled")
            win.destroy()

        def on_clear():
            key_var.set("")

        def on_test():
            # Test the provided key (do not save)
            if ai_module is None:
                messagebox.showwarning("Not available", "AI module not available (install openai package).")
                return
            k = key_var.get().strip() or None
            success, msg = ai_module.test_api_key(k)
            if success:
                messagebox.showinfo("Key test", "Key appears valid: OK")
            else:
                messagebox.showerror("Key test failed", f"Test call failed: {msg}")

        ttk.Button(btns, text="Save", command=on_save).pack(side="right")
        ttk.Button(btns, text="Test", command=on_test).pack(side="right", padx=(0, 8))
        ttk.Button(btns, text="Clear", command=on_clear).pack(side="right", padx=(0, 8))

    settings_btn = ttk.Button(controls, text="Settings", command=open_settings)
    settings_btn.pack(side="right", padx=(8, 0))

    ai_label = ttk.Label(controls, textvariable=ai_status_var)
    ai_label.pack(side="right")

    sub = ttk.Label(container, text="Chat with your tasks!")
    sub.pack(anchor="w", pady=(0, 8))

    # Initialize AI status from saved config or module
    try:
        cfg0 = load_config()
        saved_key = cfg0.get("openai_api_key")
        if saved_key and ai_module is not None:
            try:
                ai_module.set_api_key(saved_key)
                ai_status_var.set("AI: enabled")
            except Exception:
                ai_status_var.set("AI: disabled")
        elif getattr(ai_module, "OPENAI_KEY", None):
            ai_status_var.set("AI: enabled")
    except Exception:
        pass

    # Conversation area
    convo = ScrolledText(container, height=10, state="disabled", wrap="word")
    convo.pack(fill="both", expand=True)

    input_frame = ttk.Frame(container)
    input_frame.pack(fill="x", pady=(8, 0))

    entry = ttk.Entry(input_frame)
    entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    entry.focus()

    def append_message(sender: str, text: str):
        convo.configure(state="normal")
        convo.insert("end", f"{sender}: {text}\n")
        convo.see("end")
        convo.configure(state="disabled")

    def format_tasks():
        # show tasks from the default DB file
        db_path = os.environ.get("TASK_MANAGER_DB", "tasks.db")
        conn = db_module.sqlite3.connect(db_path)
        try:
            db_module.initialize(conn)
            tasks = db_module.list_tasks(conn)
        finally:
            conn.close()
        if not tasks:
            return "No tasks."
        lines = []
        for t in tasks:
            status = "✓" if t.completed else " "
            desc = f" - {t.description}" if t.description else ""
            lines.append(f"[{status}] {t.id}: {t.title}{desc}")
        return "\n".join(lines)

    def handle_user(text: str):
        append_message("You", text)
        # simple intent detection
        txt = text.strip().lower()
        if txt in ("list", "show tasks", "show my tasks", "what are my tasks", "show tasks please") or txt.startswith("show") and "task" in txt:
            result = format_tasks()
            append_message("Assistant", result)
            return

        # complete or remove commands
        if txt.startswith("complete ") or txt.startswith("done "):
            parts = txt.split()
            try:
                tid = int(parts[1])
                db_path = os.environ.get("TASK_MANAGER_DB", "tasks.db")
                conn = db_module.sqlite3.connect(db_path)
                try:
                    ok = db_module.complete_task(conn, tid)
                finally:
                    conn.close()
                if ok:
                    append_message("Assistant", f"Task {tid} marked complete.")
                else:
                    append_message("Assistant", f"Task {tid} not found.")
            except Exception:
                append_message("Assistant", "I couldn't parse the id to complete.")
            return

        if txt.startswith("remove ") or txt.startswith("delete "):
            parts = txt.split()
            try:
                tid = int(parts[1])
                db_path = os.environ.get("TASK_MANAGER_DB", "tasks.db")
                conn = db_module.sqlite3.connect(db_path)
                try:
                    ok = db_module.delete_task(conn, tid)
                finally:
                    conn.close()
                if ok:
                    append_message("Assistant", f"Task {tid} removed.")
                else:
                    append_message("Assistant", f"Task {tid} not found.")
            except Exception:
                append_message("Assistant", "I couldn't parse the id to remove.")
            return

        # Otherwise, try AI parser if enabled
        use_ai = bool(os.environ.get("TASK_MANAGER_USE_AI")) and ai_module is not None
        title = description = None
        if use_ai:
            try:
                # prefer runtime-set key in ai_module.OPENAI_KEY; parse_with_ai accepts api_key if needed
                parsed = ai_module.parse_with_ai(text)
                if parsed and parsed.get("title"):
                    title = parsed.get("title")
                    description = parsed.get("description")
            except Exception:
                title = None

        if not title:
            title, description = cli_module.parse_natural_text(text)

        # Add the task to DB
        db_path = os.environ.get("TASK_MANAGER_DB", "tasks.db")
        conn = db_module.sqlite3.connect(db_path)
        try:
            db_module.initialize(conn)
            task = db_module.add_task(conn, title, description)
        finally:
            conn.close()
        append_message("Assistant", f"Added task {task.id}: {task.title}")

    def on_send():
        txt = entry.get().strip()
        if not txt:
            return
        entry.delete(0, tk.END)
        handle_user(txt)

    send_btn = ttk.Button(input_frame, text="Send", command=on_send)
    send_btn.pack(side="right")

    def on_enter(event):
        on_send()

    entry.bind("<Return>", on_enter)

    root.mainloop()


if __name__ == "__main__":
    main()
