"""Tests for character model helpers."""

from __future__ import annotations

import unittest

from pulse.models import _migrate_wizard_step


class TestWizardStepMigration(unittest.TestCase):
    def test_old_skill_pool_steps_map_to_skills(self) -> None:
        self.assertEqual(_migrate_wizard_step(4), 4)
        self.assertEqual(_migrate_wizard_step(5), 4)
        self.assertEqual(_migrate_wizard_step(7), 4)

    def test_old_mortal_tail_renumbered(self) -> None:
        self.assertEqual(_migrate_wizard_step(8), 5)
        self.assertEqual(_migrate_wizard_step(11), 8)

    def test_old_vampire_steps_renumbered_without_forget_step(self) -> None:
        self.assertEqual(_migrate_wizard_step(12), 9)
        self.assertEqual(_migrate_wizard_step(17), 14)
        self.assertEqual(_migrate_wizard_step(18), 14)
        self.assertEqual(_migrate_wizard_step(19), 15)
        self.assertEqual(_migrate_wizard_step(20), 16)


if __name__ == "__main__":
    unittest.main()
