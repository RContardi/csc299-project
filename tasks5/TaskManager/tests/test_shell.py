"""Tests for the interactive single-line shell parsing."""
import sqlite3
import unittest
from io import StringIO
import sys

from task_manager import cli, db


class TestShell(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        db.initialize(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def capture(self, line: str):
        old = sys.stdout
        sys.stdout = StringIO()
        try:
            cli.process_line(line, self.conn)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = old

    def test_add_and_remove_same_line(self):
        out = self.capture("add Buy milk, 2 liters; add Do Homework; remove 1")
        # Should add two tasks and remove task 1
        self.assertIn("Added task", out)
        self.assertIn("Removed task 1", out)
        tasks = db.list_tasks(self.conn)
        # After removing id 1, only one task should remain
        self.assertEqual(len(tasks), 1)


if __name__ == "__main__":
    unittest.main()
