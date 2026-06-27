from __future__ import annotations

from typing import Any

from pulse.caps import effective_attribute_max, effective_skill_max, get_attribute_values, get_skill_dots, mortal_skill_dots
from pulse.constants import PREDATOR_SKILL_DOTS
from pulse.data_loader import load_predator_types
from pulse.powers import power_by_id, prerequisites_met
from pulse.constants import MORTAL_STEP_COUNT
from pulse.validation import validate_step as validate_mortal_step
from pulse.vampire import clan_by_id, get_clan_disciplines


def validate_wizard_step(character: dict[str, Any], step: int) -> list[str]:
    if step <= MORTAL_STEP_COUNT:
        return validate_mortal_step(character, step)
    validators = {
        9: _validate_embrace,
        10: _validate_level_0,
        11: _validate_l1_attributes,
        12: _validate_l1_discipline_power,
        13: _validate_predator,
        14: _validate_l2_skill_removal,
        15: _validate_l2_attributes,
        16: _validate_l2_discipline_power,
        17: _validate_complete,
    }
    fn = validators.get(step)
    if fn:
        return fn(character)
    return []


def _vampire(character: dict) -> dict:
    return character.get("vampire") or {}


def _attr_adjustment_total(character: dict, level: int) -> int:
    for block in _vampire(character).get("attribute_adjustments", []):
        if block.get("level") == level:
            return sum(int(v) for v in block.get("changes", {}).values())
    return 0


def _validate_embrace(character: dict) -> list[str]:
    errors = list(validate_mortal_step(character, MORTAL_STEP_COUNT))
    v = _vampire(character)
    if not v.get("clan"):
        errors.append("Choose a clan.")
        return errors
    clan = clan_by_id(v["clan"])
    if not clan:
        errors.append("Invalid clan.")
        return errors
    v.setdefault("bane", {})["summary"] = clan["bane"]["summary"]
    fields = v["bane"].setdefault("fields", {})
    for field in clan["bane"].get("fields", []):
        fid = field["id"]
        if not str(fields.get(fid, "")).strip():
            errors.append(f"Complete bane field: {field['label']}.")
    return errors


def _validate_level_0(character: dict) -> list[str]:
    errors = _validate_embrace(character)
    v = _vampire(character)
    discs = v.get("disciplines", [])
    powers = v.get("powers", [])
    if len(discs) < 1:
        errors.append("Choose your first Discipline.")
    if len(powers) < 1:
        errors.append("Choose your first Discipline power.")
    return errors


def _validate_l1_attributes(character: dict) -> list[str]:
    errors = _validate_level_0(character)
    total = _attr_adjustment_total(character, 1)
    if total != 2:
        errors.append(f"Assign exactly 2 attribute dots for Level 1 ({total}/2).")
    attrs = get_attribute_values(character)
    for name, value in attrs.items():
        if value > effective_attribute_max(character, name):
            errors.append(f"{name} exceeds maximum ({value} > {effective_attribute_max(character, name)}).")
    return errors


def _validate_l1_discipline_power(character: dict) -> list[str]:
    errors = _validate_l1_attributes(character)
    v = _vampire(character)
    clan_discs = get_clan_disciplines(character)
    known = [d["name"] for d in v.get("disciplines", [])]
    if len(known) < 2:
        errors.append("Choose a second clan Discipline.")
    elif known[0] == known[1]:
        errors.append("Second Discipline must differ from the first.")
    elif len(known) >= 2 and known[1] not in clan_discs:
        errors.append("Second Discipline must be from your clan list.")
    non_predator = [p for p in v.get("powers", []) if not p.get("is_predator_power")]
    if len(non_predator) < 2:
        errors.append("Choose your second Discipline power.")
    return errors


