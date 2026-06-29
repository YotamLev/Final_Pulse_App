"""Skill tree definitions and branching-logic helpers for Final Pulse 2E."""

from __future__ import annotations

# Structure:
#   SKILL_TREES[tree_name][skill_name] = {
#       description: str
#       max_dots: int
#       branches_from: None | (parent, threshold) | [(parent, threshold), ...]
#       branches_or: bool   # True when branches_from is a list (OR condition)
#   }
#
# Skill ordering inside each tree matters for display (parents before children).

SKILL_TREES: dict[str, dict[str, dict]] = {
    "Scheming": {
        "Basic Analytical": {
            "description": "Inferring secrets, planning ambushes, investigating crime scenes.",
            "max_dots": 2,
            "branches_from": None,
        },
        "Finance": {
            "description": "Manage money, embezzle, launder, follow money trails.",
            "max_dots": 5,
            "branches_from": ("Basic Analytical", 2),
        },
        "Logistics": {
            "description": "Supplying, smuggling, organizing.",
            "max_dots": 5,
            "branches_from": ("Basic Analytical", 2),
        },
        "Investigation": {
            "description": "Interrogate, pick up clues, scan vast text sources.",
            "max_dots": 5,
            "branches_from": ("Basic Analytical", 2),
        },
        "Social Academics": {
            "description": "History, Archeology, Sociology, Anthropology, Philosophy, Literature.",
            "max_dots": 5,
            "branches_from": ("Basic Analytical", 2),
        },
        "Mortal Politics": {
            "description": "Organize large institutions, find who holds sway in mortal society, understand mortal laws.",
            "max_dots": 5,
            "branches_from": ("Basic Analytical", 2),
        },
        "Undead Politics": {
            "description": "Find out who holds sway and makes decisions in vampiric society.",
            "max_dots": 2,
            "branches_from": ("Mortal Politics", 3),
        },
    },
    "Manipulation": {
        "Basic Manipulation": {
            "description": "Push people's buttons, convince, convert.",
            "max_dots": 2,
            "branches_from": None,
        },
        "Insight": {
            "description": "See through lies, uncover motives and emotions.",
            "max_dots": 5,
            "branches_from": None,
        },
        "Court Etiquette": {
            "description": "Rules of Vampiric society, traditions, proper forms of address.",
            "max_dots": 5,
            "branches_from": ("Basic Manipulation", 2),
        },
        "Boon Economy": {
            "description": "Understand how Boons and Debts amongst Vampires work and use them to your advantage.",
            "max_dots": 2,
            "branches_from": ("Court Etiquette", 3),
        },
        "Social Chameleon": {
            "description": "Integrate in mortal society and circles, understand and perform mortal culture.",
            "max_dots": 5,
            "branches_from": ("Basic Manipulation", 2),
        },
        "Mortal Society Status": {
            "description": "Learn to rise in Status and recognition, and wield them over mortals.",
            "max_dots": 2,
            "branches_from": ("Social Chameleon", 1),
        },
        "Deception": {
            "description": "Learn to lie and deceive.",
            "max_dots": 5,
            "branches_from": ("Basic Manipulation", 2),
        },
        "Persuasion": {
            "description": "Learn to convince and corrupt.",
            "max_dots": 5,
            "branches_from": ("Basic Manipulation", 2),
        },
        "Intimidation": {
            "description": "Learn to frighten and strong-arm your lessers.",
            "max_dots": 5,
            "branches_from": ("Basic Manipulation", 2),
        },
    },
    "Thrashing": {
        "Brawl": {
            "description": "Up-close and personal fighting. Battle-awareness, willingness to suffer and impose pain.",
            "max_dots": 2,
            "branches_from": None,
        },
        "Martial Arts": {
            "description": "Fighting face-to-face using fists, kicks, chokeholds etc.",
            "max_dots": 5,
            "branches_from": ("Brawl", 2),
        },
        "Swordsmanship": {
            "description": "Fighting using bladed weapons: swords, scimitars, rapiers, katanas.",
            "max_dots": 5,
            "branches_from": ("Brawl", 2),
        },
        "Bludgeoning": {
            "description": "Adept at blunt-force trauma: maces, baseball bats, rocks.",
            "max_dots": 5,
            "branches_from": ("Brawl", 2),
        },
        "Guns": {
            "description": "Can shoot, clean, reload guns. Knows how to handle them.",
            "max_dots": 5,
            "branches_from": None,
        },
        "Projectiles": {
            "description": "Can shoot bows, throw knives, and use other long-range weapons.",
            "max_dots": 5,
            "branches_from": None,
        },
        "Marksmanship": {
            "description": "Can shoot long range, picking up targets as a sniper.",
            "max_dots": 2,
            "branches_from": [("Guns", 5), ("Projectiles", 5)],
            "branches_or": True,
        },
        "Dodge": {
            "description": "Dodge physical attacks. Roll if actively dodging, or take half rounded-down as difficulty to hit you.",
            "max_dots": 5,
            "branches_from": None,
        },
        "Athletics": {
            "description": "Can jump, climb, crawl, and stay upright.",
            "max_dots": 5,
            "branches_from": None,
        },
    },
    "Resourcefulness": {
        "Awareness": {
            "description": "Notice threats, recognize surroundings.",
            "max_dots": 5,
            "branches_from": None,
        },
        "Stealth": {
            "description": "Can hide, sneak, skulk, notice gazes.",
            "max_dots": 5,
            "branches_from": None,
        },
        "Larceny": {
            "description": "Can picklock, pickpocket, carjack, break & enter.",
            "max_dots": 5,
            "branches_from": ("Stealth", 2),
        },
        "Streetwise": {
            "description": "Can get drugs, understand gang territory, notice weird looks, survive in urban areas.",
            "max_dots": 5,
            "branches_from": ("Awareness", 2),
        },
        "Survival": {
            "description": "Understand terrain, navigation, find sanctuary from the sun, survive in non-urban areas.",
            "max_dots": 5,
            "branches_from": ("Awareness", 2),
        },
        "Technology": {
            "description": "Understand common technology as something to use and manipulate.",
            "max_dots": 5,
            "branches_from": None,
        },
        "Hacking": {
            "description": "Understand operating systems, cryptography, and communication well enough to abuse, infiltrate, and distort.",
            "max_dots": 5,
            "branches_from": ("Technology", 2),
        },
        "Medicine": {
            "description": "Understand the mortal body, disease symptoms, treatments. (Mastery level — up to 7 dots)",
            "max_dots": 7,
            "branches_from": None,
        },
        "Medical Forensics": {
            "description": "Understand evidence collection methods, DNA, how to make deaths look natural.",
            "max_dots": 5,
            "branches_from": ("Medicine", 2),
        },
        "Poisons": {
            "description": "Understand dosages, poisons, drug overdoses.",
            "max_dots": 5,
            "branches_from": ("Medicine", 2),
        },
    },
    "Experimentation": {
        "Curiosity": {
            "description": "Morbid interest in pushing the limits of what current society can do and is willing to do.",
            "max_dots": 2,
            "branches_from": None,
        },
        "Science": {
            "description": "Understand the scientific method and current mainstream science.",
            "max_dots": 5,
            "branches_from": ("Curiosity", 2),
        },
        "Biology": {
            "description": "Understand biological processes in mortals, animals, bacteria, viruses.",
            "max_dots": 5,
            "branches_from": ("Science", 2),
        },
        "Chemistry": {
            "description": "Understand compounds, can create chemical reactions, acids, explosives.",
            "max_dots": 5,
            "branches_from": ("Science", 2),
        },
        "Weird Science": {
            "description": "Willing to experiment on unwilling mortals; can create mutants, targeted viruses. Uses are specific, unstable, and often unreproducible.",
            "max_dots": 5,
            "branches_from": ("Biology", 2),
        },
        "Alchemy": {
            "description": "Can create new materials, potions and elixirs with limited-time effects. Uses are specific, unstable, and require exotic ingredients.",
            "max_dots": 5,
            "branches_from": ("Chemistry", 2),
        },
        "Occult": {
            "description": "Research forbidden lore, secret weaknesses, and rituals.",
            "max_dots": 5,
            "branches_from": ("Curiosity", 2),
        },
        "Demonology": {
            "description": "Research demons and means of summoning them.",
            "max_dots": 5,
            "branches_from": ("Occult", 3),
        },
    },
}

