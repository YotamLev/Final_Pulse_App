from __future__ import annotations

import json
from functools import lru_cache

from pulse.constants import DATA_DIR


@lru_cache
def load_skill_tree() -> dict:
    return json.loads((DATA_DIR / "skill_tree.json").read_text(encoding="utf-8"))


@lru_cache
def load_skills() -> list[dict[str, str]]:
    """Flat specialty list with categories (legacy helper)."""
    tree = load_skill_tree()
    return [
        {"name": name, "category": category}
        for name, category in tree["specialty_categories"].items()
    ]


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
    from pulse.skills import base_skill_names

    mapping = {name: "General" for name in base_skill_names()}
    mapping.update(load_skill_tree()["specialty_categories"])
    return mapping
