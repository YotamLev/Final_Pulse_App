"""Shared fixtures for validation tests."""

from __future__ import annotations

from pulse.attributes import sync_mortal_attributes
from pulse.constants import TOTAL_SKILL_DOTS
from pulse.models import assign_skill_dots, ensure_skill, new_character
from pulse.vampire import ensure_vampire, new_vampire_state


def _assign_skill_dots(character: dict, budget: int, skill_names: list[str]) -> None:
    remaining = budget
    index = 0
    while remaining > 0:
        name = skill_names[index % len(skill_names)]
        entry = ensure_skill(character, name, category="Physical")
        room = min(5 - int(entry.get("dots", 0)), remaining)
        if room <= 0:
            index += 1
            if index > len(skill_names) * 6:
                raise RuntimeError(f"Could not assign {budget} skill dots")
            continue
        assign_skill_dots(entry, int(entry.get("dots", 0)) + room)
        remaining -= room
        index += 1


def minimal_mortal_character() -> dict:
    """Mortal character that passes validation through step 8."""
    character = new_character()
    character["chronicle"]["time_and_place"] = "Chicago, 1990s"
    character["mortal"]["traits"] = [
        {"name": "Studious", "plus": "Intelligence", "minus": "Strength"},
        {"name": "Alert", "plus": "Wits", "minus": "Charisma"},
        {"name": "Determined", "plus": "Resolve", "minus": "Manipulation"},
    ]
    sync_mortal_attributes(character)

    skill_names = [
        "Athletics",
        "Brawl",
        "Craft",
        "Drive",
        "Firearms",
        "Larceny",
        "Melee",
        "Stealth",
        "Survival",
        "Awareness",
        "Investigation",
        "Science",
        "Etiquette",
        "Streetwise",
        "Subterfuge",
    ]
    _assign_skill_dots(character, TOTAL_SKILL_DOTS, skill_names)

    intelligence = character["mortal"]["attributes"]["Intelligence"]
    character["mortal"]["languages"] = ["English", "Latin", "French"][:intelligence]
    character["mortal"]["specialties"] = [
        {"skill": "Athletics", "text": "parkour"},
        {"skill": "Brawl", "text": "street fights"},
    ]
    character["mortal"]["beliefs"] = "Survive at any cost."
    character["wizard_step"] = 8
    return character


def minimal_vampire_state() -> dict:
    return new_vampire_state()


def embrace_character(character: dict, clan_id: str = "veneris") -> dict:
    v = ensure_vampire(character)
    v["clan"] = clan_id
    v["bane"] = {"summary": "", "fields": {}}
    return character


def level_0_character(character: dict) -> dict:
    embrace_character(character)
    v = character["vampire"]
    v["disciplines"] = [{"name": "Dominate", "source": "clan", "acquired_at_level": 0}]
    v["powers"] = [
        {
            "id": "dominate_draw_on_instinct",
            "name": "Draw On Instinct",
            "source": "Dominate",
            "acquired_at_level": 0,
            "is_predator_power": False,
        }
    ]
    v["level"] = 0
    return character


def level_1_ready_character(character: dict) -> dict:
    level_0_character(character)
    v = character["vampire"]
    v["attribute_adjustments"] = [{"level": 1, "changes": {"Strength": 1, "Dexterity": 1}}]
    v["disciplines"].append({"name": "Protean", "source": "clan", "acquired_at_level": 1})
    v["powers"].append(
        {
            "id": "protean_animorph",
            "name": "Animorph",
            "source": "Protean",
            "acquired_at_level": 1,
            "is_predator_power": False,
        }
    )
    return character


def predator_ready_character(character: dict) -> dict:
    level_1_ready_character(character)
    v = character["vampire"]
    v["predator"] = {
        "source": "curated",
        "type": "alleycat",
        "skill_choice": {"skill": "Brawl", "dots": 2},
        "specialty": {"skill": "Brawl", "text": "back alleys"},
    }
    v["powers"].append(
        {
            "id": "potence_vigor",
            "name": "Vigor",
            "source": "Potence",
            "acquired_at_level": 1,
            "is_predator_power": True,
        }
    )
    v["level"] = 1
    return character


def level_2_ready_character(character: dict) -> dict:
    predator_ready_character(character)
    v = character["vampire"]
    v["skill_adjustments"] = [{"level": 2, "removed": {"Athletics": 2}}]
    v["attribute_adjustments"].append({"level": 2, "changes": {"Stamina": 1, "Resolve": 1}})
    v["disciplines"].append({"name": "Fortitude", "source": "clan", "acquired_at_level": 2})
    v["powers"].append(
        {
            "id": "fortitude_rapid_healing",
            "name": "Rapid Healing",
            "source": "Fortitude",
            "acquired_at_level": 2,
            "is_predator_power": False,
        }
    )
    v["level"] = 2
    return character
