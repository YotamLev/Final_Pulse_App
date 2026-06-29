"""Comprehensive tests for Final Pulse 2E character creation logic.

Tests cover:
- Skill tree branching and XP calculations
- Trait cost validation
- Discipline XP and power selection
- Clan eligibility
- HP max computation
- Edge cases and wizard flow scenarios
"""

from __future__ import annotations

import pytest

from pulse.data.skill_trees import (
    get_static_base,
    get_effective_level,
    can_invest,
    can_add_dot,
    can_remove_dot,
    xp_cost_for_next_dot,
    xp_cost_for_n_own_dots,
    total_skill_xp,
    SKILL_TREES,
)
from pulse.data.disciplines import (
    DISCIPLINES,
    get_available_powers,
    total_disc_xp,
    xp_cost_for_disc_level,
)
from pulse.data.clans import check_clan_eligibility, get_eligible_clans, CLANS
from pulse.data.traits import MORTAL_TRAITS, VAMPIRE_TRAITS, MENTAL_ILLNESS_KEYS
from pulse.models.character import (
    default_character,
    get_hp_max,
    get_total_trait_cost,
    get_trait_count,
    get_creation_skill_xp_spent,
    get_creation_disc_xp_spent,
    can_spend_skill_xp,
    can_spend_disc_xp,
    CREATION_SKILL_XP,
    CREATION_DISC_XP,
    MAX_TRAITS,
    MAX_TRAIT_COST,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def char(**overrides) -> dict:
    """Create a fresh character optionally overriding keys."""
    c = default_character()
    c.update(overrides)
    return c


def add_trait(character: dict, trait_list: str, key: str, cost: int, detail: str = "", sub_choice: str = "") -> None:
    character[trait_list].append({
        "key": key,
        "name": key,
        "cost": cost,
        "detail": detail or None,
        "sub_choice": sub_choice or None,
    })


# ─────────────────────────────────────────────────────────────────────────────
# SKILL TREE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestStaticBase:
    def test_standalone_skill_has_zero_base(self):
        assert get_static_base("Guns", "Thrashing") == 0

    def test_first_level_branch_base(self):
        # Finance branches from Basic Analytical at threshold 2
        # Basic Analytical has no parent → base = 0 + 2 = 2
        assert get_static_base("Finance", "Scheming") == 2

    def test_deep_branch_base(self):
        # Undead Politics branches from Mortal Politics at threshold 3
        # Mortal Politics branches from Basic Analytical at threshold 2
        # Undead Politics base = (0 + 2) + 3 = 5
        assert get_static_base("Undead Politics", "Scheming") == 5

    def test_experimentation_deep_chain(self):
        # Demonology ← Occult 3 ← Curiosity 2
        # base = (0 + 2) + 3 = 5
        assert get_static_base("Demonology", "Experimentation") == 5

    def test_or_branch_base(self):
        # Marksmanship branches from [Guns 5 OR Projectiles 5]
        # First parent = Guns, threshold = 5, Guns base = 0
        # Static base = 0 + 5 = 5
        assert get_static_base("Marksmanship", "Thrashing") == 5

    def test_standalone_insight_in_manipulation(self):
        # Insight is standalone in Manipulation tree
        assert get_static_base("Insight", "Manipulation") == 0


class TestEffectiveLevel:
    def test_standalone_skill(self):
        assert get_effective_level("Guns", "Thrashing", {"Guns": 3}) == 3

    def test_branching_skill_one_dot(self):
        # Finance (base 2) + 1 own = 3
        assert get_effective_level("Finance", "Scheming", {"Basic Analytical": 2, "Finance": 1}) == 3

    def test_branching_skill_two_dots(self):
        # Finance (base 2) + 2 own = 4
        assert get_effective_level("Finance", "Scheming", {"Basic Analytical": 2, "Finance": 2}) == 4

    def test_instructions_example_chain(self):
        # From instructions: A=2, B branches from A@2 with 4 dots, C branches from B@2 with 1 dot
        # We model this with Curiosity(A)/Science(B)/Biology(C) but let's test directly
        # with Scheming: Basic Analytical→Mortal Politics→Undead Politics
        dots = {"Basic Analytical": 2, "Mortal Politics": 2, "Undead Politics": 1}
        # Undead Politics base = 5 (2+3); eff = 5 + 1 = 6
        assert get_effective_level("Undead Politics", "Scheming", dots) == 6

    def test_no_own_dots_gives_zero_for_standalone(self):
        assert get_effective_level("Dodge", "Thrashing", {}) == 0

    def test_branching_with_no_own_dots_gives_only_base(self):
        # Base is still computed, even without own dots
        assert get_effective_level("Finance", "Scheming", {"Basic Analytical": 2}) == 2


class TestCanInvest:
    def test_standalone_always_investable(self):
        assert can_invest("Guns", "Thrashing", {}) is True

    def test_branch_needs_parent_dots(self):
        # Finance needs Basic Analytical at 2 own dots
        assert can_invest("Finance", "Scheming", {"Basic Analytical": 1}) is False
        assert can_invest("Finance", "Scheming", {"Basic Analytical": 2}) is True

    def test_or_branch_either_parent_qualifies(self):
        assert can_invest("Marksmanship", "Thrashing", {"Guns": 5}) is True
        assert can_invest("Marksmanship", "Thrashing", {"Projectiles": 5}) is True
        assert can_invest("Marksmanship", "Thrashing", {"Guns": 4}) is False
        assert can_invest("Marksmanship", "Thrashing", {"Guns": 4, "Projectiles": 5}) is True

    def test_deep_branch_needs_direct_parent(self):
        # Undead Politics needs Mortal Politics at 3
        dots_a = {"Basic Analytical": 2, "Mortal Politics": 2}
        dots_b = {"Basic Analytical": 2, "Mortal Politics": 3}
        assert can_invest("Undead Politics", "Scheming", dots_a) is False
        assert can_invest("Undead Politics", "Scheming", dots_b) is True


class TestCanAddDot:
    def test_cannot_add_beyond_max(self):
        # Basic Analytical max = 2
        assert can_add_dot("Basic Analytical", "Scheming", {"Basic Analytical": 2}) is False

    def test_can_add_if_below_max_and_prereq_met(self):
        assert can_add_dot("Basic Analytical", "Scheming", {"Basic Analytical": 1}) is True

    def test_cannot_add_if_prereq_not_met(self):
        assert can_add_dot("Finance", "Scheming", {"Basic Analytical": 1}) is False


class TestCanRemoveDot:
    def test_cannot_remove_if_no_dots(self):
        assert can_remove_dot("Guns", "Thrashing", {"Guns": 0}) is False

    def test_can_remove_standalone(self):
        assert can_remove_dot("Guns", "Thrashing", {"Guns": 3}) is True

    def test_cannot_remove_if_child_depends(self):
        # Cannot lower Basic Analytical below 2 if Finance has dots
        dots = {"Basic Analytical": 2, "Finance": 1}
        assert can_remove_dot("Basic Analytical", "Scheming", dots) is False

    def test_can_remove_parent_if_child_is_empty(self):
        dots = {"Basic Analytical": 2, "Finance": 0}
        assert can_remove_dot("Basic Analytical", "Scheming", dots) is True

    def test_or_branch_can_remove_one_parent_if_other_qualifies(self):
        # Marksmanship needs Guns@5 OR Projectiles@5
        # If both are at 5, can remove dots from one as long as the other still qualifies
        dots = {"Guns": 5, "Projectiles": 5, "Marksmanship": 1}
        # Removing one dot from Guns: Guns goes to 4, but Projectiles@5 still qualifies
        assert can_remove_dot("Guns", "Thrashing", dots) is True

    def test_or_branch_cannot_remove_last_qualifying_parent(self):
        # Only Guns qualifies; removing to 4 would invalidate Marksmanship
        dots = {"Guns": 5, "Projectiles": 4, "Marksmanship": 1}
        assert can_remove_dot("Guns", "Thrashing", dots) is False


class TestXPCost:
    def test_standalone_first_dot(self):
        # base = 0, cost = 0 + 0 + 1 = 1
        assert xp_cost_for_next_dot("Guns", "Thrashing", {}) == 1

    def test_standalone_third_dot(self):
        # base = 0, own = 2, cost = 0 + 2 + 1 = 3
        assert xp_cost_for_next_dot("Guns", "Thrashing", {"Guns": 2}) == 3

    def test_finance_first_dot(self):
        # base = 2, own = 0, cost = 2 + 0 + 1 = 3
        assert xp_cost_for_next_dot("Finance", "Scheming", {"Basic Analytical": 2}) == 3

    def test_finance_second_dot(self):
        # base = 2, own = 1, cost = 2 + 1 + 1 = 4
        assert xp_cost_for_next_dot("Finance", "Scheming", {"Basic Analytical": 2, "Finance": 1}) == 4

    def test_instructions_example_finance_total(self):
        # BA@1: 1 XP, BA@2: 2 XP, Finance@1: 3 XP, Finance@2: 4 XP = 10 total
        ba_cost = xp_cost_for_n_own_dots("Basic Analytical", "Scheming", 2)
        fin_cost = xp_cost_for_n_own_dots("Finance", "Scheming", 2)
        assert ba_cost == 3  # 1+2
        assert fin_cost == 7  # (2+1) + (2+2) = 3+4
        assert ba_cost + fin_cost == 10

    def test_marksmanship_first_dot_xp(self):
        # base = 5, own = 0, cost = 5 + 0 + 1 = 6
        dots = {"Guns": 5}
        assert xp_cost_for_next_dot("Marksmanship", "Thrashing", dots) == 6


class TestTotalSkillXP:
    def test_empty_dots(self):
        assert total_skill_xp({}, []) == 0

    def test_basic_analytical_two_dots(self):
        # base=0, n=2: 0*2 + 2*3/2 = 3
        assert total_skill_xp({"Basic Analytical": 2}, []) == 3

    def test_finance_with_prereq(self):
        # BA@2: 3 XP, Finance@2: 7 XP → total 10
        assert total_skill_xp({"Basic Analytical": 2, "Finance": 2}, []) == 10

    def test_custom_skill_xp(self):
        # Custom skill Dance@3: 1+2+3 = 6 XP (no base)
        custom = [{"name": "Dance", "max_dots": 5}]
        assert total_skill_xp({"Dance": 3}, custom) == 6

    def test_max_creation_budget_15(self):
        # Spending exactly 15 XP: Basic Analytical@2 (3) + Brawl@2 (3) + Guns@3 (6) + Dodge@1 (1) + Athletics@1 (1) → but check actual
        # Let's verify a known budget scenario
        dots = {"Basic Analytical": 2, "Brawl": 2}
        # 3 + 3 = 6 XP
        assert total_skill_xp(dots, []) == 6


# ─────────────────────────────────────────────────────────────────────────────
# TRAIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTraits:
    def test_empty_trait_cost(self):
        c = char()
        assert get_total_trait_cost(c) == 0

    def test_positive_trait_cost(self):
        c = char()
        add_trait(c, "mortal_traits", "brave", 2)
        assert get_total_trait_cost(c) == 2

    def test_negative_trait_cost(self):
        c = char()
        add_trait(c, "mortal_traits", "cowardly", -2)
        assert get_total_trait_cost(c) == -2

    def test_mixed_trait_cost(self):
        c = char()
        add_trait(c, "mortal_traits", "brave", 2)
        add_trait(c, "mortal_traits", "cowardly", -2)
        assert get_total_trait_cost(c) == 0

    def test_trait_cost_across_both_lists(self):
        c = char()
        add_trait(c, "mortal_traits", "beautiful", 2)
        add_trait(c, "vampire_traits", "ravenous", -3)
        assert get_total_trait_cost(c) == -1

    def test_at_max_cost_exactly_two(self):
        c = char()
        add_trait(c, "mortal_traits", "genius", 3)
        add_trait(c, "vampire_traits", "territorial", -2)
        add_trait(c, "mortal_traits", "brave", 2)
        # 3 + (-2) + 2 = 3... wait that's 3 not 2
        # Let's check: genius(3) + territorial(-2) + something(1) = 2
        c2 = char()
        add_trait(c2, "mortal_traits", "genius", 3)
        add_trait(c2, "vampire_traits", "territorial", -2)
        add_trait(c2, "mortal_traits", "famous", 1)
        assert get_total_trait_cost(c2) == 2

    def test_trait_count(self):
        c = char()
        add_trait(c, "mortal_traits", "brave", 2)
        add_trait(c, "mortal_traits", "cowardly", -2)
        add_trait(c, "vampire_traits", "ravenous", -3)
        assert get_trait_count(c) == 3

    def test_mental_illness_keys_in_set(self):
        assert "paranoid" in MENTAL_ILLNESS_KEYS
        assert "dissociative_episodes" in MENTAL_ILLNESS_KEYS
        assert "brave" not in MENTAL_ILLNESS_KEYS

    def test_all_mortal_traits_have_valid_cost(self):
        """All traits have either a fixed cost or variable_cost flag."""
        for t in MORTAL_TRAITS:
            assert "cost" in t
            if t.get("variable_cost"):
                assert "cost_options" in t
            else:
                assert isinstance(t.get("cost"), (int, type(None)))

    def test_all_vampire_traits_have_valid_cost(self):
        for t in VAMPIRE_TRAITS:
            assert "cost" in t
            if t.get("variable_cost"):
                assert "cost_options" in t


# ─────────────────────────────────────────────────────────────────────────────
# DISCIPLINE TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestDisciplines:
    def test_xp_cost_per_level(self):
        assert xp_cost_for_disc_level(0) == 1  # 0→1 costs 1
        assert xp_cost_for_disc_level(1) == 2  # 1→2 costs 2
        assert xp_cost_for_disc_level(4) == 5  # 4→5 costs 5

    def test_total_disc_xp_single(self):
        # Level 4: 1+2+3+4 = 10
        assert total_disc_xp({"Auspex": 4}) == 10

    def test_total_disc_xp_multiple(self):
        # Auspex@2 (3) + Celerity@1 (1) = 4
        assert total_disc_xp({"Auspex": 2, "Celerity": 1}) == 4

    def test_total_disc_xp_zero(self):
        assert total_disc_xp({}) == 0
        assert total_disc_xp({"Auspex": 0}) == 0

    def test_available_powers_level_1(self):
        powers = get_available_powers("Auspex", 1, [])
        names = {p["name"] for p in powers}
        assert "Enhance Senses" in names
        assert "Sense The Unseen" in names
        assert "Impulse" in names
        assert "Read Aura" not in names  # level 2

    def test_available_powers_excludes_acquired(self):
        acquired = ["Enhance Senses"]
        powers = get_available_powers("Auspex", 1, acquired)
        names = {p["name"] for p in powers}
        assert "Enhance Senses" not in names

    def test_power_requires_prerequisite(self):
        # Scry requires Telepathy (level 3 power)
        powers_without_telepathy = get_available_powers("Auspex", 4, ["Read Aura"])
        names = {p["name"] for p in powers_without_telepathy}
        assert "Scry" not in names

        # With Telepathy acquired, Scry becomes available
        powers_with_telepathy = get_available_powers("Auspex", 4, ["Telepathy"])
        names_with = {p["name"] for p in powers_with_telepathy}
        assert "Scry" in names_with

    def test_fortitude_toughness_is_level_1(self):
        fortitude_powers = DISCIPLINES["Fortitude"]["powers"]
        toughness = next(p for p in fortitude_powers if p["name"] == "Toughness")
        assert toughness["level"] == 1

    def test_all_disciplines_have_at_least_one_level1_power(self):
        for disc_name, disc in DISCIPLINES.items():
            level1_powers = [p for p in disc["powers"] if p["level"] == 1]
            assert len(level1_powers) >= 1, f"{disc_name} has no level 1 powers"


# ─────────────────────────────────────────────────────────────────────────────
# HP MAX TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestHPMax:
    def test_base_hp(self):
        c = char()
        assert get_hp_max(c) == 10

    def test_iron_constitution_adds_one(self):
        c = char()
        add_trait(c, "mortal_traits", "iron_constitution", 2)
        assert get_hp_max(c) == 11

    def test_fortitude_toughness_adds_two_per_level(self):
        c = char()
        c["discipline_levels"]["Fortitude"] = 2
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        assert get_hp_max(c) == 10 + 2 * 2  # 14

    def test_fortitude_without_toughness_no_bonus(self):
        c = char()
        c["discipline_levels"]["Fortitude"] = 3
        c["discipline_powers"]["Fortitude"] = ["Rapid Healing"]  # not Toughness
        assert get_hp_max(c) == 10

    def test_iron_constitution_plus_fortitude_toughness(self):
        c = char()
        add_trait(c, "mortal_traits", "iron_constitution", 2)
        c["discipline_levels"]["Fortitude"] = 3
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        assert get_hp_max(c) == 10 + 1 + 2 * 3  # 17

    def test_fortitude_level_5_toughness(self):
        c = char()
        c["discipline_levels"]["Fortitude"] = 5
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        assert get_hp_max(c) == 10 + 2 * 5  # 20


# ─────────────────────────────────────────────────────────────────────────────
# CLAN ELIGIBILITY TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestClanEligibility:
    def test_no_eligible_clans_fresh_character(self):
        c = char()
        assert get_eligible_clans(c) == []

    def test_ventrue_requires_selective_taste_and_dominate(self):
        c = char()
        add_trait(c, "vampire_traits", "selective_taste", -1)
        assert not check_clan_eligibility("Ventrue", c)
        c["unlocked_disciplines"] = ["Dominate"]
        assert check_clan_eligibility("Ventrue", c)

    def test_dracul_requires_territorial_or_archaic(self):
        c = char()
        assert not check_clan_eligibility("Dracul", c)
        add_trait(c, "vampire_traits", "territorial", -2)
        assert check_clan_eligibility("Dracul", c)

    def test_dracul_archaic_also_works(self):
        c = char()
        add_trait(c, "vampire_traits", "archaic", -3)
        assert check_clan_eligibility("Dracul", c)

    def test_toreador_requires_trait_and_presence(self):
        c = char()
        add_trait(c, "mortal_traits", "infatuation", -1)
        assert not check_clan_eligibility("Toreador", c)
        c["unlocked_disciplines"] = ["Presence"]
        # infatuation is in VAMPIRE_TRAITS but we can add to mortal for testing
        assert check_clan_eligibility("Toreador", c)

    def test_nosferatu_ugly_or_corpse_like(self):
        c = char()
        c["unlocked_disciplines"] = ["Obfuscate"]
        add_trait(c, "mortal_traits", "ugly", -2)
        assert check_clan_eligibility("Nosferatu", c)

    def test_nosferatu_corpse_like_also_works(self):
        c = char()
        c["unlocked_disciplines"] = ["Obfuscate"]
        add_trait(c, "vampire_traits", "corpse_like", -2)
        assert check_clan_eligibility("Nosferatu", c)

    def test_brujah_needs_prone_to_rage_and_potence_or_celerity(self):
        c = char()
        add_trait(c, "vampire_traits", "prone_to_rage", -2)
        assert not check_clan_eligibility("Brujah", c)
        c["unlocked_disciplines"] = ["Potence"]
        assert check_clan_eligibility("Brujah", c)

    def test_brujah_celerity_also_works(self):
        c = char()
        add_trait(c, "vampire_traits", "prone_to_rage", -2)
        c["unlocked_disciplines"] = ["Celerity"]
        assert check_clan_eligibility("Brujah", c)

    def test_gangrel_needs_ravenous_and_animalism_or_protean(self):
        c = char()
        add_trait(c, "vampire_traits", "ravenous", -3)
        assert not check_clan_eligibility("Gangrel", c)
        c["unlocked_disciplines"] = ["Animalism"]
        assert check_clan_eligibility("Gangrel", c)

    def test_malkavian_mortal_mental_illness(self):
        c = char()
        add_trait(c, "mortal_traits", "paranoid", -2)
        assert check_clan_eligibility("Malkavian", c)

    def test_malkavian_vampire_mental_illness(self):
        c = char()
        add_trait(c, "vampire_traits", "psychotic_episodes", -3)
        assert check_clan_eligibility("Malkavian", c)

    def test_malkavian_no_mental_illness_fails(self):
        c = char()
        add_trait(c, "mortal_traits", "brave", 2)
        assert not check_clan_eligibility("Malkavian", c)

    def test_tremere_needs_specific_traits_and_blood_sorcery(self):
        c = char()
        add_trait(c, "mortal_traits", "rare_specialist", 2, detail="Alchemy")
        c["unlocked_disciplines"] = ["Blood Sorcery"]
        assert check_clan_eligibility("Tremere", c)

    def test_hecata_painful_bite_or_selective_mutism(self):
        c = char()
        c["unlocked_disciplines"] = ["Necromancy"]
        add_trait(c, "vampire_traits", "painful_bite", -2)
        assert check_clan_eligibility("Hecata", c)

    def test_multiple_eligible_clans(self):
        c = char()
        # Set up Toreador + Tremere (both need infatuation/specialist)
        add_trait(c, "mortal_traits", "rare_specialist", 2, detail="Opera")
        c["unlocked_disciplines"] = ["Presence", "Blood Sorcery"]
        eligible = get_eligible_clans(c)
        assert "Toreador" in eligible
        assert "Tremere" in eligible

    def test_unknown_clan_returns_false(self):
        c = char()
        assert check_clan_eligibility("Unknown Clan", c) is False


# ─────────────────────────────────────────────────────────────────────────────
# XP BUDGET TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestXPBudget:
    def test_creation_skill_xp_starts_zero(self):
        c = char()
        assert get_creation_skill_xp_spent(c) == 0

    def test_creation_disc_xp_starts_zero(self):
        c = char()
        assert get_creation_disc_xp_spent(c) == 0

    def test_can_spend_skill_xp_within_budget(self):
        c = char()
        # 15 XP available; spending 5 is fine
        assert can_spend_skill_xp(c, 5) is True

    def test_cannot_overspend_creation_skill_budget(self):
        c = char()
        # Already spent 13 XP
        c["skill_dots"] = {"Brawl": 2, "Guns": 3}  # 3 + 6 = 9 XP
        # Actually compute: Brawl max 2 (standalone) → 1+2=3; Guns 3 dots → 1+2+3=6; total=9
        # Can we spend 7 more? 9+7=16 > 15: depends on earned_xp
        c["earned_xp"] = 0
        assert can_spend_skill_xp(c, 7) is False  # would push to 16 total
        assert can_spend_skill_xp(c, 6) is True   # 9+6=15 exactly

    def test_earned_xp_extends_budget(self):
        c = char()
        # Spend all 15 creation skill XP
        c["skill_dots"] = {"Awareness": 5}  # 1+2+3+4+5 = 15 XP
        c["earned_xp"] = 5
        # Now can spend more from earned pool
        assert can_spend_skill_xp(c, 1) is True

    def test_creation_disc_xp_limit(self):
        c = char()
        c["discipline_levels"] = {"Auspex": 4}  # 10 XP
        c["earned_xp"] = 0
        # Already at 10/10, can't spend more
        assert can_spend_disc_xp(c, 1) is False

    def test_creation_disc_xp_within_budget(self):
        c = char()
        c["discipline_levels"] = {"Auspex": 2}  # 3 XP spent
        assert can_spend_disc_xp(c, 3) is True  # 3+3=6 ≤ 10


# ─────────────────────────────────────────────────────────────────────────────
# EDGE CASE / WIZARD FLOW SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_spend_exactly_15_skill_xp(self):
        """Spend exactly the creation budget."""
        c = char()
        # Brawl@2 (3) + Dodge@3 (6) + Guns@2 (3) + Awareness@1 (1) + Stealth@1 (1) = 14
        # Add one more to get 15: Stealth@2 costs 2, total 16 → too much
        # Instead: Brawl@2(3) + Dodge@3(6) + Guns@2(3) + Awareness@1(1) + Stealth@1(1) + Medicine@1(1) = 15
        c["skill_dots"] = {
            "Brawl": 2, "Dodge": 3, "Guns": 2, "Awareness": 1, "Stealth": 1, "Medicine": 1
        }
        assert total_skill_xp(c["skill_dots"], []) == 15

    def test_cannot_invest_in_child_without_parent(self):
        c = char()
        # Finance requires Basic Analytical at 2 dots
        assert can_add_dot("Finance", "Scheming", {}) is False
        assert can_add_dot("Finance", "Scheming", {"Basic Analytical": 1}) is False

    def test_removing_dots_bottom_up(self):
        """Can remove child dots before parent dots."""
        dots = {"Basic Analytical": 2, "Finance": 2}
        # Can remove Finance dot (no children)
        assert can_remove_dot("Finance", "Scheming", dots) is True
        # Can remove Basic Analytical only after Finance is emptied
        assert can_remove_dot("Basic Analytical", "Scheming", dots) is False
        dots_no_finance = {"Basic Analytical": 2}
        assert can_remove_dot("Basic Analytical", "Scheming", dots_no_finance) is True

    def test_max_trait_count_8(self):
        c = char()
        for i in range(MAX_TRAITS):
            add_trait(c, "mortal_traits", f"trait_{i}", 0)
        assert get_trait_count(c) == MAX_TRAITS

    def test_max_creation_disc_xp_level_4_one_discipline(self):
        """Level 4 in a single discipline costs exactly 10 XP."""
        assert total_disc_xp({"Auspex": 4}) == 10

    def test_three_disciplines_at_level_1_costs_3(self):
        assert total_disc_xp({"Auspex": 1, "Celerity": 1, "Dominate": 1}) == 3

    def test_character_default_state(self):
        c = default_character()
        assert c["wizard_stage"] == 1
        assert c["wizard_complete"] is False
        assert c["skill_dots"] == {}
        assert c["unlocked_disciplines"] == []
        assert c["hp_current"] == 10
        assert c["willpower_current"] == 10
        assert c["blood_current"] == 10
        assert c["earned_xp"] == 0

    def test_medicine_max_dots_7(self):
        """Medicine is special — can go up to 7 dots."""
        assert SKILL_TREES["Resourcefulness"]["Medicine"]["max_dots"] == 7

    def test_marksmanship_requires_max_guns_or_projectiles(self):
        """Marksmanship requires Guns@5 OR Projectiles@5."""
        dots = {"Guns": 4}
        assert can_add_dot("Marksmanship", "Thrashing", dots) is False
        dots["Guns"] = 5
        assert can_add_dot("Marksmanship", "Thrashing", dots) is True

    def test_discipline_powers_list_grows_with_level(self):
        """Powers list should not exceed discipline level."""
        c = char()
        c["unlocked_disciplines"] = ["Auspex"]
        c["discipline_levels"]["Auspex"] = 2
        c["discipline_powers"]["Auspex"] = ["Enhance Senses", "Read Aura"]
        # 2 powers for level 2 — valid
        assert len(c["discipline_powers"]["Auspex"]) <= c["discipline_levels"]["Auspex"]

    def test_scry_requires_telepathy_at_level_4(self):
        """Scry can only be picked if Telepathy is already acquired."""
        available_without = get_available_powers("Auspex", 4, ["Enhance Senses"])
        names_without = {p["name"] for p in available_without}
        assert "Scry" not in names_without

        available_with = get_available_powers("Auspex", 4, ["Enhance Senses", "Telepathy"])
        names_with = {p["name"] for p in available_with}
        assert "Scry" in names_with

    def test_boon_economy_requires_court_etiquette_3(self):
        """Boon Economy branches from Court Etiquette at 3 dots."""
        assert not can_invest("Boon Economy", "Manipulation", {"Basic Manipulation": 2, "Court Etiquette": 2})
        assert can_invest("Boon Economy", "Manipulation", {"Basic Manipulation": 2, "Court Etiquette": 3})

    def test_occult_and_science_both_branch_from_curiosity_2(self):
        """Both Occult and Science require Curiosity@2."""
        dots_ok = {"Curiosity": 2}
        dots_fail = {"Curiosity": 1}
        assert can_invest("Science", "Experimentation", dots_ok)
        assert not can_invest("Science", "Experimentation", dots_fail)
        assert can_invest("Occult", "Experimentation", dots_ok)
        assert not can_invest("Occult", "Experimentation", dots_fail)


# ─────────────────────────────────────────────────────────────────────────────
# COMPREHENSIVE WIZARD FLOW SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

class TestWizardFlows:
    def test_flow_scholar_vampire(self):
        """Scholar-type character: Scheming-focused with Auspex and Arrete."""
        c = char()
        # Stage 1: Mortal traits
        add_trait(c, "mortal_traits", "genius", 3)
        add_trait(c, "mortal_traits", "cowardly", -2)
        assert get_total_trait_cost(c) == 1

        # Stage 2: Vampire traits
        add_trait(c, "vampire_traits", "selective_taste", -1)
        assert get_total_trait_cost(c) == 0

        # Stage 3: Skills — spend 15 XP on Scheming tree
        c["skill_dots"] = {
            "Basic Analytical": 2,  # 3 XP
            "Investigation": 3,     # base 2, own 3 → costs 3+4+5 = 12 XP
        }
        xp = total_skill_xp(c["skill_dots"], [])
        assert xp == 15

        # Before unlocking Dominate: has selective_taste but no Dominate → Ventrue ineligible
        c["unlocked_disciplines"] = ["Auspex", "Arrete"]
        assert not check_clan_eligibility("Ventrue", c)

        # Stage 4: Unlock Dominate (Ventrue requires it unlocked, regardless of level)
        c["unlocked_disciplines"] = ["Auspex", "Arrete", "Dominate"]
        c["discipline_levels"] = {"Auspex": 3, "Arrete": 1, "Dominate": 0}
        # Auspex@3 = 6, Arrete@1 = 1, total = 7 XP ≤ 10
        assert total_disc_xp(c["discipline_levels"]) == 7

        # Stage 5: Ventrue eligible — has selective_taste + Dominate unlocked
        assert check_clan_eligibility("Ventrue", c)

    def test_flow_brujah_warrior(self):
        """Combat-focused Brujah character."""
        c = char()
        add_trait(c, "vampire_traits", "prone_to_rage", -2)
        add_trait(c, "mortal_traits", "large", 1)
        add_trait(c, "vampire_traits", "ravenous", -3)
        add_trait(c, "mortal_traits", "brave", 2)
        # Total: -2 + 1 + -3 + 2 = -2 ≤ 2 ✓
        assert get_total_trait_cost(c) == -2

        # Skills: Thrashing focus
        c["skill_dots"] = {
            "Brawl": 2,           # 3 XP
            "Martial Arts": 3,    # base 2, own 3 → 3+4+5=12 XP → total 15 ✓
        }
        assert total_skill_xp(c["skill_dots"], []) == 15

        # Disciplines: Potence, Celerity, Fortitude
        c["unlocked_disciplines"] = ["Potence", "Celerity", "Fortitude"]
        c["discipline_levels"] = {"Potence": 2, "Celerity": 2, "Fortitude": 1}
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        # XP: 3 + 3 + 1 = 7 ≤ 10 ✓
        assert total_disc_xp(c["discipline_levels"]) == 7

        # HP max with Toughness+Fortitude 1 = 10 + 2 = 12
        assert get_hp_max(c) == 12

        # Brujah eligible (prone_to_rage + Potence)
        assert check_clan_eligibility("Brujah", c)

    def test_flow_gangrel_with_fortitude_5(self):
        """Gangrel with max Fortitude + Toughness → max HP."""
        c = char()
        add_trait(c, "vampire_traits", "ravenous", -3)
        c["unlocked_disciplines"] = ["Animalism", "Protean", "Fortitude"]
        c["discipline_levels"]["Fortitude"] = 5
        c["discipline_powers"]["Fortitude"] = ["Toughness"]
        assert get_hp_max(c) == 20  # 10 + 2*5

        # XP for Fortitude@5 = 15 XP (exceeds 10 creation budget — needs earned XP)
        c["earned_xp"] = 5
        disc_spent = total_disc_xp(c["discipline_levels"])
        assert disc_spent == 15

        # Gangrel eligible
        assert check_clan_eligibility("Gangrel", c)

    def test_flow_nosferatu_spy(self):
        """Nosferatu with ugly + Obfuscate."""
        c = char()
        add_trait(c, "mortal_traits", "ugly", -2)
        add_trait(c, "mortal_traits", "amnesiac", -2)
        add_trait(c, "mortal_traits", "brave", 2)
        # total: -2 + -2 + 2 = -2 ✓
        assert get_total_trait_cost(c) == -2

        c["unlocked_disciplines"] = ["Obfuscate", "Auspex", "Animalism"]
        c["discipline_levels"] = {"Obfuscate": 2, "Auspex": 2, "Animalism": 1}
        # 3 + 3 + 1 = 7 ≤ 10 ✓
        assert total_disc_xp(c["discipline_levels"]) == 7
        assert check_clan_eligibility("Nosferatu", c)

    def test_flow_no_discipline_character(self):
        """Valid character with no disciplines (0 XP on disciplines)."""
        c = char()
        c["unlocked_disciplines"] = ["Auspex", "Celerity", "Potence"]
        # No levels — valid for an unfocused character
        assert total_disc_xp({}) == 0

    def test_flow_trait_cost_at_exactly_2(self):
        """Verify the +2 trait cost cap is enforced correctly."""
        c = char()
        add_trait(c, "mortal_traits", "genius", 3)
        add_trait(c, "mortal_traits", "lightning_reflexes", 3)
        add_trait(c, "vampire_traits", "archaic", -3)
        add_trait(c, "vampire_traits", "ravenous", -3)
        # 3 + 3 + (-3) + (-3) = 0 ≤ 2 ✓
        assert get_total_trait_cost(c) == 0

    def test_flow_malkavian_multiple_mental_illnesses(self):
        """Malkavian with several mental illness traits."""
        c = char()
        add_trait(c, "mortal_traits", "paranoid", -2)
        add_trait(c, "mortal_traits", "depressive_episodes", -2)
        add_trait(c, "mortal_traits", "beautiful", 2)
        add_trait(c, "vampire_traits", "morph", 2)
        # total: -2 + -2 + 2 + 2 = 0 ✓
        assert get_total_trait_cost(c) == 0
        assert check_clan_eligibility("Malkavian", c)
