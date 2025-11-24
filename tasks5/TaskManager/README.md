# Task Manager (Terminal)

A small terminal-based task manager written in Python using SQLite for data
persistence. It supports adding tasks, listing tasks, searching by keyword,
and marking tasks complete. The code is modular, includes docstrings, follows
PEP 8, and is unit-testable.

How to run
-----------

Run the CLI with Python:

```powershell
python -m main add "Buy milk" --description "2 liters"
python -m main list
python -m main search milk
python -m main complete 1
```

Run tests:

```powershell
python -m unittest discover -v

Install as a command-line application
-----------------------------------

You can install the project into your environment so it exposes a `task-manager` command.

PowerShell (editable/developer install):

```powershell
# from the project root
.\install.ps1
# then run
task-manager -h
```

Or install manually with pip:

```powershell
python -m pip install -e .
```

After installing, run the command directly:

```powershell
task-manager add "Buy milk" --description "2 liters"
task-manager list

Launcher utilities
------------------

If you'd like a small front-end that takes a natural-language sentence and
forwards it to the `say` command, there are two simple options provided:

- `say.ps1` — PowerShell launcher. Example:

```powershell
.\say.ps1 put buy a 2 liter container of milk on my tasks
```

This will call:

```powershell
python -m main say "put buy a 2 liter container of milk on my tasks"
```

- `say_app.py` — Tiny Tkinter GUI launcher. Run it with:

```powershell
python say_app.py
```

Type your instruction into the text field and press Add or Enter.

Both launchers simply forward the text to the existing `say` command and
preserve the same parsing behaviour.

Create a Desktop shortcut (Windows)
----------------------------------

To create a Desktop shortcut that launches the small GUI (without a console
window), run the included PowerShell helper from the project root:

```powershell
.\create_shortcut.ps1
```

This will create "Task Manager - Quick Add.lnk" on your Desktop and configure
it to launch `say_app.py` using `pythonw` if available (falls back to `python`).

```
```

Project layout
--------------

- `task_manager/` - package code
- `tests/` - unit tests
- `main.py` - CLI entrypoint
