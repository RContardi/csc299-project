"""Tests for the natural language parser used by the `say` command."""
import unittest

from task_manager.cli import parse_natural_text


class TestParser(unittest.TestCase):
    def test_simple_add(self):
        title, desc = parse_natural_text("add Do Homework to my tasks")
        self.assertEqual(title, "Do Homework")
        self.assertIsNone(desc)

    def test_with_quantity(self):
        title, desc = parse_natural_text("put buy a 2 liter container of milk on my tasks")
        # Title should focus on the item, description should capture quantity
        self.assertIn("Milk", title)
        self.assertIsNotNone(desc)

    def test_comma_description(self):
        title, desc = parse_natural_text("add buy milk, 2 liters")
        self.assertEqual(title, "Buy Milk")
        self.assertEqual(desc, "2 liters")

    def test_plain_sentence(self):
        title, desc = parse_natural_text("do laundry")
        self.assertEqual(title, "Do Laundry")


if __name__ == "__main__":
    unittest.main()
