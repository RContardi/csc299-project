"""CLI edge-case tests for the task manager.

These tests verify behavior when no command is provided, completing a
non-existent id, and searching with no matches.
"""
import os
import sys
import tempfile
import unittest
from io import StringIO

from task_manager import cli


class TestCLIEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
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

    def test_no_command_prints_help(self):
        rc, out = self._run_capture([])
        self.assertEqual(rc, 0)
        self.assertIn("usage", out.lower())

    def test_complete_invalid_id_returns_not_found(self):
        rc, out = self._run_capture(["complete", "42"])  # no tasks created
        self.assertEqual(rc, 1)
        self.assertIn("not found", out.lower())

    def test_search_no_matches_prints_message(self):
        rc, out = self._run_capture(["search", "nope"]) 
        self.assertEqual(rc, 0)
        self.assertIn("no matches", out.lower())


if __name__ == "__main__":
    unittest.main()
