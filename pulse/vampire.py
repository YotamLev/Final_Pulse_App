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


def ensure_predator(vampire: dict[str, Any]) -> dict[str, Any]:
    if vampire.get("predator") is None:
        vampire["predator"] = {"source": "curated"}
    return vampire["predator"]


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


def known_discipline_names(character: dict[str, Any]) -> list[str]:
    vampire = character.get("vampire") or {}
    return [d["name"] for d in vampire.get("disciplines", [])]


def discipline_pick_options(
    character: dict[str, Any],
    slot_index: int,
    pool: list[str],
) -> list[str]:
    """Options for editing one discipline slot without dropping the current pick."""
    taken = known_discipline_names(character)
    excluded = set(taken[:slot_index])
    options = sorted(set(pool) - excluded)
    current = taken[slot_index] if len(taken) > slot_index else None
    if current and current not in options:
        options = sorted(options + [current])
    return options


def non_predator_powers(vampire: dict[str, Any]) -> list[dict]:
    return [p for p in vampire.get("powers", []) if not p.get("is_predator_power")]


def predator_powers(vampire: dict[str, Any]) -> list[dict]:
    return [p for p in vampire.get("powers", []) if p.get("is_predator_power")]


def set_discipline_slot(
    vampire: dict[str, Any],
    index: int,
    name: str,
    source: str,
    acquired_at_level: int,
) -> None:
    discs = list(vampire.get("disciplines", []))
    entry = {"name": name, "source": source, "acquired_at_level": acquired_at_level}
    if index < len(discs):
        discs[index] = entry
    else:
        discs.append(entry)
    vampire["disciplines"] = discs


def power_entry_from_def(power: dict, level: int, *, is_predator_power: bool = False) -> dict:
    return {
        "id": power["id"],
        "name": power["name"],
        "source": power["source"] if power.get("source_type") != "amalgam" else "Amalgam",
        "acquired_at_level": level,
        "is_predator_power": is_predator_power,
    }


def upsert_non_predator_power(vampire: dict[str, Any], index: int, entry: dict) -> None:
    non_pred = list(non_predator_powers(vampire))
    if index < len(non_pred):
        non_pred[index] = entry
    elif index == len(non_pred):
        non_pred.append(entry)
    else:
        raise ValueError(
            f"Cannot set non-predator power slot {index + 1} before slot {index} is filled "
            f"({len(non_pred)} non-predator power(s) present)."
        )
    vampire["powers"] = non_pred + predator_powers(vampire)


def sync_non_predator_power(
    vampire: dict[str, Any],
    index: int,
    power: dict | None,
    level: int,
) -> None:
    """Update a wizard power slot only when a power is selected."""
    if not power:
        return
    entry = power_entry_from_def(power, level)
    existing = non_predator_powers(vampire)
    if index < len(existing) and existing[index].get("id") == entry["id"]:
        return
    upsert_non_predator_power(vampire, index, entry)


def set_predator_powers(vampire: dict[str, Any], entries: list[dict]) -> None:
    existing = predator_powers(vampire)
    merged: list[dict] = []
    for i in range(max(len(entries), len(existing))):
        if i < len(entries):
            merged.append(entries[i])
        elif i < len(existing):
            merged.append(existing[i])
    vampire["powers"] = non_predator_powers(vampire) + merged
