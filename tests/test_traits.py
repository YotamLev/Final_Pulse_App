"""Tests for trait suggestion helpers."""

from __future__ import annotations

import unittest

from pulse.data_loader import load_trait_suggestions
from pulse.ui.mortal_steps import (
    _filtered_attributes,
    _filtered_suggestion_labels,
    _trait_pick_label,
    _trait_suggestion_labels,
)


class TestTraitHelpers(unittest.TestCase):
    def test_pick_label_matches_suggestion(self) -> None:
        suggestions = load_trait_suggestions()
        brawny = next(s for s in suggestions if s["name"] == "Brawny")
        label = _trait_pick_label(brawny, suggestions)
        self.assertEqual(label, "Brawny (+Strength/−Dexterity)")

    def test_pick_label_custom_when_unknown(self) -> None:
        suggestions = load_trait_suggestions()
        label = _trait_pick_label({"name": "Smart", "plus": "Intelligence", "minus": "Manipulation"}, suggestions)
        self.assertEqual(label, "— custom —")

    def test_suggestion_labels_include_custom(self) -> None:
        suggestions = load_trait_suggestions()
        labels = _trait_suggestion_labels(suggestions)
        self.assertEqual(labels[0], "— custom —")
        self.assertIn("Confident (+Charisma/−Wits)", labels)

    def test_filtered_suggestions_exclude_used_attributes(self) -> None:
        suggestions = load_trait_suggestions()
        used = {"Strength", "Dexterity"}
        labels = _filtered_suggestion_labels(suggestions, used)
        self.assertNotIn("Brawny (+Strength/−Dexterity)", labels)
        self.assertIn("— custom —", labels)

    def test_filtered_suggestions_keep_current_pick(self) -> None:
        suggestions = load_trait_suggestions()
        used = {"Strength", "Dexterity"}
        labels = _filtered_suggestion_labels(
            suggestions,
            used,
            current_pick="Brawny (+Strength/−Dexterity)",
        )
        self.assertIn("Brawny (+Strength/−Dexterity)", labels)

    def test_filtered_attributes_exclude_used_and_opposite_pole(self) -> None:
        used = {"Charisma", "Wits"}
        plus_options = _filtered_attributes(used, exclude="Manipulation", current="Intelligence")
        self.assertNotIn("Charisma", plus_options)
        self.assertNotIn("Wits", plus_options)
        self.assertNotIn("Manipulation", plus_options)
        self.assertIn("Intelligence", plus_options)


if __name__ == "__main__":
    unittest.main()
