"""Tests for base + specialty skill rules."""

from __future__ import annotations

import unittest

from pulse.models import assign_skill_dots, ensure_skill, new_character
from pulse.skills import effective_specialty_rating, validate_skill_allocation


class TestSkillTree(unittest.TestCase):
    def test_effective_rating_includes_base_dots(self) -> None:
        character = new_character()
        reaction = ensure_skill(character, "Reaction", kind="base")
        athletics = ensure_skill(character, "Athletics", kind="specialty")
        assign_skill_dots(reaction, 2, skill_name="Reaction")
        assign_skill_dots(athletics, 1, skill_name="Athletics")
        self.assertEqual(effective_specialty_rating(character, "Athletics"), 3)

    def test_equivalent_allocations_same_effective(self) -> None:
        a = new_character()
        assign_skill_dots(ensure_skill(a, "Athletics", kind="specialty"), 3, skill_name="Athletics")

        b = new_character()
        assign_skill_dots(ensure_skill(b, "Reaction", kind="base"), 2, skill_name="Reaction")
        assign_skill_dots(ensure_skill(b, "Athletics", kind="specialty"), 1, skill_name="Athletics")

        self.assertEqual(
            effective_specialty_rating(a, "Athletics"),
            effective_specialty_rating(b, "Athletics"),
        )

    def test_base_skill_capped_at_two(self) -> None:
        character = new_character()
        entry = ensure_skill(character, "Reaction", kind="base")
        assign_skill_dots(entry, 3, skill_name="Reaction")
        self.assertEqual(entry["dots"], 2)

    def test_effective_cap_validation(self) -> None:
        character = new_character()
        assign_skill_dots(ensure_skill(character, "Reaction", kind="base"), 2, skill_name="Reaction")
        assign_skill_dots(ensure_skill(character, "Athletics", kind="specialty"), 4, skill_name="Athletics")
        errors = validate_skill_allocation(character)
        self.assertTrue(any("effective rating exceeds" in e.lower() for e in errors))


if __name__ == "__main__":
    unittest.main()
