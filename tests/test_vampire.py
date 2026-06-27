"""Tests for vampire model helpers."""

from __future__ import annotations

import unittest

from pulse.vampire import ensure_predator, new_vampire_state


class TestEnsurePredator(unittest.TestCase):
    def test_initializes_when_null(self) -> None:
        vampire = new_vampire_state()
        self.assertIsNone(vampire["predator"])
        predator = ensure_predator(vampire)
        self.assertEqual(predator["source"], "curated")
        self.assertIs(vampire["predator"], predator)

    def test_preserves_existing_predator(self) -> None:
        vampire = new_vampire_state()
        vampire["predator"] = {"source": "custom", "type": "custom", "custom_name": "Hunter"}
        predator = ensure_predator(vampire)
        self.assertEqual(predator["custom_name"], "Hunter")


if __name__ == "__main__":
    unittest.main()
