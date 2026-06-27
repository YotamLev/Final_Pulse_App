"""Tests for cap / dot computation helpers used by Streamlit widgets."""

from __future__ import annotations

import unittest

from pulse.caps import (
    attribute_adjustment_bounds,
    get_skill_dots,
    skill_dots_before_removal,
    skill_removal_bounds,
    SKILL_REMOVAL_BUDGET,
)
from tests.support import level_1_ready_character, minimal_mortal_character, predator_ready_character


class TestAttributeAdjustmentBounds(unittest.TestCase):
    def test_level_delta_not_double_counted_against_cap(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        changes = {"Strength": 1}
        base, max_assignable, assigned = attribute_adjustment_bounds(
            character, "Strength", level_changes=changes
        )
        self.assertEqual(assigned, 1)
        self.assertGreater(max_assignable, 0)
        self.assertEqual(base + assigned, base + 1)

    def test_budget_limits_second_attribute(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        changes = {"Strength": 1, "Dexterity": 1}
        _, max_strength, _ = attribute_adjustment_bounds(
            character, "Strength", level_changes=changes
        )
        self.assertEqual(max_strength, 1)

    def test_invalid_over_cap_assignment_clamps(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        character["mortal"]["attributes"]["Strength"] = 3
        changes = {"Strength": 3}
        base, max_assignable, assigned = attribute_adjustment_bounds(
            character, "Strength", level_changes=changes
        )
        self.assertLessEqual(assigned, max_assignable)
        self.assertLessEqual(base + assigned, 5)


class TestSkillRemovalBounds(unittest.TestCase):
    def setUp(self) -> None:
        self.character = minimal_mortal_character()
        predator_ready_character(self.character)
        self.character["mortal"]["skills"]["Brawl"]["dots"] = 5
        self.character["vampire"]["predator"]["skill_choice"] = {"skill": "Brawl", "dots": 2}

    def test_predator_bonus_clamped_before_removal_step(self) -> None:
        before = skill_dots_before_removal(self.character, 2)
        self.assertEqual(before["Brawl"], 5)

    def test_own_removal_not_subtracted_from_available_dots(self) -> None:
        removed = {"Brawl": 2}
        available, max_removable, value = skill_removal_bounds(
            self.character, "Brawl", removed=removed
        )
        self.assertEqual(available, 5)
        self.assertEqual(max_removable, 2)
        self.assertEqual(value, 2)
        self.assertLessEqual(value, max_removable)

    def test_over_assigned_removal_clamps_to_available(self) -> None:
        removed = {"Brawl": 5}
        available, max_removable, value = skill_removal_bounds(
            self.character, "Brawl", removed=removed
        )
        self.assertEqual(available, 5)
        self.assertEqual(max_removable, SKILL_REMOVAL_BUDGET)
        self.assertEqual(value, SKILL_REMOVAL_BUDGET)
        self.assertLessEqual(value, max_removable)

    def test_budget_exhausted_blocks_other_skills(self) -> None:
        removed = {"Athletics": 2}
        _, max_brawl, value = skill_removal_bounds(self.character, "Brawl", removed=removed)
        self.assertEqual(max_brawl, 0)
        self.assertEqual(value, 0)

    def test_partial_budget_shared_across_skills(self) -> None:
        removed = {"Athletics": 1}
        _, max_brawl, _ = skill_removal_bounds(self.character, "Brawl", removed=removed)
        self.assertEqual(max_brawl, 1)

    def test_get_skill_dots_applies_removals_after_step(self) -> None:
        self.character["vampire"]["skill_adjustments"] = [{"level": 2, "removed": {"Brawl": 2}}]
        before = skill_dots_before_removal(self.character, 2)["Brawl"]
        after = get_skill_dots(self.character)["Brawl"]
        self.assertEqual(before, 5)
        self.assertEqual(after, 3)

    def test_widget_safe_value_never_exceeds_max(self) -> None:
        """Regression: StreamlitValueAboveMaxError when value > max_value."""
        removed = {"Brawl": 4}
        for skill in skill_dots_before_removal(self.character, 2):
            if skill_dots_before_removal(self.character, 2)[skill] <= 0:
                continue
            _, max_removable, value = skill_removal_bounds(
                self.character, skill, removed=removed
            )
            self.assertLessEqual(value, max_removable, msg=f"{skill} value above max")


if __name__ == "__main__":
    unittest.main()
