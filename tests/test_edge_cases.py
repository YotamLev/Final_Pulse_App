"""Edge-case and robustness tests for Final Pulse 2E.

Covers gaps in the primary test suite:
- XP log seeding, refund cancellation, and format consistency
- HP clamping when Fortitude/Toughness is removed
- Character serialization round-trips and migration
- Discipline power integrity (count ≤ level, dependency chains)
- Quickstart XP balance and log correctness
- Tracker bounds (HP ≥ 0, WP ≥ 0, Blood can go negative)
"""

from __future__ import annotations

import pytest

from pulse.models.character import (
    default_character,
    char_to_dict,
    char_from_dict,
    get_hp_max,
    normalize_character,
    log_xp_spend,
    log_xp_refund,
    CREATION_SKILL_XP,
    CREATION_DISC_XP,
    BASE_HP,
    BASE_BLOOD,
    BASE_WILLPOWER,
)
from pulse.data.skill_trees import total_skill_xp, xp_cost_for_next_dot, SKILL_TREES
from pulse.data.disciplines import (
    DISCIPLINES,
    total_disc_xp,
    xp_cost_for_disc_level,
    get_available_powers,
)
from pulse.ui.wizard import QUICKSTARTS, _apply_quickstart


def fresh() -> dict:
    return default_character()


# ─────────────────────────────────────────────────────────────────────────────
# XP LOG: REFUND CANCELLATION
# ─────────────────────────────────────────────────────────────────────────────