ALL_TREE_NAMES: list[str] = list(SKILL_TREES.keys())


# ── Branch logic helpers ──────────────────────────────────────────────────────

def get_static_base(skill_name: str, tree_name: str) -> int:
    """
    Static contribution from parent skills at their branch threshold.
    This depends only on tree structure, not on current dot investments.
    Equal to: parent_static_base + branch_threshold (recursively).
    """
    skill = SKILL_TREES.get(tree_name, {}).get(skill_name)
    if skill is None:
        return 0
    branch = skill.get("branches_from")
    if branch is None:
        return 0

    if skill.get("branches_or", False):
        # OR condition: all options have the same threshold in current data;
        # take the first for the static computation.
        parent_name, threshold = branch[0]
    else:
        parent_name, threshold = branch

    return get_static_base(parent_name, tree_name) + threshold


def get_effective_level(skill_name: str, tree_name: str, own_dots: dict[str, int]) -> int:
    """Effective (practical) level = static_base + own_dots invested."""
    return get_static_base(skill_name, tree_name) + own_dots.get(skill_name, 0)


def can_invest(skill_name: str, tree_name: str, own_dots: dict[str, int]) -> bool:
    """Return True if prerequisites are satisfied to invest any dot in this skill."""
    skill = SKILL_TREES.get(tree_name, {}).get(skill_name)
    if skill is None:
        return False
    branch = skill.get("branches_from")
    if branch is None:
        return True

    if skill.get("branches_or", False):
        return any(own_dots.get(p, 0) >= t for p, t in branch)
    else:
        parent, threshold = branch
        return own_dots.get(parent, 0) >= threshold


