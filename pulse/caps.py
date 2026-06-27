from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pulse.constants import DATA_DIR

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


def get_skill_dots(character: dict[str, Any]) -> dict[str, int]:
    skills: dict[str, int] = {}
    for name, entry in character.get("mortal", {}).get("skills", {}).items():
        skills[name] = int(entry.get("dots", 0))

    vampire = character.get("vampire") or {}
    predator = vampire.get("predator") or {}
    if predator.get("skill_choice"):
        sk = predator["skill_choice"].get("skill")
        dots = int(predator["skill_choice"].get("dots", 0))
        if sk:
            skills[sk] = skills.get(sk, 0) + dots

    for block in vampire.get("skill_adjustments", []):
        for name, delta in block.get("removed", {}).items():
            skills[name] = max(0, skills.get(name, 0) - int(delta))
        for name, delta in block.get("added", {}).items():
            skills[name] = skills.get(name, 0) + int(delta)

    for level_up in vampire.get("level_ups", []):
        if level_up.get("choice") == "skills":
            for name, delta in level_up.get("details", {}).items():
                skills[name] = skills.get(name, 0) + int(delta)
    return skills
