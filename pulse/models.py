from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pulse.attributes import sync_mortal_attributes
from pulse.constants import APP_VERSION, ATTRIBUTES, BASE_ATTRIBUTE_VALUE, SCHEMA_VERSION, SKILL_POOLS

EMPTY_POOLS = {pool: 0 for pool in SKILL_POOLS}


def _empty_skill_entry(category: str = "Mental", custom: bool = False) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "dots": 0,
        "pools": dict(EMPTY_POOLS),
        "category": category,
    }
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
) -> dict[str, Any]:
    mortal = character.setdefault("mortal", {})
    skills = mortal.setdefault("skills", {})
    if skill_name not in skills:
        skills[skill_name] = _empty_skill_entry(category=category, custom=custom)
    return skills[skill_name]


def recompute_skill_dots(skill_entry: dict[str, Any]) -> None:
    pools = skill_entry.get("pools", EMPTY_POOLS)
    skill_entry["dots"] = sum(int(pools.get(pool, 0)) for pool in SKILL_POOLS)


def touch_meta(character: dict[str, Any]) -> None:
    character.setdefault("meta", {})["updated_at"] = datetime.now(timezone.utc).isoformat()
    sync_mortal_attributes(character)


def character_to_json(character: dict[str, Any]) -> str:
    touch_meta(character)
    return json.dumps(character, indent=2, ensure_ascii=False)


def character_from_json(text: str) -> dict[str, Any]:
    data = json.loads(text)
    if data.get("schema_version", 1) > SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version {data.get('schema_version')}.")
    merged = new_character()
    _deep_merge(merged, data)
    touch_meta(merged)
    return merged


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
