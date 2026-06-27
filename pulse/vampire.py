from __future__ import annotations

from typing import Any

from pulse.data_loader import load_clans


def ensure_vampire(character: dict[str, Any]) -> dict[str, Any]:
    if character.get("vampire") is None:
        character["vampire"] = new_vampire_state()
    return character["vampire"]


def new_vampire_state() -> dict[str, Any]:
    return {
        "level": 0,
        "clan": "",
        "bane": {"summary": "", "fields": {}},
        "disciplines": [],
        "powers": [],
        "predator": None,
        "attribute_adjustments": [],
        "skill_adjustments": [],
        "specialty_adjustments": [],
        "level_ups": [],
        "cap_choices": {},
    }


def clan_by_id(clan_id: str) -> dict | None:
    for clan in load_clans():
        if clan["id"] == clan_id:
            return clan
    return None


def add_discipline(character: dict[str, Any], name: str, source: str, level: int) -> None:
    vampire = ensure_vampire(character)
    if any(d["name"] == name for d in vampire["disciplines"]):
        return
    vampire["disciplines"].append({"name": name, "source": source, "acquired_at_level": level})


def add_power(
    character: dict[str, Any],
    power: dict,
    level: int,
    *,
    is_predator_power: bool = False,
) -> None:
    vampire = ensure_vampire(character)
    if any(p["id"] == power["id"] for p in vampire["powers"]):
        return
    vampire["powers"].append(
        {
            "id": power["id"],
            "name": power["name"],
            "source": power["source"] if power.get("source_type") != "amalgam" else "Amalgam",
            "acquired_at_level": level,
            "is_predator_power": is_predator_power,
        }
    )


def get_clan_disciplines(character: dict[str, Any]) -> list[str]:
    vampire = character.get("vampire") or {}
    clan = clan_by_id(vampire.get("clan", ""))
    return clan["disciplines"] if clan else []
