from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pulse.constants import DATA_DIR, PREDATOR_SKILL_DOTS

CAP_PATH = DATA_DIR / "cap_extensions.json"
POWERS_PATH = DATA_DIR / "powers.json"


@lru_cache
def _cap_data() -> dict:
    return json.loads(CAP_PATH.read_text(encoding="utf-8"))


def known_power_names(character: dict[str, Any]) -> set[str]:
    vampire = character.get("vampire") or {}
    names: set[str] = set()
    for p in vampire.get("powers", []):
        if p.get("name"):
            names.add(p["name"])
        if p.get("id"):
            names.add(p["id"])
    return names


def known_power_ids(character: dict[str, Any]) -> set[str]:
    vampire = character.get("vampire") or {}
    return {p["id"] for p in vampire.get("powers", []) if p.get("id")}


def known_disciplines(character: dict[str, Any]) -> list[str]:
    vampire = character.get("vampire") or {}
    return [d["name"] for d in vampire.get("disciplines", [])]


def effective_attribute_max(character: dict[str, Any], attribute: str) -> int:
    data = _cap_data()
    maximum = data["defaults"]["attribute_max"]
    for entry in data["permanent_extensions"]["attribute_max_plus_one"]:
        if entry["attribute"] == attribute and entry["power"] in known_power_names(character):
            maximum += 1
    return maximum


def effective_skill_max(character: dict[str, Any], skill: str) -> int:
    data = _cap_data()
    maximum = data["defaults"]["skill_max"]
    vampire = character.get("vampire") or {}
    masterwork = vampire.get("cap_choices", {}).get("masterwork")
    if masterwork and entry_has_masterwork_boost(masterwork, skill):
        if masterwork.get("mode") == "one_skill_plus_two" and skill in masterwork.get("skills", []):
            maximum += 2
        elif masterwork.get("mode") == "two_skills_plus_one" and skill in masterwork.get("skills", []):
            maximum += 1
    if "Masterwork" in known_power_names(character) and not masterwork:
        pass
    return maximum


def entry_has_masterwork_boost(masterwork: dict, skill: str) -> bool:
    return skill in masterwork.get("skills", [])


def get_attribute_values(character: dict[str, Any]) -> dict[str, int]:
    attrs = dict(character.get("mortal", {}).get("attributes", {}))
    vampire = character.get("vampire") or {}
    for block in vampire.get("attribute_adjustments", []):
        for name, delta in block.get("changes", {}).items():
            attrs[name] = attrs.get(name, 0) + int(delta)
    for level_up in vampire.get("level_ups", []):
        if level_up.get("choice") == "attr":
            details = level_up.get("details", {})
            name = details.get("attribute")
            if name:
                attrs[name] = attrs.get(name, 0) + int(details.get("dots", 1))
    return attrs


def attribute_adjustment_bounds(
    character: dict[str, Any],
    attribute: str,
    *,
    level_changes: dict[str, int],
    budget: int = 2,
) -> tuple[int, int, int]:
    """Return (base_before_level, max_assignable, assigned) for one attribute step."""
    attrs = get_attribute_values(character)
    assigned = int(level_changes.get(attribute, 0))
    base = int(attrs.get(attribute, 2)) - assigned
    cap = effective_attribute_max(character, attribute)
    room_to_cap = max(0, cap - base)
    other_total = sum(int(v) for v in level_changes.values()) - assigned
    room_in_budget = max(0, budget - other_total)
    max_assignable = min(room_to_cap, room_in_budget)
    return base, max_assignable, min(assigned, max_assignable)


def mortal_skill_dots(character: dict[str, Any], skill: str) -> int:
    entry = character.get("mortal", {}).get("skills", {}).get(skill, {})
    return int(entry.get("dots", 0))


def skills_with_predator_room(
    character: dict[str, Any],
    candidates: list[str] | None = None,
    *,
    grant: int = PREDATOR_SKILL_DOTS,
) -> list[str]:
    from pulse.data_loader import skill_category_map

    names = candidates if candidates is not None else sorted(skill_category_map().keys())
    return [
        skill
        for skill in names
        if mortal_skill_dots(character, skill) + grant <= effective_skill_max(character, skill)
    ]


