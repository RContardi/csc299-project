"""Entrypoint for the task manager application.

This module launches the GUI by default, but can run the CLI if --cli flag is provided.
"""
import sys

from task_manager import cli
from gui import main as gui_main


def main() -> int:
    """Main entrypoint.

    Returns an exit code integer for use by the calling process.
    """
    # Check if user wants CLI mode
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Remove --cli flag and pass remaining args to CLI
        return cli.run(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] not in ["--help", "-h"]:
        # If there are arguments but not --cli, assume CLI mode for backwards compatibility
        return cli.run(sys.argv[1:])
    else:
        # Launch GUI
        gui_main()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
