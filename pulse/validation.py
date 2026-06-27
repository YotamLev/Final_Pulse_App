from __future__ import annotations

from typing import Any

from pulse.attributes import compute_attributes, distribution_valid
from pulse.constants import MORTAL_STEP_COUNT, TOTAL_SKILL_DOTS
from pulse.skills import (
    effective_specialty_rating,
    total_assigned_skill_dots,
    validate_skill_allocation,
)


def validate_step(character: dict[str, Any], step: int) -> list[str]:
    validators = {
        1: _validate_chronicle,
        2: _validate_traits,
        3: _validate_attributes,
        4: _validate_skills,
        5: _validate_languages,
        6: _validate_specialties,
        7: _validate_beliefs,
        8: _validate_mortal_complete,
    }
    if step < 1 or step > MORTAL_STEP_COUNT:
        return []
    return validators[step](character)


def _validate_chronicle(character: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not character.get("chronicle", {}).get("time_and_place", "").strip():
        errors.append("Time & place is required.")
    return errors


def _validate_traits(character: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    traits = character.get("mortal", {}).get("traits", [])
    if len(traits) != 3:
        errors.append("Assign exactly 3 traits.")
        return errors

    used_attrs: set[str] = set()
    for index, trait in enumerate(traits, start=1):
        name = trait.get("name", "").strip()
        plus = trait.get("plus", "")
        minus = trait.get("minus", "")
        if not name or not plus or not minus:
            errors.append(f"Trait {index}: complete name, +1, and −1.")
        if plus == minus:
            errors.append(f"Trait {index}: +1 and −1 cannot be the same attribute.")
        for attr in (plus, minus):
            if attr in used_attrs:
                errors.append(f"Each attribute can only appear in one trait ({attr} is repeated).")
            used_attrs.add(attr)

    attrs = compute_attributes(traits)
    if not distribution_valid(attrs):
        errors.append("Attributes must end as 3 at 3, 3 at 2, and 3 at 1.")
    return errors


def _validate_attributes(character: dict[str, Any]) -> list[str]:
    return _validate_traits(character)


def total_skill_dots(character: dict[str, Any]) -> int:
    return total_assigned_skill_dots(character)


def _validate_skills(character: dict[str, Any]) -> list[str]:
    return validate_skill_allocation(character)


def _validate_languages(character: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    intelligence = int(character.get("mortal", {}).get("attributes", {}).get("Intelligence", 2))
    languages = character.get("mortal", {}).get("languages", [])
    if len(languages) != intelligence:
        errors.append(f"Choose {intelligence} language(s) (one per Intelligence dot).")
    for index, language in enumerate(languages, start=1):
        if not str(language).strip():
            errors.append(f"Language {index} must be named.")
    errors.extend(_validate_skills(character))
    return errors


def _validate_specialties(character: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    specialties = character.get("mortal", {}).get("specialties", [])
    if len(specialties) != 2:
        errors.append("Add exactly 2 specialties.")
        return errors

    chosen_skills: list[str] = []
    for index, spec in enumerate(specialties, start=1):
        skill = spec.get("skill", "").strip()
        text = spec.get("text", "").strip()
        if not skill or not text:
            errors.append(f"Specialty {index}: choose a skill and describe the specialty.")
        if skill in chosen_skills:
            errors.append("Specialties must be on two different skills.")
        chosen_skills.append(skill)
        if skill and effective_specialty_rating(character, skill) < 1:
            errors.append(f"Specialty {index}: {skill} needs at least 1 effective dot.")

    errors.extend(_validate_languages(character))
    return errors


def _validate_beliefs(character: dict[str, Any]) -> list[str]:
    return _validate_specialties(character)


def _validate_mortal_complete(character: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for step in range(1, MORTAL_STEP_COUNT):
        errors.extend(validate_step(character, step))
    if total_skill_dots(character) != TOTAL_SKILL_DOTS:
        errors.append(f"Total skill dots: {total_skill_dots(character)}/{TOTAL_SKILL_DOTS}.")
    return errors