def _mortal_skill_dots_map(character: dict[str, Any]) -> dict[str, int]:
    skills: dict[str, int] = {}
    for name, entry in character.get("mortal", {}).get("skills", {}).items():
        skills[name] = int(entry.get("dots", 0))
    return skills


def _apply_predator_skill_bonus(character: dict[str, Any], skills: dict[str, int]) -> None:
    vampire = character.get("vampire") or {}
    predator = vampire.get("predator") or {}
    if predator.get("skill_choice"):
        sk = predator["skill_choice"].get("skill")
        dots = int(predator["skill_choice"].get("dots", 0))
        if sk:
            cap = effective_skill_max(character, sk)
            skills[sk] = min(cap, skills.get(sk, 0) + dots)


def _apply_skill_adjustments(
    skills: dict[str, int],
    vampire: dict[str, Any],
    *,
    skip_removed_at_level: int | None = None,
) -> None:
    for block in vampire.get("skill_adjustments", []):
        level = block.get("level")
        if skip_removed_at_level is None or level != skip_removed_at_level:
            for name, delta in block.get("removed", {}).items():
                skills[name] = max(0, skills.get(name, 0) - int(delta))
        for name, delta in block.get("added", {}).items():
            skills[name] = skills.get(name, 0) + int(delta)


def _apply_skill_level_ups(skills: dict[str, int], vampire: dict[str, Any]) -> None:
    for level_up in vampire.get("level_ups", []):
        if level_up.get("choice") == "skills":
            for name, delta in level_up.get("details", {}).items():
                skills[name] = skills.get(name, 0) + int(delta)


SKILL_REMOVAL_BUDGET = 2
SKILL_LEVEL_UP_BUDGET = 2


def skill_dots_before_removal(character: dict[str, Any], level: int = 2) -> dict[str, int]:
    """Skill totals before forget-step removals at level are applied."""
    skills = _mortal_skill_dots_map(character)
    _apply_predator_skill_bonus(character, skills)
    vampire = character.get("vampire") or {}
    _apply_skill_adjustments(skills, vampire, skip_removed_at_level=level)
    _apply_skill_level_ups(skills, vampire)
    return skills


def skill_removal_bounds(
    character: dict[str, Any],
    skill: str,
    *,
    removed: dict[str, int],
    level: int = 2,
    budget: int = SKILL_REMOVAL_BUDGET,
) -> tuple[int, int, int]:
    """Return (dots_before_removal, max_removable, clamped_removal)."""
    available = int(skill_dots_before_removal(character, level).get(skill, 0))
    assigned = int(removed.get(skill, 0))
    other_total = sum(int(v) for v in removed.values()) - assigned
    room_in_budget = max(0, budget - other_total)
    max_removable = min(available, room_in_budget)
    return available, max_removable, min(assigned, max_removable)


def skill_addition_bounds(
    character: dict[str, Any],
    skill: str,
    additions: dict[str, int],
    *,
    budget: int = SKILL_LEVEL_UP_BUDGET,
) -> tuple[int, int, int, int]:
    """Return (current_dots, cap, max_addable, clamped_assigned) for level-up skill dots."""
    current = int(get_skill_dots(character).get(skill, 0))
    cap = effective_skill_max(character, skill)
    assigned = int(additions.get(skill, 0))
    other_total = sum(int(v) for v in additions.values()) - assigned
    room_to_cap = max(0, cap - current)
    room_in_budget = max(0, budget - other_total)
    max_addable = min(room_to_cap, room_in_budget)
    return current, cap, max_addable, min(assigned, max_addable)


def get_skill_dots(character: dict[str, Any]) -> dict[str, int]:
    skills = _mortal_skill_dots_map(character)
    _apply_predator_skill_bonus(character, skills)
    vampire = character.get("vampire") or {}
    _apply_skill_adjustments(skills, vampire)
    _apply_skill_level_ups(skills, vampire)
    return skills
