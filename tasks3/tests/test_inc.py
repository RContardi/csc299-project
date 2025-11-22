# tasks3/tests/test_inc.py

from tasks3.src.__init__ import inc

def test_inc():
    """Test the inc function as required by [2025-11-05 Wed] milestone."""
    assert inc(5) == 6
