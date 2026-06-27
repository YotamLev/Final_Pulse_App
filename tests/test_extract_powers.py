"""Tests for power extraction helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from extract_powers import detect_predator_bonus, parse_power_body  # noqa: E402


class TestPowerBodyParsing(unittest.TestCase):
    def test_splits_mechanics_and_description(self) -> None:
        body = [
            "First paragraph of the power.",
            "Second paragraph with more detail.",
            "Cost: 1 Liter",
            "Duration: a scene",
            "Roll: Manipulation vs Resolve",
            "If chosen as predator power: bonus text.",
        ]
        parsed = parse_power_body(body)
        self.assertEqual(parsed["summary"], "First paragraph of the power.")
        self.assertEqual(len(parsed["description"]), 2)
        self.assertIn("Second paragraph", parsed["description_text"])
        self.assertEqual(parsed["cost"], "Cost: 1 Liter")
        self.assertEqual(parsed["duration"], "Duration: a scene")
        self.assertEqual(parsed["roll"], "Roll: Manipulation vs Resolve")
        self.assertTrue(parsed["predator_bonus"])
        self.assertIn("bonus text", str(parsed["predator_bonus_text"]))


class TestPredatorBonusExtraction(unittest.TestCase):
    def test_detects_predator_power_line(self) -> None:
        body = [
            "Issue a simple command.",
            "If chosen as predator power: +2 dice bonus for the roll.",
        ]
        found, text = detect_predator_bonus(body)
        self.assertTrue(found)
        self.assertIn("+2 dice", text or "")

    def test_detects_predator_type_power_line(self) -> None:
        body = [
            "Can give an animal vitae.",
            "If chosen as predator type power: allows you to direct the animals.",
        ]
        found, text = detect_predator_bonus(body)
        self.assertTrue(found)
        self.assertIn("predator type power", text or "")

    def test_no_bonus_in_body(self) -> None:
        found, text = detect_predator_bonus(["A mundane power with no bonus clause."])
        self.assertFalse(found)
        self.assertIsNone(text)


if __name__ == "__main__":
    unittest.main()
