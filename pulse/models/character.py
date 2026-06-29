"""Character state management for Final Pulse 2E."""

from __future__ import annotations

import copy

from pulse.data.skill_trees import total_skill_xp
from pulse.data.disciplines import total_disc_xp

CREATION_SKILL_XP = 15
CREATION_DISC_XP = 10
MAX_TRAITS = 8
MAX_TRAIT_COST = 2
BASE_HP = 10
BASE_WILLPOWER = 10
BASE_BLOOD = 10


def default_character() -> dict:
    return {
        # ── Wizard progress ──────────────────────────────────────────────────
        "wizard_stage": 1,
        "wizard_complete": False,

        # ── Stage 1: Mortal ──────────────────────────────────────────────────
        "name": "",
        "birthplace": "",
        "birthtime": "",
        "mortal_history": "",   # who you were, childhood, job, hobbies, events
        "beliefs": "",
        "connections": "",      # important characters and connections
        "mortal_traits": [],    # list of trait dicts (see traits.py)

        # ── Stage 2: Vampire ─────────────────────────────────────────────────
        "sire": "",
        "embrace_time": "",
        "embrace_backstory": "",
        "vampire_traits": [],

        # ── Stage 3: Skills ──────────────────────────────────────────────────
        "skill_dots": {},        # {skill_name: own_dots}
        "custom_skills": [],     # [{name, max_dots}]

        # ── Stage 4: Disciplines ─────────────────────────────────────────────
        "unlocked_disciplines": [],    # up to 3 discipline names
        "discipline_levels": {},       # {disc_name: level (0-5)}
        "discipline_powers": {},       # {disc_name: [power_name, ...]}

        # ── Stage 5: Clan ────────────────────────────────────────────────────
        "clan": None,

        # ── Character sheet trackers ─────────────────────────────────────────
        "hp_current": BASE_HP,
        "willpower_current": BASE_WILLPOWER,
        "blood_current": BASE_BLOOD,

        # ── Post-creation XP ─────────────────────────────────────────────────
        "earned_xp": 0,          # total XP awarded by Storyteller

        # ── XP log ───────────────────────────────────────────────────────────
        "xp_log": [],            # list of log-entry dicts

        # ── Notes ─────────────────────────────────────────────────────────────
        "notes": "",

        # ── Struggle ──────────────────────────────────────────────────────────
        "struggle_schemes": [],
        "struggle_assets": [],
    }


# ── Computed properties ────────────────────────────────────────────────────────

def get_hp_max(char: dict) -> int:
    """Max HP = 10 + 1 (Iron Constitution) + 2 × Fortitude level (if Toughness acquired)."""
    hp = BASE_HP
    # Iron Constitution mortal trait
    if any(t["key"] == "iron_constitution" for t in char.get("mortal_traits", [])):
        hp += 1
    # Fortitude Toughness power
    fort_level = char.get("discipline_levels", {}).get("Fortitude", 0)
    if fort_level > 0 and "Toughness" in char.get("discipline_powers", {}).get("Fortitude", []):
        hp += 2 * fort_level
    return hp


def get_total_trait_cost(char: dict) -> int:
    """Sum of all mortal + vampire trait costs."""
    total = 0
    for t in char.get("mortal_traits", []):
        total += t.get("cost", 0) or 0
    for t in char.get("vampire_traits", []):
        total += t.get("cost", 0) or 0
    return total


def get_trait_count(char: dict) -> int:
    return len(char.get("mortal_traits", [])) + len(char.get("vampire_traits", []))


def get_creation_skill_xp_spent(char: dict) -> int:
    return total_skill_xp(char.get("skill_dots", {}), char.get("custom_skills", []))


def get_creation_disc_xp_spent(char: dict) -> int:
    return total_disc_xp(char.get("discipline_levels", {}))


def get_earned_xp_available(char: dict) -> int:
    """Earned XP not yet spoken for by post-creation spending."""
    skill_spent = get_creation_skill_xp_spent(char)
    disc_spent = get_creation_disc_xp_spent(char)
    creation_spent = min(skill_spent, CREATION_SKILL_XP) + min(disc_spent, CREATION_DISC_XP)
    overflow = max(0, skill_spent - CREATION_SKILL_XP) + max(0, disc_spent - CREATION_DISC_XP)
    return char.get("earned_xp", 0) - overflow


def can_spend_skill_xp(char: dict, cost: int) -> bool:
    """True if there is enough XP (creation + earned) to spend on a skill dot."""
    skill_spent = get_creation_skill_xp_spent(char)
    if skill_spent < CREATION_SKILL_XP:
        return cost <= (CREATION_SKILL_XP - skill_spent)
    return cost <= get_earned_xp_available(char)


def can_spend_disc_xp(char: dict, cost: int) -> bool:
    """True if there is enough XP (creation + earned) to spend on a disc level."""
    disc_spent = get_creation_disc_xp_spent(char)
    if disc_spent < CREATION_DISC_XP:
        return cost <= (CREATION_DISC_XP - disc_spent)
    return cost <= get_earned_xp_available(char)


# ── Log helpers ───────────────────────────────────────────────────────────────

def log_xp_spend(char: dict, description: str, cost: int) -> None:
    char.setdefault("xp_log", []).append({"description": description, "cost": cost})


def log_xp_refund(char: dict, description: str, refund: int) -> None:
    char.setdefault("xp_log", []).append({"description": f"[Refund] {description}", "cost": -refund})


# ── Serialisation helpers ─────────────────────────────────────────────────────

def char_to_dict(char: dict) -> dict:
    return copy.deepcopy(char)


def char_from_dict(data: dict) -> dict:
    base = default_character()
    base.update(data)
    return base
