"""Tests for power extraction helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from extract_powers import detect_predator_bonus  # noqa: E402


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
