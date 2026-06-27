"""Base + specialty skill tree rules."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pulse.constants import DATA_DIR

TREE_PATH = DATA_DIR / "skill_tree.json"


@lru_cache
def _tree_data() -> dict[str, Any]:
    return json.loads(TREE_PATH.read_text(encoding="utf-8"))


def base_skill_names() -> list[str]:
    return [entry["name"] for entry in _tree_data()["bases"]]


def specialty_names() -> list[str]:
    names: list[str] = []
    for entry in _tree_data()["bases"]:
        names.extend(entry["specialties"])
    return names


def all_skill_names() -> list[str]:
    return base_skill_names() + specialty_names()


def specialty_to_base_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in _tree_data()["bases"]:
        for specialty in entry["specialties"]:
            mapping[specialty] = entry["name"]
    return mapping


def specialties_for_base(base: str) -> list[str]:
    for entry in _tree_data()["bases"]:
        if entry["name"] == base:
            return list(entry["specialties"])
    return []


def specialty_category(name: str) -> str:
    return _tree_data()["specialty_categories"].get(name, "Mental")


def base_skill_max() -> int:
    return int(_tree_data()["base_max"])


def specialty_skill_max() -> int:
    return int(_tree_data()["specialty_max"])


def creation_skill_dots() -> int:
    return int(_tree_data()["creation_dots"])


def is_base_skill(name: str) -> bool:
    return name in base_skill_names()


def is_specialty_skill(name: str) -> bool:
    return name in specialty_to_base_map()


def base_for_skill(name: str, entry: dict[str, Any] | None = None) -> str | None:
    if is_base_skill(name):
        return name
    if entry and entry.get("base_skill"):
        return str(entry["base_skill"])
    return specialty_to_base_map().get(name)


def skill_kind(name: str, entry: dict[str, Any] | None = None) -> str:
    if entry and entry.get("kind"):
        return str(entry["kind"])
    if is_base_skill(name):
        return "base"
    if is_specialty_skill(name) or (entry and entry.get("custom")):
        return "specialty"
    return "specialty"


def raw_skill_dots(character: dict[str, Any]) -> dict[str, int]:
    skills: dict[str, int] = {}
    for name, entry in character.get("mortal", {}).get("skills", {}).items():
        dots = int(entry.get("dots", 0))
        if dots > 0:
            skills[name] = dots
    return skills


def base_dots_map(character: dict[str, Any]) -> dict[str, int]:
    raw = raw_skill_dots(character)
    return {base: raw.get(base, 0) for base in base_skill_names()}


def effective_specialty_rating(
    character: dict[str, Any],
    specialty: str,
    *,
    raw: dict[str, int] | None = None,
) -> int:
    """Specialty rating = base dots in tree + specialty dots (e.g. 2 Reaction + 1 Athletics → 3 Athletics)."""
    if raw is None:
        raw = raw_skill_dots(character)
    entry = character.get("mortal", {}).get("skills", {}).get(specialty, {})
    base = base_for_skill(specialty, entry)
    if not base:
        return raw.get(specialty, 0)
    return int(raw.get(specialty, 0)) + int(raw.get(base, 0))


def total_assigned_skill_dots(character: dict[str, Any]) -> int:
    return sum(raw_skill_dots(character).values())


def max_raw_specialty_dots(character: dict[str, Any], specialty: str) -> int:
    """Max dots assignable on the specialty entry (raw), before cap extensions."""
    entry = character.get("mortal", {}).get("skills", {}).get(specialty, {})
    base = base_for_skill(specialty, entry)
    base_part = int(raw_skill_dots(character).get(base or "", 0)) if base else 0
    return max(0, specialty_skill_max() - base_part)


def validate_skill_allocation(character: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    raw = raw_skill_dots(character)
    assigned = sum(raw.values())
    budget = creation_skill_dots()
    if assigned != budget:
        errors.append(f"Assign exactly {budget} skill dots ({assigned}/{budget}).")

    for name, dots in raw.items():
        entry = character.get("mortal", {}).get("skills", {}).get(name, {})
        kind = skill_kind(name, entry)
        if kind == "base":
            if dots > base_skill_max():
                errors.append(f"{name} (base) cannot exceed {base_skill_max()} dots (has {dots}).")
            continue

        base = base_for_skill(name, entry)
        if not base:
            errors.append(f"{name}: choose a base skill.")
            continue
        if entry.get("custom") and not entry.get("base_skill"):
            errors.append(f"Custom skill '{name}' must list a base skill.")
        if dots > specialty_skill_max():
            errors.append(f"{name} cannot exceed {specialty_skill_max()} specialty dots (has {dots}).")
        effective = effective_specialty_rating(character, name, raw=raw)
        if effective > specialty_skill_max():
            errors.append(
                f"{name} effective rating exceeds {specialty_skill_max()} "
                f"({effective} = {raw.get(name, 0)} specialty + {raw.get(base, 0)} base)."
            )

    for name, entry in character.get("mortal", {}).get("skills", {}).items():
        if entry.get("custom") and not str(name).strip():
            errors.append("Custom skills need a name.")
    return errors


def skills_with_room_for_dots(
    character: dict[str, Any],
    *,
    grant: int,
    effective_cap_fn,
) -> list[str]:
    """Skills that can receive `grant` dots without exceeding effective cap."""
    candidates: list[str] = []
    for specialty in specialty_names():
        current = effective_specialty_rating(character, specialty)
        if current + grant <= effective_cap_fn(character, specialty):
            candidates.append(specialty)
    for name, entry in character.get("mortal", {}).get("skills", {}).items():
        if entry.get("custom") and name not in candidates:
            current = effective_specialty_rating(character, name)
            if current + grant <= effective_cap_fn(character, name):
                candidates.append(name)
    return sorted(set(candidates))
