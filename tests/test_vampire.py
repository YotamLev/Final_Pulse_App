"""Tests for vampire model helpers."""

from __future__ import annotations

import unittest

from pulse.vampire import (
    ensure_predator,
    known_discipline_names,
    new_vampire_state,
    non_predator_powers,
    set_discipline_slot,
    set_predator_powers,
    upsert_non_predator_power,
)


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


class TestDisciplinePersistence(unittest.TestCase):
    def test_set_discipline_slot_preserves_other_slots(self) -> None:
        vampire = new_vampire_state()
        set_discipline_slot(vampire, 0, "Animalism", "clan", 0)
        set_discipline_slot(vampire, 1, "Protean", "clan", 1)
        set_discipline_slot(vampire, 0, "Dominate", "clan", 0)
        self.assertEqual(known_discipline_names({"vampire": vampire}), ["Dominate", "Protean"])

    def test_upsert_non_predator_preserves_predator_powers(self) -> None:
        vampire = new_vampire_state()
        vampire["powers"] = [
            {"id": "a", "name": "A", "source": "Animalism", "acquired_at_level": 0, "is_predator_power": False},
            {"id": "b", "name": "B", "source": "Potence", "acquired_at_level": 1, "is_predator_power": True},
        ]
        upsert_non_predator_power(
            vampire,
            0,
            {"id": "c", "name": "C", "source": "Animalism", "acquired_at_level": 0, "is_predator_power": False},
        )
        self.assertEqual(non_predator_powers(vampire)[0]["id"], "c")
        self.assertEqual(len([p for p in vampire["powers"] if p.get("is_predator_power")]), 1)

    def test_set_predator_powers_keeps_non_predator(self) -> None:
        vampire = new_vampire_state()
        vampire["powers"] = [
            {"id": "a", "name": "A", "source": "Animalism", "acquired_at_level": 0, "is_predator_power": False},
        ]
        set_predator_powers(
            vampire,
            [{"id": "b", "name": "B", "source": "Potence", "acquired_at_level": 1, "is_predator_power": True}],
        )
        self.assertEqual(len(non_predator_powers(vampire)), 1)
        self.assertEqual(vampire["powers"][-1]["id"], "b")


if __name__ == "__main__":
    unittest.main()
