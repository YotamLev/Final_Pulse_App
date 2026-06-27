from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache
def load_skills() -> list[dict[str, str]]:
    return json.loads((DATA_DIR / "skills.json").read_text(encoding="utf-8"))


@lru_cache
def load_trait_suggestions() -> list[dict[str, str]]:
    return json.loads((DATA_DIR / "trait_suggestions.json").read_text(encoding="utf-8"))


@lru_cache
def load_language_suggestions() -> list[str]:
    return json.loads((DATA_DIR / "language_suggestions.json").read_text(encoding="utf-8"))


@lru_cache
def load_clans() -> list[dict]:
    return json.loads((DATA_DIR / "clans.json").read_text(encoding="utf-8"))


@lru_cache
def load_predator_types() -> list[dict]:
    return json.loads((DATA_DIR / "predator_types.json").read_text(encoding="utf-8"))


def predator_type_by_id(type_id: str) -> dict | None:
    for entry in load_predator_types():
        if entry["id"] == type_id:
            return entry
    return None


def skill_category_map() -> dict[str, str]:
    return {item["name"]: item["category"] for item in load_skills()}
