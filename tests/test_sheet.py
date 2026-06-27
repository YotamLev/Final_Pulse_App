"""Tests for HTML character sheet export."""

from __future__ import annotations

import unittest

from pulse.powers import power_by_id
from pulse.sheet import format_level_up_summary, format_power_html, render_character_sheet
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

    def test_level_up_log_on_sheet(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        v = character["vampire"]
        v["level"] = 4
        v["level_ups"] = [
            {"to_level": 3, "choice": "skills", "details": {"Stealth": 1, "Athletics": 1}},
            {
                "to_level": 4,
                "choice": "power",
                "details": {"id": "fortitude_rapid_healing"},
            },
        ]
        html_out = render_character_sheet(character)
        self.assertIn("Level-up log", html_out)
        self.assertIn("+1 Stealth", html_out)
        self.assertIn("Rapid Healing", html_out)

    def test_format_level_up_summary_specialties(self) -> None:
        summary = format_level_up_summary(
            {
                "to_level": 5,
                "choice": "specialties",
                "details": {
                    "specialties": [
                        {"skill": "Stealth", "text": "shadows"},
                        {"skill": "Brawl", "text": "bar fights"},
                    ]
                },
            }
        )
        self.assertIn("Stealth (shadows)", summary)
        self.assertIn("Brawl (bar fights)", summary)


if __name__ == "__main__":
    unittest.main()
