"""Tests for mortal validation."""

from __future__ import annotations

import unittest

from pulse.constants import TOTAL_SKILL_DOTS
from pulse.models import assign_skill_dots, ensure_skill, new_character
from pulse.validation import validate_step


class TestSkillValidation(unittest.TestCase):
    def test_skills_require_exactly_22_dots(self) -> None:
        character = new_character()
        character["chronicle"]["time_and_place"] = "Test"
        entry = ensure_skill(character, "Athletics", "Physical")
        assign_skill_dots(entry, 5)
        errors = validate_step(character, 4)
        self.assertTrue(any(f"{TOTAL_SKILL_DOTS}" in e for e in errors))

    def test_skills_reject_more_than_five_dots(self) -> None:
        character = new_character()
        character["chronicle"]["time_and_place"] = "Test"
        entry = ensure_skill(character, "Athletics", "Physical")
        entry["dots"] = 6
        errors = validate_step(character, 4)
        self.assertTrue(any("cannot exceed 5" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