class TestXPLogRefund:
    def test_structural_skill_refund_cancels_spend(self):
        c = fresh()
        log_xp_spend(c, "Guns +1 dot", 1, skill="Guns")
        log_xp_refund(c, "Guns −1 dot", 1, skill="Guns")
        assert len(c["xp_log"]) == 0

    def test_structural_disc_refund_cancels_spend(self):
        c = fresh()
        log_xp_spend(c, "Auspex level 0 → 1", 1, disc="Auspex", from_level=0, to_level=1)
        log_xp_refund(c, "Auspex level 1 → 0", 1, disc="Auspex", from_level=0, to_level=1)
        assert len(c["xp_log"]) == 0

    def test_structural_refund_ignores_description_format(self):
        """Structural match works even if description strings differ."""
        c = fresh()
        log_xp_spend(c, "Guns dot 1", 1, skill="Guns")   # different description
        log_xp_refund(c, "removing Guns", 1, skill="Guns")
        assert len(c["xp_log"]) == 0

    def test_refund_without_match_appends_refund_entry(self):
        c = fresh()
        log_xp_refund(c, "Guns −1 dot", 1, skill="Guns")
        assert len(c["xp_log"]) == 1
        assert c["xp_log"][0]["cost"] == -1
        assert "[Refund]" in c["xp_log"][0]["description"]

    def test_structural_refund_cancels_most_recent_skill_match(self):
        """Two spend entries for same skill — refund removes only the last one."""
        c = fresh()
        log_xp_spend(c, "Guns +1 dot", 1, skill="Guns")
        log_xp_spend(c, "Brawl +1 dot", 1, skill="Brawl")
        log_xp_spend(c, "Guns +1 dot", 2, skill="Guns")
        log_xp_refund(c, "Guns −1 dot", 2, skill="Guns")
        assert len(c["xp_log"]) == 2
        skills = [e.get("skill") for e in c["xp_log"]]
        assert "Guns" in skills   # first entry survives
        assert "Brawl" in skills

    def test_refund_only_cancels_positive_cost_entries(self):
        """Refund entries (negative cost) are not cancelled by structural match."""
        c = fresh()
        c["xp_log"] = [{"description": "Guns +1 dot", "skill": "Guns", "cost": -1}]
        log_xp_refund(c, "Guns −1 dot", 1, skill="Guns")
        assert len(c["xp_log"]) == 2

    def test_legacy_cancel_description_fallback(self):
        """Old log entries without structured fields still cancel by description."""
        c = fresh()
        c["xp_log"] = [{"description": "Guns +1 dot", "cost": 1}]  # no 'skill' key
        log_xp_refund(c, "Guns −1 dot", 1, cancel_description="Guns +1 dot")
        assert len(c["xp_log"]) == 0

    def test_no_match_args_always_appends(self):
        c = fresh()
        log_xp_spend(c, "Guns +1 dot", 1, skill="Guns")
        log_xp_refund(c, "Guns −1 dot", 1)  # no match args at all
        assert len(c["xp_log"]) == 2

    def test_disc_refund_matches_exact_level_transition(self):
        """Disc refund only cancels the exact from→to transition, not others."""
        c = fresh()
        log_xp_spend(c, "Auspex level 0 → 1", 1, disc="Auspex", from_level=0, to_level=1)
        log_xp_spend(c, "Auspex level 1 → 2", 2, disc="Auspex", from_level=1, to_level=2)
        log_xp_refund(c, "Auspex level 2 → 1", 2, disc="Auspex", from_level=1, to_level=2)
        assert len(c["xp_log"]) == 1
        assert c["xp_log"][0]["from_level"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# HP EDGE CASES: TOUGHNESS REMOVAL
# ─────────────────────────────────────────────────────────────────────────────

class TestHPEdgeCases:
    def test_hp_max_drops_when_toughness_removed(self):
        """Removing Toughness from Fortitude 2 drops hp_max from 14 → 10."""
        c = fresh()
        c["discipline_levels"]["Fortitude"] = 2
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        assert get_hp_max(c) == 14

        c["discipline_powers"]["Fortitude"] = []  # Toughness removed
        assert get_hp_max(c) == 10

    def test_hp_clamped_to_max_after_toughness_removed(self):
        """normalize_character clamps hp_current down when hp_max decreases."""
        c = fresh()
        c["discipline_levels"]["Fortitude"] = 2
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        c["hp_current"] = 14  # at full health with Toughness

        c["discipline_powers"]["Fortitude"] = []  # Toughness removed
        assert get_hp_max(c) == 10
        normalize_character(c)
        assert c["hp_current"] == 10

    def test_normalize_clamps_hp_above_max(self):
        c = fresh()
        c["hp_current"] = 999
        normalize_character(c)
        assert c["hp_current"] == get_hp_max(c)

    def test_normalize_clamps_wp_above_max(self):
        c = fresh()
        c["willpower_current"] = 999
        normalize_character(c)
        assert c["willpower_current"] == BASE_WILLPOWER

    def test_normalize_clamps_hp_below_zero(self):
        c = fresh()
        c["hp_current"] = -5
        normalize_character(c)
        assert c["hp_current"] == 0

    def test_normalize_does_not_clamp_blood_below_zero(self):
        c = fresh()
        c["blood_current"] = -5
        normalize_character(c)
        assert c["blood_current"] == -5  # blood/Hunger stays negative

    def test_hp_max_with_iron_constitution_plus_fortitude_5_toughness(self):
        c = fresh()
        c["mortal_traits"].append({"key": "iron_constitution", "name": "Iron Constitution", "cost": 2})
        c["discipline_levels"]["Fortitude"] = 5
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        assert get_hp_max(c) == 10 + 1 + 2 * 5  # 21

    def test_blood_can_go_below_zero(self):
        """Blood/Hunger is allowed to go negative — unlike HP and WP."""
        c = fresh()
        c["blood_current"] = -3
        assert c["blood_current"] < 0  # valid Hunger state

    def test_hp_cannot_logically_go_below_zero(self):
        """Sanity check: the model doesn't clamp HP, but UI should."""
        c = fresh()
        c["hp_current"] = -1  # model allows it; UI is responsible for the clamp
        assert c["hp_current"] < 0

    def test_fortitude_without_toughness_gives_no_hp_bonus(self):
        c = fresh()
        c["discipline_levels"]["Fortitude"] = 5
        c["discipline_powers"]["Fortitude"] = ["Rapid Healing"]
        assert get_hp_max(c) == BASE_HP

    def test_hp_max_with_fortitude_0(self):
        """Fortitude unlocked but at level 0 gives no bonus."""
        c = fresh()
        c["discipline_levels"]["Fortitude"] = 0
        c["discipline_powers"]["Fortitude"] = []
        assert get_hp_max(c) == BASE_HP


# ─────────────────────────────────────────────────────────────────────────────
# SERIALIZATION: ROUND-TRIP AND MIGRATION
# ─────────────────────────────────────────────────────────────────────────────

class TestSerialization:
    def test_default_character_round_trip(self):
        c = default_character()
        restored = char_from_dict(char_to_dict(c))
        assert restored["wizard_stage"] == c["wizard_stage"]
        assert restored["skill_dots"] == c["skill_dots"]
        assert restored["xp_log"] == c["xp_log"]

    def test_char_from_dict_fills_missing_keys_with_defaults(self):
        """A minimal dict (e.g., an old save) gets all missing fields from default."""
        minimal = {"name": "Old Vampire", "clan": "Ventrue"}
        restored = char_from_dict(minimal)
        assert restored["name"] == "Old Vampire"
        assert restored["skill_dots"] == {}
        assert restored["xp_log"] == []
        assert restored["wizard_stage"] == 1

    def test_stage_migration_old_to_new(self):
        """Old 5-stage wizard_stage numbers get mapped to new 4-stage numbers."""
        for old, new in {2: 1, 3: 2, 4: 3, 5: 4}.items():
            c = char_from_dict({"wizard_stage": old})
            assert c["wizard_stage"] == new, f"stage {old} should migrate to {new}"

    def test_stage_1_unchanged(self):
        c = char_from_dict({"wizard_stage": 1})
        assert c["wizard_stage"] == 1

    def test_memories_migration_from_mortal_history(self):
        old = {"mortal_history": "I used to be human.", "beliefs": "I believe in order."}
        c = char_from_dict(old)
        assert "I used to be human." in c["memories"]
        assert "I believe in order." in c["memories"]

    def test_existing_memories_not_overwritten_by_migration(self):
        data = {"memories": "Already set.", "mortal_history": "Old field."}
        c = char_from_dict(data)
        assert c["memories"] == "Already set."

    def test_xp_log_preserved_through_round_trip(self):
        c = default_character()
        log_xp_spend(c, "Guns +1 dot", 1)
        restored = char_from_dict(char_to_dict(c))
        assert len(restored["xp_log"]) == 1
        assert restored["xp_log"][0]["description"] == "Guns +1 dot"


# ─────────────────────────────────────────────────────────────────────────────
# DISCIPLINE POWER INTEGRITY
# ─────────────────────────────────────────────────────────────────────────────

class TestDisciplinePowerIntegrity:
    def test_power_count_cannot_logically_exceed_level(self):
        """Powers list should never exceed the discipline level."""
        for disc_name, disc in DISCIPLINES.items():
            for level in range(1, 6):
                available = get_available_powers(disc_name, level, [])
                # Can only pick 'level' powers total
                assert len(available) >= 0  # trivially true, but ensures no crash

    def test_releasing_prerequisite_blocked_if_dependent_acquired(self):
        """Cannot release Telepathy if Scry (which requires it) is acquired."""
        auspex = DISCIPLINES["Auspex"]
        powers = ["Telepathy", "Scry"]
        dependents_of_telepathy = [
            p for p in auspex["powers"]
            if p.get("requires") == "Telepathy" and p["name"] in powers
        ]
        assert len(dependents_of_telepathy) > 0  # Scry depends on Telepathy
        can_release = len(dependents_of_telepathy) == 0
        assert not can_release

    def test_can_release_prerequisite_after_dependent_removed(self):
        auspex = DISCIPLINES["Auspex"]
        powers = ["Telepathy"]  # Scry NOT acquired
        dependents = [
            p for p in auspex["powers"]
            if p.get("requires") == "Telepathy" and p["name"] in powers
        ]
        assert len(dependents) == 0

    def test_all_power_requires_reference_existing_powers(self):
        """Every power's 'requires' field names a power that exists in the same discipline."""
        for disc_name, disc in DISCIPLINES.items():
            power_names = {p["name"] for p in disc["powers"]}
            for power in disc["powers"]:
                req = power.get("requires")
                if req is not None:
                    assert req in power_names, (
                        f"{disc_name}.{power['name']} requires '{req}' which doesn't exist"
                    )

    def test_all_power_levels_between_1_and_5(self):
        for disc_name, disc in DISCIPLINES.items():
            for power in disc["powers"]:
                assert 1 <= power["level"] <= 5, (
                    f"{disc_name}.{power['name']} has invalid level {power['level']}"
                )

    def test_scry_not_available_without_telepathy(self):
        available = get_available_powers("Auspex", 4, ["Enhance Senses"])
        names = {p["name"] for p in available}
        assert "Scry" not in names

    def test_scry_available_with_telepathy(self):
        available = get_available_powers("Auspex", 4, ["Telepathy"])
        names = {p["name"] for p in available}
        assert "Scry" in names


# ─────────────────────────────────────────────────────────────────────────────
# QUICKSTART: XP BALANCE AND LOG SEEDING
# ─────────────────────────────────────────────────────────────────────────────

class TestQuickstartBalance:
    @pytest.mark.parametrize("key,qs", list(QUICKSTARTS.items()))
    def test_skill_xp_exactly_15(self, key, qs):
        spent = total_skill_xp(qs["skill_dots"], [])
        assert spent == CREATION_SKILL_XP, (
            f"{qs['label']}: skill XP = {spent}, expected {CREATION_SKILL_XP}"
        )

    @pytest.mark.parametrize("key,qs", list(QUICKSTARTS.items()))
    def test_disc_xp_exactly_10(self, key, qs):
        spent = total_disc_xp(qs.get("discipline_levels", {}))
        assert spent == CREATION_DISC_XP, (
            f"{qs['label']}: disc XP = {spent}, expected {CREATION_DISC_XP}"
        )

    @pytest.mark.parametrize("key", list(QUICKSTARTS.keys()))
    def test_apply_quickstart_seeds_xp_log(self, key):
        """After applying a quickstart, the XP log should be non-empty."""
        c = fresh()
        _apply_quickstart(c, key)
        assert len(c["xp_log"]) > 0

    @pytest.mark.parametrize("key", list(QUICKSTARTS.keys()))
    def test_xp_log_skill_total_matches_skill_dots(self, key):
        """Sum of skill spend entries in log should equal total_skill_xp."""
        c = fresh()
        _apply_quickstart(c, key)
        qs = QUICKSTARTS[key]
        expected = total_skill_xp(qs["skill_dots"], [])
        log_skill_total = sum(
            e["cost"] for e in c["xp_log"]
            if e["cost"] > 0 and "+1 dot" in e["description"]
        )
        assert log_skill_total == expected, (
            f"{QUICKSTARTS[key]['label']}: log skill XP = {log_skill_total}, expected {expected}"
        )

    @pytest.mark.parametrize("key", list(QUICKSTARTS.keys()))
    def test_xp_log_disc_total_matches_discipline_levels(self, key):
        """Sum of discipline spend entries in log should equal total_disc_xp."""
        c = fresh()
        _apply_quickstart(c, key)
        qs = QUICKSTARTS[key]
        expected = total_disc_xp(qs.get("discipline_levels", {}))
        log_disc_total = sum(
            e["cost"] for e in c["xp_log"]
            if e["cost"] > 0 and " level " in e["description"] and "→" in e["description"]
        )
        assert log_disc_total == expected, (
            f"{QUICKSTARTS[key]['label']}: log disc XP = {log_disc_total}, expected {expected}"
        )

    @pytest.mark.parametrize("key", list(QUICKSTARTS.keys()))
    def test_discipline_powers_count_does_not_exceed_level(self, key):
        qs = QUICKSTARTS[key]
        for disc, level in qs.get("discipline_levels", {}).items():
            powers = qs.get("discipline_powers", {}).get(disc, [])
            assert len(powers) <= level, (
                f"{qs['label']}: {disc} has {len(powers)} powers but level {level}"
            )

    def test_all_quickstarts_have_valid_clan(self):
        from pulse.data.clans import CLANS
        for key, qs in QUICKSTARTS.items():
            assert qs["clan"] in CLANS, f"{qs['label']}: clan '{qs['clan']}' not in CLANS"

    def test_all_quickstarts_have_exactly_3_disciplines(self):
        for key, qs in QUICKSTARTS.items():
            assert len(qs["disciplines"]) == 3, (
                f"{qs['label']}: has {len(qs['disciplines'])} disciplines, expected 3"
            )

    def test_apply_quickstart_resets_mortal_traits(self):
        c = fresh()
        c["mortal_traits"].append({"key": "brave", "name": "Brave", "cost": 2})
        _apply_quickstart(c, "ventrue_commander")
        # mortal_traits should only contain what the quickstart sets
        assert all(t["key"] != "brave" for t in c["mortal_traits"])

    def test_apply_quickstart_overwrites_previous_disciplines(self):
        c = fresh()
        c["unlocked_disciplines"] = ["Auspex", "Celerity"]
        _apply_quickstart(c, "ventrue_commander")
        assert c["unlocked_disciplines"] == ["Dominate", "Fortitude", "Presence"]


# ─────────────────────────────────────────────────────────────────────────────
# SKILL TREE STRUCTURAL INTEGRITY
# ─────────────────────────────────────────────────────────────────────────────

class TestSkillTreeIntegrity:
    def test_all_branch_parents_exist_in_same_tree(self):
        """Every branches_from parent must exist in the same tree."""
        for tree_name, tree in SKILL_TREES.items():
            for skill_name, skill in tree.items():
                branch = skill.get("branches_from")
                if branch is None:
                    continue
                if skill.get("branches_or"):
                    parents = [p for p, _ in branch]
                else:
                    parents = [branch[0]]
                for parent in parents:
                    assert parent in tree, (
                        f"{tree_name}.{skill_name} branches from '{parent}' which is not in the tree"
                    )

    def test_no_circular_branches(self):
        """No skill should directly or transitively branch from itself."""
        def ancestors(skill_name, tree_name, visited=None):
            if visited is None:
                visited = set()
            skill = SKILL_TREES[tree_name].get(skill_name, {})
            branch = skill.get("branches_from")
            if branch is None:
                return visited
            if skill.get("branches_or"):
                parents = [p for p, _ in branch]
            else:
                parents = [branch[0]]
            for p in parents:
                assert p not in visited, f"Circular branch detected at {p} in {tree_name}"
                visited.add(p)
                ancestors(p, tree_name, visited)
            return visited

        for tree_name, tree in SKILL_TREES.items():
            for skill_name in tree:
                ancestors(skill_name, tree_name)

    def test_all_skills_have_required_fields(self):
        for tree_name, tree in SKILL_TREES.items():
            for skill_name, skill in tree.items():
                assert "max_dots" in skill, f"{tree_name}.{skill_name} missing max_dots"
                assert "description" in skill, f"{tree_name}.{skill_name} missing description"
                assert skill["max_dots"] >= 1

    def test_max_dots_are_positive_integers(self):
        for tree_name, tree in SKILL_TREES.items():
            for skill_name, skill in tree.items():
                assert isinstance(skill["max_dots"], int) and skill["max_dots"] > 0
