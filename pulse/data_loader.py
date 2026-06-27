from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

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


def skill_category_map() -> dict[str, str]:
    return {item["name"]: item["category"] for item in load_skills()}
