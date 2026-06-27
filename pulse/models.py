from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pulse.attributes import sync_mortal_attributes
from pulse.constants import APP_VERSION, ATTRIBUTES, BASE_ATTRIBUTE_VALUE, SCHEMA_VERSION, SKILL_POOLS
from pulse.skills import (
    base_for_skill,
    base_skill_max,
    is_base_skill,
    is_specialty_skill,
    skill_kind,
    specialty_category,
    specialty_skill_max,
)

EMPTY_POOLS = {pool: 0 for pool in SKILL_POOLS}


def _empty_skill_entry(
    *,
    kind: str = "specialty",
    category: str = "Mental",
    base_skill: str | None = None,
    custom: bool = False,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "dots": 0,
        "kind": kind,
        "pools": dict(EMPTY_POOLS),
        "category": category,
    }
    if base_skill:
        entry["base_skill"] = base_skill
    if custom:
        entry["custom"] = True
    return entry


def new_character() -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": SCHEMA_VERSION,
        "wizard_step": 1,
        "character": {"name": ""},
        "chronicle": {"name": "", "time_and_place": ""},
        "concept": {
            "childhood": "",
            "adulthood": "",
            "personality": "",
            "mannerisms": "",
        },
        "mortal": {
            "traits": [
                {"name": "", "plus": ATTRIBUTES[0], "minus": ATTRIBUTES[1]},
                {"name": "", "plus": ATTRIBUTES[2], "minus": ATTRIBUTES[3]},
                {"name": "", "plus": ATTRIBUTES[4], "minus": ATTRIBUTES[5]},
            ],
            "attributes": {name: BASE_ATTRIBUTE_VALUE for name in ATTRIBUTES},
            "skills": {},
            "languages": [],
            "specialties": [
                {"skill": "", "text": ""},
                {"skill": "", "text": ""},
            ],
            "beliefs": "",
            "relations_and_resources": "",
        },
        "vampire": None,
        "meta": {
            "created_at": now,
            "updated_at": now,
            "app_version": APP_VERSION,
        },
    }


def ensure_skill(
    character: dict[str, Any],
    skill_name: str,
    category: str = "Mental",
    custom: bool = False,
    *,
    kind: str | None = None,
    base_skill: str | None = None,
) -> dict[str, Any]:
    mortal = character.setdefault("mortal", {})
    skills = mortal.setdefault("skills", {})
    if skill_name not in skills:
        if kind is None:
            if is_base_skill(skill_name):
                kind = "base"
            else:
                kind = "specialty"
        if kind == "specialty" and not base_skill and not custom:
            base_skill = base_for_skill(skill_name)
        if kind == "specialty" and not custom:
            category = specialty_category(skill_name)
        skills[skill_name] = _empty_skill_entry(
            kind=kind,
            category=category,
            base_skill=base_skill,
            custom=custom,
        )
    entry = skills[skill_name]
    if base_skill and not entry.get("base_skill"):
        entry["base_skill"] = base_skill
    if kind and not entry.get("kind"):
        entry["kind"] = kind
    return entry


def assign_skill_dots(skill_entry: dict[str, Any], dots: int, *, skill_name: str = "") -> None:
    kind = skill_kind(skill_name, skill_entry)
    cap = base_skill_max() if kind == "base" else specialty_skill_max()
    skill_entry["dots"] = max(0, min(int(dots), cap))
    skill_entry["pools"] = dict(EMPTY_POOLS)


def recompute_skill_dots(skill_entry: dict[str, Any]) -> None:
    pools = skill_entry.get("pools", EMPTY_POOLS)
    pool_sum = sum(int(pools.get(pool, 0)) for pool in SKILL_POOLS)
    if pool_sum > 0:
        skill_entry["dots"] = pool_sum
    elif "dots" not in skill_entry:
        skill_entry["dots"] = 0


def touch_meta(character: dict[str, Any]) -> None:
    character.setdefault("meta", {})["updated_at"] = datetime.now(timezone.utc).isoformat()
    sync_mortal_attributes(character)


def character_to_json(character: dict[str, Any]) -> str:
    touch_meta(character)
    return json.dumps(character, indent=2, ensure_ascii=False)


def _migrate_skills_v2(character: dict[str, Any]) -> None:
    from pulse.skills import specialty_to_base_map

    mapping = specialty_to_base_map()
    mortal = character.setdefault("mortal", {})
    skills = mortal.get("skills", {})
    migrated: dict[str, Any] = {}
    for name, entry in skills.items():
        entry = dict(entry)
        if is_base_skill(name):
            entry["kind"] = "base"
        elif name in mapping or entry.get("custom"):
            entry.setdefault("kind", "specialty")
            entry.setdefault("base_skill", mapping.get(name))
            entry.setdefault("category", specialty_category(name) if name in mapping else entry.get("category", "Mental"))
        else:
            entry.setdefault("kind", "specialty")
        migrated[name] = entry
    mortal["skills"] = migrated


def character_from_json(text: str) -> dict[str, Any]:
    data = json.loads(text)
    if data.get("schema_version", 1) > SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version {data.get('schema_version')}.")
    merged = new_character()
    _deep_merge(merged, data)
    if int(merged.get("schema_version", 1)) < SCHEMA_VERSION:
        _migrate_skills_v2(merged)
        merged["schema_version"] = SCHEMA_VERSION
    merged["wizard_step"] = _migrate_wizard_step(int(merged.get("wizard_step", 1)))
    for entry in merged.get("mortal", {}).get("skills", {}).values():
        recompute_skill_dots(entry)
    touch_meta(merged)
    return merged


def _migrate_wizard_step(step: int) -> int:
    """Map wizard_step from older layouts to current 16-step layout."""
    if step <= 3:
        return step
    if step <= 7:
        return 4
    if step <= 11:
        return step - 3
    step = step - 3
    if step >= 15:
        step -= 1
    return min(step, 16)


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> None:
    for key, value in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def export_filename(character: dict[str, Any]) -> str:
    name = character.get("character", {}).get("name", "").strip()
    if not name:
        name = character.get("chronicle", {}).get("name", "").strip()
    if not name:
        name = "character"
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    return f"{safe}_pulse.json"
