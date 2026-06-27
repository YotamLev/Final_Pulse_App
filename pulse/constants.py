from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

SCHEMA_VERSION = 3
APP_VERSION = "0.1.0"

ATTRIBUTES = [
    "Strength",
    "Dexterity",
    "Stamina",
    "Charisma",
    "Manipulation",
    "Composure",
    "Intelligence",
    "Wits",
    "Resolve",
]

ATTRIBUTE_GROUPS = {
    "Physical": ["Strength", "Dexterity", "Stamina"],
    "Social": ["Charisma", "Manipulation", "Composure"],
    "Mental": ["Intelligence", "Wits", "Resolve"],
}

ATTRIBUTE_DESCRIPTIONS = {
    "Strength": "Muscles, stability in movement",
    "Dexterity": "Finesse, grace in movement",
    "Stamina": "Constitution, endurance",
    "Charisma": "Likability, ability to convince, initial perceived trustworthiness",
    "Manipulation": "Ability to see through others, push buttons",
    "Composure": "Poker face, withstanding adverse social situations",
    "Intelligence": "Memory, pattern recognition, problem-solving",
    "Wits": "Snap judgment, situational awareness",
    "Resolve": "Grit, ability to perform lengthy boring tasks",
}

BASE_ATTRIBUTE_VALUE = 2
TARGET_DISTRIBUTION = {3: 3, 2: 3, 1: 3}

SKILL_MAX_DEFAULT = 5
BASE_SKILL_MAX = 2
ATTRIBUTE_MAX_DEFAULT = 5

TOTAL_SKILL_DOTS = 18

# Legacy pool fields kept for old JSON compatibility only.
SKILL_POOLS = ("professional", "life_event", "leisure", "natural")
POOL_BUDGETS = {
    "professional": 10,
    "life_event": 5,
    "leisure": 3,
    "natural": 4,
}

POOL_LABELS = {
    "professional": "Professional Skills",
    "life_event": "Life Event Skills",
    "leisure": "Leisure Skills",
    "natural": "Natural Skills",
}

POOL_PROMPTS = {
    "professional": "What do you spend most of your waking hours doing? Add 10 dots to relevant skills.",
    "life_event": "What major life events shaped you? Add 5 dots to relevant skills.",
    "leisure": "What do you do for kicks? Add 3 dots to relevant skills.",
    "natural": "Some people are born better than others. Add 4 dots to skills.",
}

MORTAL_STEPS = {
    1: "Chronicle & Concept",
    2: "Traits",
    3: "Attributes",
    4: "Skills",
    5: "Languages",
    6: "Specialties",
    7: "Beliefs & Relations",
    8: "Mortal Complete",
}

MORTAL_STEP_COUNT = len(MORTAL_STEPS)

VAMPIRE_STEPS = {
    9: "Embrace — Clan & Bane",
    10: "Level 0 — First Discipline",
    11: "Level 1 — Attributes (+2)",
    12: "Level 1 — Second Discipline & Power",
    13: "Level 1 — Predator Type",
    14: "Level 2 — Attributes (+2)",
    15: "Level 2 — Third Discipline & Power",
    16: "Character Complete",
}

PREDATOR_SKILL_DOTS = 2

WIZARD_STEPS = {**MORTAL_STEPS, **VAMPIRE_STEPS}
WIZARD_STEP_COUNT = len(WIZARD_STEPS)
CREATION_STEP_COUNT = WIZARD_STEP_COUNT

INNATE_VAMPIRE_ABILITIES = [
    "Blush of Life — appear human for a scene (1 Liter)",
    "Blood Surge — add red dice to rolls (1 Liter per die, up to 5)",
    "Vampiric Healing — heal 1 HP per Liter",
]