def _validate_predator(character: dict) -> list[str]:
    errors = _validate_l1_discipline_power(character)
    v = _vampire(character)
    predator = v.get("predator")
    if not predator or not predator.get("type"):
        errors.append("Choose a predator type.")
        return errors
    if predator.get("source") == "custom":
        if not predator.get("custom_name", "").strip():
            errors.append("Name your custom predator type.")
        if not predator.get("skill_choice", {}).get("skill"):
            errors.append("Assign predator skill dots.")
        if int(predator.get("skill_choice", {}).get("dots", 0)) != 2:
            errors.append("Predator type grants exactly 2 skill dots.")
        if not predator.get("specialty", {}).get("text"):
            errors.append("Add a predator specialty.")
    else:
        sc = predator.get("skill_choice", {})
        if int(sc.get("dots", 0)) != 2:
            errors.append("Assign exactly 2 predator skill dots.")
        if not sc.get("skill"):
            errors.append("Choose a skill for predator dots.")
        if not predator.get("specialty", {}).get("text"):
            errors.append("Add a predator specialty.")
    predator_powers = [p for p in v.get("powers", []) if p.get("is_predator_power")]
    ptype = predator.get("type")
    pdef = next((p for p in load_predator_types() if p["id"] == ptype), None)
    needed = 2 if pdef and (pdef.get("special_rules") or {}).get("predator_power_count") == 2 else 1
    if len(predator_powers) < needed:
        errors.append(f"Choose {needed} predator power(s).")
    rules = (pdef.get("special_rules") if pdef else None) or {}
    if rules.get("same_discipline") and len(predator_powers) >= 2:
        sources = {p.get("source") for p in predator_powers}
        if len(sources) > 1:
            errors.append("Leech predator powers must be from the same Discipline.")
    sc = predator.get("skill_choice") or {}
    skill = sc.get("skill")
    if skill:
        total = mortal_skill_dots(character, skill) + int(sc.get("dots", 0))
        cap = effective_skill_max(character, skill)
        if total > cap:
            errors.append(
                f"{skill} exceeds maximum ({total} > {cap}). "
                f"Choose a skill with room for +{PREDATOR_SKILL_DOTS} dots."
            )
    return errors


def _validate_l2_skill_removal(character: dict) -> list[str]:
    errors = _validate_predator(character)
    removed = 0
    for block in _vampire(character).get("skill_adjustments", []):
        if block.get("level") == 2:
            removed += sum(int(v) for v in block.get("removed", {}).values())
    if removed != 2:
        errors.append(f"Remove exactly 2 skill dots ({removed}/2).")
    return errors


def _validate_l2_attributes(character: dict) -> list[str]:
    errors = _validate_l2_skill_removal(character)
    total = _attr_adjustment_total(character, 2)
    if total != 2:
        errors.append(f"Assign exactly 2 attribute dots for Level 2 ({total}/2).")
    attrs = get_attribute_values(character)
    for name, value in attrs.items():
        if value > effective_attribute_max(character, name):
            errors.append(f"{name} exceeds maximum ({value} > {effective_attribute_max(character, name)}).")
    return errors


def _validate_l2_discipline_power(character: dict) -> list[str]:
    errors = _validate_l2_attributes(character)
    v = _vampire(character)
    if len(v.get("disciplines", [])) < 3:
        errors.append("Choose a third Discipline.")
    if len(v.get("powers", [])) < 4:
        errors.append("Choose your fourth Discipline power.")
    return errors


def _validate_complete(character: dict) -> list[str]:
    return _validate_l2_discipline_power(character)


def validate_level_up(character: dict, choice: str, details: dict) -> list[str]:
    errors: list[str] = []
    v = _vampire(character)
    if v.get("level", 0) < 2:
        errors.append("Complete character creation before leveling up.")
    if choice == "attr":
        attr = details.get("attribute")
        if not attr:
            errors.append("Choose an attribute.")
        else:
            current = get_attribute_values(character).get(attr, 0)
            if current + 1 > effective_attribute_max(character, attr):
                errors.append(f"{attr} is at its maximum.")
    elif choice == "power":
        pid = details.get("id")
        if not pid:
            errors.append("Choose a power.")
        else:
            power = power_by_id(pid)
            if power and not prerequisites_met(power, character):
                errors.append("Prerequisites not met for that power.")
    elif choice == "skills":
        if sum(int(v) for v in details.values()) != 2:
            errors.append("Assign exactly 2 skill dots.")
        for skill, dots in details.items():
            current = get_skill_dots(character).get(skill, 0)
            cap = effective_skill_max(character, skill)
            total = int(current) + int(dots)
            if total > cap:
                errors.append(f"{skill} would exceed maximum ({total} > {cap}).")
    elif choice == "specialties":
        specs = details.get("specialties", [])
        if len(specs) != 3:
            errors.append("Add exactly 3 specialties.")
        for spec in specs:
            if not spec.get("skill") or not spec.get("text"):
                errors.append("Complete all specialty fields.")
    else:
        errors.append("Choose a level-up option.")
    return errors
