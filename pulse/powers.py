from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pulse.caps import known_disciplines, known_power_ids, known_power_names
from pulse.constants import DATA_DIR

POWERS_PATH = DATA_DIR / "powers.json"


@lru_cache
def load_powers_data() -> dict:
    return json.loads(POWERS_PATH.read_text(encoding="utf-8"))


def all_powers() -> list[dict]:
    return load_powers_data()["powers"]


def disciplines_list() -> list[str]:
    return load_powers_data()["disciplines"]


def sorcery_paths_list() -> list[str]:
    return load_powers_data()["sorcery_paths"]


def power_by_id(power_id: str) -> dict | None:
    for power in all_powers():
        if power["id"] == power_id:
            return power
    return None


def power_by_name(name: str) -> dict | None:
    for power in all_powers():
        if power["name"] == name:
            return power
    return None


def powers_for_sources(sources: list[str]) -> list[dict]:
    source_set = set(sources)
    return [p for p in all_powers() if p["source"] in source_set or p["source_type"] == "amalgam" and "Amalgams" in source_set]


def _powers_from_source_count(character: dict, source: str, exclude_names: list[str]) -> int:
    count = 0
    vampire = character.get("vampire") or {}
    for power in vampire.get("powers", []):
        if power["name"] in exclude_names:
            continue
        if power.get("source") == source:
            count += 1
    return count


def _evaluate_rule(rule: dict, character: dict, power_name: str) -> bool:
    rule_type = rule.get("type")
    if rule_type == "power":
        return rule["power"] in known_power_names(character)
    if rule_type == "any_powers":
        return any(name in known_power_names(character) for name in rule.get("powers", []))
    if rule_type == "disciplines":
        known = set(known_disciplines(character))
        return set(rule.get("disciplines", [])).issubset(known)
    if rule_type == "powers_from_source":
        exclude = rule.get("exclude", [power_name])
        count = _powers_from_source_count(character, rule["source"], exclude)
        return count >= int(rule.get("min_count", 1))
    if rule_type == "specialty":
        return True
    return True


def prerequisites_met(power: dict, character: dict) -> bool:
    prereq = power.get("prerequisites")
    if not prereq:
        return True
    if "all" in prereq:
        return all(_evaluate_rule(rule, character, power["name"]) for rule in prereq["all"])
    if "any" in prereq:
        return any(_evaluate_rule(rule, character, power["name"]) for rule in prereq["any"])
    return True


def amalgam_eligible(power: dict, character: dict) -> bool:
    if power.get("source_type") != "amalgam":
        return False
    prereq = power.get("prerequisites") or {}
    if "any" in prereq:
        return any(_evaluate_rule(rule, character, power["name"]) for rule in prereq["any"])
    if "all" in prereq:
        discipline_rules = [r for r in prereq["all"] if r.get("type") == "disciplines"]
        if discipline_rules:
            return all(_evaluate_rule(r, character, power["name"]) for r in discipline_rules)
    return len(known_disciplines(character)) >= 2


def available_powers(
    character: dict,
    *,
    allowed_sources: list[str] | None = None,
    include_amalgams: bool = False,
    exclude_known: bool = True,
    keep_power_id: str | None = None,
) -> list[dict]:
    results: list[dict] = []
    known_ids = known_power_ids(character)
    sources = set(allowed_sources or [])

    for power in all_powers():
        if exclude_known and power["id"] in known_ids and power["id"] != keep_power_id:
            continue
        if power.get("source_type") == "amalgam":
            if not include_amalgams:
                continue
            if power["id"] != keep_power_id and not amalgam_eligible(power, character):
                continue
        elif allowed_sources is not None and power["source"] not in sources:
            if power["id"] != keep_power_id:
                continue
        if prerequisites_met(power, character) or power["id"] == keep_power_id:
            results.append(power)
    return sorted(results, key=lambda p: (p["source"], p["name"]))


def has_predator_bonus(power: dict) -> bool:
    if "predator_bonus" in power:
        return bool(power["predator_bonus"])
    summary = power.get("summary", "").lower()
    bonus_text = power.get("predator_bonus_text", "").lower()
    return "if chosen as predator" in summary or "if chosen as predator" in bonus_text