def can_add_dot(skill_name: str, tree_name: str, own_dots: dict[str, int]) -> bool:
    """Return True if a dot can be added (prerequisites met and below max)."""
    skill = SKILL_TREES.get(tree_name, {}).get(skill_name)
    if skill is None:
        return False
    if own_dots.get(skill_name, 0) >= skill["max_dots"]:
        return False
    return can_invest(skill_name, tree_name, own_dots)


def can_remove_dot(skill_name: str, tree_name: str, own_dots: dict[str, int]) -> bool:
    """Return True if a dot can be removed (has dots and no child skill depends on this level)."""
    current = own_dots.get(skill_name, 0)
    if current <= 0:
        return False

    new_own = current - 1

    for child_name, child_skill in SKILL_TREES.get(tree_name, {}).items():
        branch = child_skill.get("branches_from")
        if branch is None:
            continue
        if own_dots.get(child_name, 0) == 0:
            continue  # child not invested

        if child_skill.get("branches_or", False):
            for parent_name, threshold in branch:
                if parent_name == skill_name and new_own < threshold:
                    # Would lose this qualifying parent; check other parents
                    other_qualifies = any(
                        own_dots.get(p, 0) >= t
                        for p, t in branch
                        if p != skill_name
                    )
                    if not other_qualifies:
                        return False
        else:
            parent_name, threshold = branch
            if parent_name == skill_name and new_own < threshold:
                return False

    return True


def xp_cost_for_next_dot(skill_name: str, tree_name: str, own_dots: dict[str, int]) -> int:
    """XP cost to add the next dot = the effective level after adding it."""
    base = get_static_base(skill_name, tree_name)
    return base + own_dots.get(skill_name, 0) + 1


def xp_cost_for_n_own_dots(skill_name: str, tree_name: str, n: int) -> int:
    """Total XP cost to reach n own dots from 0 (not counting prerequisites)."""
    base = get_static_base(skill_name, tree_name)
    # XP = sum_{i=1}^{n} (base + i) = n*base + n*(n+1)/2
    return n * base + n * (n + 1) // 2


def total_skill_xp(own_dots: dict[str, int], custom_skills: list[dict]) -> int:
    """Total XP spent across all skill trees (standard + custom)."""
    total = 0
    for tree_name, skills in SKILL_TREES.items():
        for skill_name in skills:
            n = own_dots.get(skill_name, 0)
            if n > 0:
                total += xp_cost_for_n_own_dots(skill_name, tree_name, n)
    # Custom skills are standalone (base = 0)
    for cs in custom_skills:
        n = own_dots.get(cs["name"], 0)
        if n > 0:
            total += n * (n + 1) // 2
    return total


def get_tree_for_skill(skill_name: str) -> str | None:
    """Return the tree name that contains this skill, or None."""
    for tree_name, skills in SKILL_TREES.items():
        if skill_name in skills:
            return tree_name
    return None


def invested_skills(own_dots: dict[str, int]) -> list[tuple[str, str, int]]:
    """Return [(tree_name, skill_name, dots), ...] for all skills with dots > 0."""
    result = []
    for tree_name, skills in SKILL_TREES.items():
        for skill_name in skills:
            d = own_dots.get(skill_name, 0)
            if d > 0:
                result.append((tree_name, skill_name, d))
    return result
