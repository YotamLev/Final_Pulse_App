"""Tests for power selection and persistence."""

from __future__ import annotations

import unittest

from pulse.powers import available_powers
from pulse.vampire import (
    known_discipline_names,
    non_predator_powers,
    predator_powers,
    set_predator_powers,
    sync_non_predator_power,
    upsert_non_predator_power,
)
from tests.support import (
    level_0_character,
    level_1_ready_character,
    level_2_ready_character,
    minimal_mortal_character,
)


class TestAvailablePowers(unittest.TestCase):
    def test_keep_power_id_retains_current_slot_pick(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        v = character["vampire"]
        second = non_predator_powers(v)[1]
        sources = known_discipline_names(character)
        options = available_powers(
            character,
            allowed_sources=sources,
            include_amalgams=True,
            keep_power_id=second["id"],
        )
        self.assertIn(second["id"], {p["id"] for p in options})

    def test_exclude_known_drops_saved_power_without_keep(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        v = character["vampire"]
        second = non_predator_powers(v)[1]
        sources = known_discipline_names(character)
        options = available_powers(
            character,
            allowed_sources=sources,
            include_amalgams=True,
        )
        self.assertNotIn(second["id"], {p["id"] for p in options})


class TestWizardPowerPersistence(unittest.TestCase):
    def test_complete_character_keeps_four_chosen_powers(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        v = character["vampire"]
        non_pred = non_predator_powers(v)
        pred = predator_powers(v)
        self.assertEqual(len(non_pred), 3)
        self.assertEqual(len(pred), 1)
        self.assertEqual(non_pred[0]["id"], "dominate_draw_on_instinct")
        self.assertEqual(non_pred[1]["id"], "protean_animorph")
        self.assertEqual(non_pred[2]["id"], "fortitude_rapid_healing")
        self.assertEqual(pred[0]["id"], "potence_vigor")

    def test_revisit_slot_does_not_swap_power_when_unchanged(self) -> None:
        character = minimal_mortal_character()
        level_0_character(character)
        v = character["vampire"]
        first = non_predator_powers(v)[0]
        from pulse.powers import power_by_id

        power = power_by_id(first["id"])
        assert power is not None
        sync_non_predator_power(v, 0, power, 0)
        self.assertEqual(non_predator_powers(v)[0]["id"], first["id"])

    def test_set_predator_powers_empty_entries_preserves_existing(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        v = character["vampire"]
        before = [p["id"] for p in predator_powers(v)]
        set_predator_powers(v, [])
        after = [p["id"] for p in predator_powers(v)]
        self.assertEqual(before, after)

    def test_upsert_rejects_skipping_slots(self) -> None:
        v = {"powers": []}
        entry = {
            "id": "x",
            "name": "X",
            "source": "Dominate",
            "acquired_at_level": 2,
            "is_predator_power": False,
        }
        with self.assertRaises(ValueError):
            upsert_non_predator_power(v, 2, entry)


if __name__ == "__main__":
    unittest.main()
