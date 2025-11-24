"""Additional DB edge-case tests for the task manager.

These tests cover behaviour such as completing a non-existent task and
ensuring created_at is timezone-aware.
"""
import sqlite3
import unittest
from datetime import timezone

from task_manager import db


class TestDBEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        db.initialize(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_complete_nonexistent(self):
        # Completing a non-existent task should return False
        ok = db.complete_task(self.conn, 9999)
        self.assertFalse(ok)

    def test_created_at_is_timezone_aware(self):
        t = db.add_task(self.conn, "TZ Test", None)
        tasks = db.list_tasks(self.conn)
        self.assertEqual(len(tasks), 1)
        created = tasks[0].created_at
        # Should carry tzinfo (UTC)
        self.assertIsNotNone(created.tzinfo)
        self.assertEqual(created.utcoffset(), timezone.utc.utcoffset(created))

    def test_empty_title_allowed(self):
        # Database schema allows empty string (NOT NULL only), ensure it persists
        t = db.add_task(self.conn, "", "empty title")
        self.assertIsNotNone(t.id)
        tasks = db.list_tasks(self.conn)
        self.assertEqual(tasks[0].title, "")


if __name__ == "__main__":
    unittest.main()
