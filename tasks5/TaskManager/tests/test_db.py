"""Unit tests for the database layer of the task manager.

These tests use an in-memory SQLite database to ensure isolation and speed.
"""
import sqlite3
import unittest

from task_manager import db


class TestDB(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        db.initialize(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_add_and_list(self):
        t = db.add_task(self.conn, "Test", "Desc")
        self.assertIsNotNone(t.id)
        tasks = db.list_tasks(self.conn)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Test")

    def test_search(self):
        db.add_task(self.conn, "Buy milk", "Get 2 liters")
        db.add_task(self.conn, "Read book", "Fiction")
        res = db.search_tasks(self.conn, "milk")
        self.assertEqual(len(res), 1)
        self.assertIn("Buy milk", [r.title for r in res])

    def test_complete(self):
        t = db.add_task(self.conn, "Task", None)
        ok = db.complete_task(self.conn, t.id)
        self.assertTrue(ok)
        tasks = db.list_tasks(self.conn)
        self.assertTrue(tasks[0].completed)


if __name__ == "__main__":
    unittest.main()
