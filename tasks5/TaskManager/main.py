"""Entrypoint for the task manager CLI.

This module delegates to `task_manager.cli.run` and is designed to be run as a
module (python -m main ...).
"""
import sys

from task_manager import cli


def main() -> int:
    """Main entrypoint.

    Returns an exit code integer for use by the calling process.
    """
    return cli.run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
