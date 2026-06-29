"""Clan definitions and eligibility checker for Final Pulse 2E."""

from __future__ import annotations

from pulse.data.traits import MENTAL_ILLNESS_KEYS

# requirements keys:
#   trait_any   : at least one of these trait keys must be present (mortal or vampire)
#   discipline_any: at least one of these disciplines must be unlocked
#   discipline_all: all of these disciplines must be unlocked

CLANS: dict[str, dict] = {
    "Ventrue": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Ventrue_symbol.png&width=1280",
        "description": "The self-styled rulers of vampire society, masters of control, who believe it is their birthright to lead.",
        "recruitment": "Generals, Lords, Gang Leaders",
        "requirements": {
            "trait_any": ["selective_taste"],
            "discipline_all": ["Dominate"],
        },
        "bonus": "Connected — you gain significant advantages to find useful vampires and advance your status.",
        "suggested_disciplines": ["Fortitude", "Presence"],
    },
    "Dracul": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Tzimisce_symbol.png&width=1280",
        "description": "The main competitors of the Ventrue, fiercely stubborn. Known to ruin potential Embracees' lives to 'test' whether they are cut out for the Clan.",
        "recruitment": "Crusaders, Fierce Nationalists, Merchant Princes",
        "requirements": {
            "trait_any": ["territorial", "archaic"],
        },
        "bonus": "Vengeful — you can Blood Surge and pay only half when pursuing vengeance against one target at a time, once per scene.",
        "suggested_disciplines": ["Dominate", "Protean", "Potence"],
    },
    "Toreador": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Toreador_symbol.png&width=1280",
        "description": "Connoisseurs of ascendant beauty and emotion, drawn irresistibly to the artistic and the sublime.",
        "recruitment": "Artists, Diplomats, Charismatic Clergy",
        "requirements": {
            "trait_any": ["infatuation", "rare_specialist", "world_renowned_specialist"],
            "discipline_all": ["Presence"],
        },
        "bonus": "Gentle Touch — you anger targets of Presence, Auspex, and Dominate less if they discover they've been influenced. Gain +2 on rolls to blood-bond others.",
        "suggested_disciplines": ["Auspex", "Celerity"],
    },
    "Nosferatu": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Nosferatu_symbol.png&width=1280",
        "description": "Hidden eyes and ears of the vampire world, cursed with a grotesque appearance that separates them from mortal society.",
        "recruitment": "Spymasters, Assassins, Mercenaries",
        "requirements": {
            "trait_any": ["ugly", "corpse_like"],
            "discipline_all": ["Obfuscate"],
        },
        "bonus": "Cryptomania — you heal Willpower when finding hidden information or things due to a focused, unnerving curiosity. Gain an advantage convincing Vampires to share information via trade.",
        "suggested_disciplines": ["Nightmare", "Shadow Sorcery", "Animalism"],
    },
    "Brujah": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Brujah_symbol.png&width=1280",
        "description": "Philosophers, fighters, rebels, gladiators. A history of great thinkers, generals, and revolutionaries.",
        "recruitment": "Anarchists, Soldiers, Disloyal Knights",
        "requirements": {
            "trait_any": ["prone_to_rage"],
            "discipline_any": ["Potence", "Celerity"],
        },
        "bonus": "Freedom — heals Willpower twice as fast.",
        "suggested_disciplines": ["Presence", "Potence", "Celerity"],
    },
    "Gangrel": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Gangrel_symbol.png&width=1280",
        "description": "Wild vampires described as closest to their Beast, who maintain they are simply best at interacting with it.",
        "recruitment": "Survivalists, Conquistadors, Raiders",
        "requirements": {
            "trait_any": ["ravenous"],
            "discipline_any": ["Animalism", "Protean"],
        },
        "bonus": "Can stay awake an hour after dawn and wake up half an hour before sunset.",
        "suggested_disciplines": ["Animalism", "Protean", "Fortitude"],
    },
    "Malkavian": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Malkavian_symbol.png&width=1280",
        "description": "Afflicted by a supernatural madness — the clan of seers and oracles. The most heterogeneous clan.",
        "recruitment": "Odd Scientists, Genius Detectives, Shamans",
        "requirements": {
            "trait_any_malkavian": True,  # special handling: mental illness traits
        },
        "bonus": "Prophetic — you can make a cryptic, vague, or riddle prophecy and have it be fulfilled. Only one prophecy active at a time.",
        "suggested_disciplines": ["Auspex", "Nightmare", "Arrete"],
    },
    "Tremere": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Tremere_symbol.png&width=1280",
        "description": "Mages who sought immortality. In their greed, they instigated a terrifying magical experiment, damning themselves to a hell of their own making.",
        "recruitment": "Occultists, Pagans, Academics",
        "requirements": {
            "trait_any": ["infatuation", "rare_specialist", "world_renowned_specialist"],
            "discipline_all": ["Blood Sorcery"],
        },
        "bonus": "Ritual Magic — can find other Tremere to cast spells together; somewhat tolerated by other mages.",
        "suggested_disciplines": ["Auspex", "Arrete"],
    },
    "Hecata": {
        "image": "https://vtm.paradoxwikis.com/thumb.php?f=Hecata_symbol.png&width=1920",
        "description": "A strange clan steeped in death, practising the arts of necromancy. Favors Embracing from their own mortal family or those with useful outside connections.",
        "recruitment": "Bankers, Arms Dealers, Monks",
        "requirements": {
            "trait_any": ["painful_bite", "selective_mutism"],
            "discipline_all": ["Necromancy"],
        },
        "bonus": "Private — spend 1 Willpower to automatically succeed against Insight, Aura Reading, or Dominate.",
        "suggested_disciplines": ["Fortitude", "Potence"],
    },
}


def check_clan_eligibility(clan_name: str, char: dict) -> bool:
    """Return True if the character meets all requirements for the given clan."""
    clan = CLANS.get(clan_name)
    if clan is None:
        return False

    reqs = clan["requirements"]
    all_trait_keys: set[str] = {t["key"] for t in char.get("mortal_traits", [])} | {
        t["key"] for t in char.get("vampire_traits", [])
    }
    disc_names: set[str] = set(char.get("unlocked_disciplines", []))

    # Special Malkavian requirement: at least one mental illness trait
    if reqs.get("trait_any_malkavian"):
        if not (all_trait_keys & MENTAL_ILLNESS_KEYS):
            return False

    if "trait_any" in reqs:
        if not any(k in all_trait_keys for k in reqs["trait_any"]):
            return False

    if "discipline_all" in reqs:
        if not all(d in disc_names for d in reqs["discipline_all"]):
            return False

    if "discipline_any" in reqs:
        if not any(d in disc_names for d in reqs["discipline_any"]):
            return False

    return True


def get_eligible_clans(char: dict) -> list[str]:
    """Return sorted list of clan names the character currently qualifies for."""
    return [name for name in CLANS if check_clan_eligibility(name, char)]
