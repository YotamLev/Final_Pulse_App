"""Tests for vampire creation and level-up validation."""

from __future__ import annotations

import unittest

from pulse.powers import has_predator_bonus, power_by_id
from pulse.vampire_validation import validate_level_up, validate_wizard_step
from tests.support import (
    embrace_character,
    level_0_character,
    level_1_ready_character,
    level_2_ready_character,
    minimal_mortal_character,
    predator_ready_character,
)


class TestPredatorBonusFlag(unittest.TestCase):
    def test_draw_on_instinct_has_predator_bonus(self) -> None:
        power = power_by_id("dominate_draw_on_instinct")
        self.assertIsNotNone(power)
        assert power is not None
        self.assertTrue(power.get("predator_bonus"))
        self.assertIn("predator_bonus_text", power)
        self.assertTrue(has_predator_bonus(power))

    def test_power_without_bonus(self) -> None:
        power = power_by_id("protean_back_to_basics")
        self.assertIsNotNone(power)
        assert power is not None
        self.assertFalse(power.get("predator_bonus"))
        self.assertFalse(has_predator_bonus(power))


class TestEmbraceValidation(unittest.TestCase):
    def test_step_12_requires_mortal_complete_and_clan(self) -> None:
        character = minimal_mortal_character()
        errors = validate_wizard_step(character, 9)
        self.assertIn("Choose a clan.", errors)

    def test_step_12_valid_veneris(self) -> None:
        character = minimal_mortal_character()
        embrace_character(character, "veneris")
        errors = validate_wizard_step(character, 9)
        self.assertEqual(errors, [])

    def test_step_12_ventrue_requires_bane_fields(self) -> None:
        character = minimal_mortal_character()
        embrace_character(character, "ventrue")
        errors = validate_wizard_step(character, 9)
        self.assertTrue(any("bane field" in e.lower() for e in errors))


class TestLevel0Validation(unittest.TestCase):
    def test_requires_discipline_and_power(self) -> None:
        character = minimal_mortal_character()
        embrace_character(character)
        errors = validate_wizard_step(character, 10)
        self.assertIn("Choose your first Discipline.", errors)
        self.assertIn("Choose your first Discipline power.", errors)

    def test_valid_level_0(self) -> None:
        character = minimal_mortal_character()
        level_0_character(character)
        self.assertEqual(validate_wizard_step(character, 10), [])


class TestLevel1Validation(unittest.TestCase):
    def test_attributes_must_total_two(self) -> None:
        character = minimal_mortal_character()
        level_0_character(character)
        errors = validate_wizard_step(character, 11)
        self.assertTrue(any("exactly 2 attribute dots" in e for e in errors))

    def test_second_discipline_must_differ(self) -> None:
        character = minimal_mortal_character()
        level_0_character(character)
        v = character["vampire"]
        v["attribute_adjustments"] = [{"level": 1, "changes": {"Strength": 2}}]
        v["disciplines"].append({"name": "Dominate", "source": "clan", "acquired_at_level": 1})
        errors = validate_wizard_step(character, 12)
        self.assertIn("Second Discipline must differ from the first.", errors)

    def test_valid_level_1_discipline_step(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        self.assertEqual(validate_wizard_step(character, 12), [])


class TestPredatorValidation(unittest.TestCase):
    def test_predator_requires_package(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        errors = validate_wizard_step(character, 13)
        self.assertIn("Choose a predator type.", errors)

    def test_valid_predator(self) -> None:
        character = minimal_mortal_character()
        predator_ready_character(character)
        self.assertEqual(validate_wizard_step(character, 13), [])

    def test_predator_skill_cannot_exceed_cap(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        character["mortal"]["skills"]["Brawl"]["dots"] = 5
        v = character["vampire"]
        v["predator"] = {
            "source": "curated",
            "type": "alleycat",
            "skill_choice": {"skill": "Brawl", "dots": 2},
            "specialty": {"skill": "Brawl", "text": "back alleys"},
        }
        errors = validate_wizard_step(character, 13)
        self.assertTrue(any("exceeds maximum" in e for e in errors))

    def test_predator_skill_any_skill_with_room_valid(self) -> None:
        character = minimal_mortal_character()
        level_1_ready_character(character)
        v = character["vampire"]
        v["predator"] = {
            "source": "curated",
            "type": "alleycat",
            "skill_choice": {"skill": "Firearms", "dots": 2},
            "specialty": {"skill": "Firearms", "text": "concealed carry"},
        }
        v["powers"].append(
            {
                "id": "potence_vigor",
                "name": "Vigor",
                "source": "Potence",
                "acquired_at_level": 1,
                "is_predator_power": True,
            }
        )
        self.assertEqual(validate_wizard_step(character, 13), [])

    def test_leech_requires_two_powers_same_discipline(self) -> None:
        character = minimal_mortal_character()
        predator_ready_character(character)
        v = character["vampire"]
        v["predator"]["type"] = "leech"
        v["powers"] = [p for p in v["powers"] if not p.get("is_predator_power")]
        v["powers"].extend(
            [
                {
                    "id": "dominate_draw_on_instinct",
                    "name": "Draw On Instinct",
                    "source": "Dominate",
                    "acquired_at_level": 1,
                    "is_predator_power": True,
                },
                {
                    "id": "dominate_mesmerize",
                    "name": "Mesmerize",
                    "source": "Presence",
                    "acquired_at_level": 1,
                    "is_predator_power": True,
                },
            ]
        )
        errors = validate_wizard_step(character, 13)
        self.assertIn("Leech predator powers must be from the same Discipline.", errors)


class TestLevel2Validation(unittest.TestCase):
    def test_skill_removal_must_total_two(self) -> None:
        character = minimal_mortal_character()
        predator_ready_character(character)
        errors = validate_wizard_step(character, 14)
        self.assertTrue(any("Remove exactly 2 skill dots" in e for e in errors))

    def test_complete_creation_valid(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        self.assertEqual(validate_wizard_step(character, 17), [])


class TestLevelUpValidation(unittest.TestCase):
    def test_requires_creation_complete(self) -> None:
        character = minimal_mortal_character()
        level_0_character(character)
        errors = validate_level_up(character, "attr", {"attribute": "Strength", "dots": 1})
        self.assertIn("Complete character creation before leveling up.", errors)

    def test_attr_at_max_blocked(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        v = character["vampire"]
        v["attribute_adjustments"].append({"level": 99, "changes": {"Strength": 3}})
        errors = validate_level_up(character, "attr", {"attribute": "Strength", "dots": 1})
        self.assertTrue(any("maximum" in e.lower() for e in errors))

    def test_skills_must_total_two(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        errors = validate_level_up(character, "skills", {"Athletics": 1})
        self.assertIn("Assign exactly 2 skill dots.", errors)

    def test_valid_skill_level_up(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        errors = validate_level_up(character, "skills", {"Occult": 1, "Politics": 1})
        self.assertEqual(errors, [])

    def test_skill_level_up_over_cap_blocked(self) -> None:
        character = minimal_mortal_character()
        level_2_ready_character(character)
        character["mortal"]["skills"]["Stealth"] = {"dots": 5, "category": "Physical", "pools": {}}
        errors = validate_level_up(character, "skills", {"Stealth": 2})
        self.assertTrue(any("Stealth would exceed maximum (7 > 5)" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
