"""Unit tests for the CLI module.

Tests run commands against an in-memory database by passing `db_path` as
":memory:" through the `run` function.
"""
import os
import sqlite3
import sys
import tempfile
import unittest
from io import StringIO

from task_manager import cli


class TestCLI(unittest.TestCase):
    def setUp(self) -> None:
        # Use a temp file for the DB to allow separate connections
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)

    def tearDown(self) -> None:
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def _run_capture(self, argv):
        old = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = cli.run(argv, db_path=self.db_path)
            output = sys.stdout.getvalue()
            return rc, output
        finally:
            sys.stdout = old

    def test_add_and_list(self):
        rc, out = self._run_capture(["add", "CLI Task", "--description", "d"]) 
        self.assertEqual(rc, 0)
        self.assertIn("Added task", out)
        rc, out = self._run_capture(["list"]) 
        self.assertIn("CLI Task", out)

    def test_search_and_complete(self):
        self._run_capture(["add", "FindMe", "--description", "x"]) 
        rc, out = self._run_capture(["search", "FindMe"]) 
        self.assertIn("FindMe", out)
        # Get the id from list
        rc, out = self._run_capture(["list"]) 
        # assume id is 1
        rc, out = self._run_capture(["complete", "1"]) 
        self.assertIn("marked complete", out)


if __name__ == "__main__":
    unittest.main()
