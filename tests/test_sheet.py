"""Tests for HTML character sheet export."""

from __future__ import annotations

import unittest

from pulse.powers import power_by_id
from pulse.sheet import format_power_html, render_character_sheet
from tests.support import level_2_ready_character, minimal_mortal_character


class TestPowerSheetFormatting(unittest.TestCase):
    def test_includes_full_description_and_mechanics(self) -> None:
        power_def = power_by_id("dominate_draw_on_instinct")
        assert power_def is not None
        html_out = format_power_html(
            {
                "id": "dominate_draw_on_instinct",
                "name": "Draw On Instinct",
                "source": "Dominate",
                "is_predator_power": True,
            },
            power_def,
        )
        self.assertIn("Draw On Instinct", html_out)
        self.assertIn("Cost: Free for use against mortals", html_out)
        self.assertIn("Roll: Charisma", html_out)
        self.assertIn("more difficult by 2.", html_out)
        self.assertIn("If chosen as predator power:", html_out)

    def test_complete_character_sheet_lists_power_details(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        html_out = render_character_sheet(character)
        self.assertIn("Rapid Healing", html_out)
        self.assertIn("power-block", html_out)
        self.assertIn("Vigor", html_out)


if __name__ == "__main__":
    unittest.main()
