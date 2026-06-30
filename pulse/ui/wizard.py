"""Character Creation Wizard — Five stages for Final Pulse 2E."""

from __future__ import annotations

import streamlit as st

from pulse.data.traits import MORTAL_TRAITS, VAMPIRE_TRAITS, get_mortal_trait, get_vampire_trait
from pulse.data.skill_trees import (
    SKILL_TREES,
    can_add_dot,
    can_remove_dot,
    get_effective_level,
    get_static_base,
    get_achieved_base,
    xp_cost_for_next_dot,
    total_skill_xp,
)
from pulse.data.disciplines import (
    DISCIPLINES,
    ALL_DISCIPLINE_NAMES,
    MAX_DISCIPLINES,
    DISC_SHORT_DESC,
    get_available_powers,
    total_disc_xp,
    xp_cost_for_disc_level,
)
from pulse.data.clans import CLANS, get_eligible_clans
from pulse.models.character import (
    CREATION_SKILL_XP,
    CREATION_DISC_XP,
    MAX_TRAITS,
    MAX_TRAIT_COST,
    get_total_trait_cost,
    get_trait_count,
    log_xp_spend,
    log_xp_refund,
)
from pulse.ui.components import dots, section_header, info_box


# ── Stage labels ──────────────────────────────────────────────────────────────

STAGES = {
    1: "Origins & Traits",
    2: "Skills",
    3: "Disciplines",
    4: "Clan",
}

# ── Quick Start archetypes ────────────────────────────────────────────────────
# Each entry pre-fills a clan, qualifying trait, discipline unlocks, and a
# small skill seed so the player can dive straight into the biography.

QUICKSTARTS: dict[str, dict] = {
    "ventrue_commander": {
        "label": "Ventrue Commander",
        "name": "Marcus St. Claire",
        "clan": "Ventrue",
        "tagline": "Nobles of the night. Rule through command, wealth, and iron will.",
        "backstory": (
            "Chicago's most feared litigator, St. Claire dismantled corporations and careers "
            "with equal precision from his Loop office. Annalise of Clan Ventrue watched him "
            "destroy a rival's empire in court and made her offer — eternity in exchange for his talent."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "selective_taste", "name": "Selective Taste",
            "cost": -1, "detail": "The powerful and well-bred", "sub_choice": None,
        },
        "disciplines": ["Dominate", "Fortitude", "Presence"],
        "discipline_levels": {"Dominate": 3, "Fortitude": 1, "Presence": 2},
        "discipline_powers": {
            "Dominate": ["Draw On Instinct", "Mesmerize", "Implant Trigger"],
            "Fortitude": ["Toughness"],
            "Presence": ["Awe", "Midnight Command"],
        },
        "skill_dots": {
            "Basic Analytical": 2, "Finance": 1, "Mortal Politics": 1,
            "Basic Manipulation": 2, "Persuasion": 1,
        },
    },
    "dracul_warlord": {
        "label": "Dracul Warlord",
        "name": "Viktor Harken",
        "clan": "Dracul",
        "tagline": "Immovable and vengeful. No one trespasses on what is yours.",
        "backstory": (
            "A Balkan mercenary who made his name in post-war chaos, Harken arrived in "
            "Chicago in '94 running private security contracts. His Sire found him useful — "
            "and simply unwilling to die. An appropriate quality for the Clan."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "territorial", "name": "Territorial",
            "cost": -2, "detail": None, "sub_choice": None,
        },
        "disciplines": ["Dominate", "Protean", "Potence"],
        "discipline_levels": {"Dominate": 1, "Protean": 3, "Potence": 2},
        "discipline_powers": {
            "Dominate": ["Draw On Instinct"],
            "Protean": ["Feral Weapons", "Bone Bullets", "Bone Armor"],
            "Potence": ["Vigor", "Brutal Feed"],
        },
        "skill_dots": {
            "Basic Manipulation": 2, "Intimidation": 1,
            "Brawl": 2, "Martial Arts": 1,
            "Awareness": 2,
        },
    },
    "toreador_manipulator": {
        "label": "Toreador Manipulator",
        "name": "Celeste Vane",
        "clan": "Toreador",
        "tagline": "Beauty as a weapon. Emotion as a lever. Every room is a stage.",
        "backstory": (
            "Celeste built Chicago's River North into a scene by sheer force of taste and charm. "
            "She was Embraced in 1987 by a mid-century Toreador who grew obsessed with her eye "
            "for beauty, and now navigates Elysium with the same precision as a gallery opening."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "infatuation", "name": "Infatuation",
            "cost": -1, "detail": None, "sub_choice": None,
        },
        "disciplines": ["Presence", "Auspex", "Celerity"],
        "discipline_levels": {"Presence": 3, "Auspex": 1, "Celerity": 2},
        "discipline_powers": {
            "Presence": ["Awe", "Affect Mood", "Hypnotize"],
            "Auspex": ["Impulse"],
            "Celerity": ["Speed", "The Still World"],
        },
        "skill_dots": {
            "Basic Manipulation": 2, "Persuasion": 1, "Court Etiquette": 1,
            "Insight": 2, "Deception": 1,
        },
    },
    "nosferatu_spymaster": {
        "label": "Nosferatu Spymaster",
        "name": "Grim",
        "clan": "Nosferatu",
        "tagline": "Unseen and unavoidable. The city's secrets flow through your hands.",
        "backstory": (
            "A disgraced NSA analyst who learned too much about the undead world and was "
            "consequently Embraced rather than silenced. Grim runs intelligence from Chicago's "
            "tunnel network, selling information to anyone worth knowing."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "corpse_like", "name": "Corpse-Like",
            "cost": -2, "detail": None, "sub_choice": None,
        },
        "disciplines": ["Obfuscate", "Nightmare", "Shadow Sorcery"],
        "discipline_levels": {"Obfuscate": 3, "Nightmare": 2, "Shadow Sorcery": 1},
        "discipline_powers": {
            "Obfuscate": ["Fade", "Vanish", "Silent Hunter"],
            "Nightmare": ["Haunt Dream", "Lullaby"],
            "Shadow Sorcery": ["Dim the Lights"],
        },
        "skill_dots": {
            "Basic Analytical": 2, "Investigation": 1,
            "Awareness": 2, "Stealth": 2, "Streetwise": 1,
        },
    },
    "brujah_rebel": {
        "label": "Brujah Rebel",
        "name": "Dex Malone",
        "clan": "Brujah",
        "tagline": "Passionate and explosive. Fight for the cause — or just fight.",
        "backstory": (
            "A union organizer and fixture of Chicago's punk circuit, Dex fought systems "
            "before he had the strength to break them. His Brujah Sire caught him mid-brawl "
            "outside a Bridgeport tavern and decided the city needed his fire."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "prone_to_rage", "name": "Prone to Rage",
            "cost": -2, "detail": None, "sub_choice": None,
        },
        "disciplines": ["Potence", "Celerity", "Presence"],
        "discipline_levels": {"Potence": 3, "Celerity": 2, "Presence": 1},
        "discipline_powers": {
            "Potence": ["Vigor", "Shockwave", "Bloody Strangle"],
            "Celerity": ["Speed", "The Still World"],
            "Presence": ["Awe"],
        },
        "skill_dots": {
            "Brawl": 2, "Martial Arts": 1, "Athletics": 1,
            "Awareness": 1, "Basic Manipulation": 2, "Guns": 1, "Intimidation": 1,
        },
    },
    "gangrel_wanderer": {
        "label": "Gangrel Wanderer",
        "name": "Reva",
        "clan": "Gangrel",
        "tagline": "Predator and survivor. The wild is your haven, the beast your compass.",
        "backstory": (
            "A wilderness guide from Minnesota who came south following a trail and found "
            "something hunting her in return. The Embrace changed her direction but not her "
            "nature. She haunts the forest preserves and Chicago's industrial edges."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "ravenous", "name": "Ravenous",
            "cost": -3, "detail": None, "sub_choice": None,
        },
        "disciplines": ["Animalism", "Protean", "Fortitude"],
        "discipline_levels": {"Animalism": 3, "Protean": 1, "Fortitude": 2},
        "discipline_powers": {
            "Animalism": ["Ghoul Animal", "Borrowed Wisdom", "Confront the Beast"],
            "Protean": ["Feral Weapons"],
            "Fortitude": ["Rapid Healing", "Toughness"],
        },
        "skill_dots": {
            "Awareness": 2, "Survival": 1, "Athletics": 2,
            "Brawl": 2, "Stealth": 2,
        },
    },
    "malkavian_oracle": {
        "label": "Malkavian Oracle",
        "name": "Pip",
        "clan": "Malkavian",
        "tagline": "Madness and prophecy walk hand in hand. You see what others cannot.",
        "backstory": (
            "A behavioral economist at U of C whose gift for reading systems was simply too "
            "unsettling to ignore. The Embrace fractured Pip's already-strange mind into "
            "something genuinely prophetic — and genuinely difficult to follow in conversation."
        ),
        "mortal_trait": {
            "key": "paranoid", "name": "Paranoid",
            "cost": -2, "detail": None, "sub_choice": None,
        },
        "vampire_trait": None,
        "disciplines": ["Auspex", "Nightmare", "Arrete"],
        "discipline_levels": {"Auspex": 3, "Nightmare": 1, "Arrete": 2},
        "discipline_powers": {
            "Auspex": ["Impulse", "Read Aura", "Telepathy"],
            "Nightmare": ["Haunt Dream"],
            "Arrete": ["Calculating", "Borrowed Knowledge"],
        },
        "skill_dots": {
            "Basic Analytical": 2, "Insight": 2,
            "Curiosity": 2, "Awareness": 1, "Basic Manipulation": 2, "Dodge": 1, "Stealth": 1,
        },
    },
    "tremere_warlock": {
        "label": "Tremere Warlock",
        "name": "Adara Voss",
        "clan": "Tremere",
        "tagline": "Mages who sought eternity and found damnation. Power has a price.",
        "backstory": (
            "A rare books archivist recruited by Chicago's Emerald Circle Chantry with "
            "promises of access to texts that don't exist in libraries. The blood bond "
            "was not disclosed in the recruitment materials."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "infatuation", "name": "Infatuation",
            "cost": -1, "detail": None, "sub_choice": None,
        },
        "disciplines": ["Blood Sorcery", "Auspex", "Arrete"],
        "discipline_levels": {"Blood Sorcery": 3, "Auspex": 2, "Arrete": 1},
        "discipline_powers": {
            "Blood Sorcery": ["Bend Blood", "Bend Veins", "Telekinesis"],
            "Auspex": ["Enhance Senses", "Sense The Unseen"],
            "Arrete": ["Calculating"],
        },
        "skill_dots": {
            "Basic Analytical": 2, "Social Academics": 1,
            "Curiosity": 2, "Occult": 1, "Insight": 2,
        },
    },
    "hecata_necromancer": {
        "label": "Hecata Necromancer",
        "name": "Father Ioseph",
        "clan": "Hecata",
        "tagline": "Death is a doorway. You hold the key — and the business card.",
        "backstory": (
            "A Catholic priest who ministered to a Hecata-affiliated family for a decade "
            "before learning what they were. The Clan offered eternity when they realized "
            "his networks of grief and trust were worth more than his silence."
        ),
        "mortal_trait": None,
        "vampire_trait": {
            "key": "painful_bite", "name": "Painful Bite",
            "cost": -2, "detail": None, "sub_choice": None,
        },
        "disciplines": ["Necromancy", "Fortitude", "Potence"],
        "discipline_levels": {"Necromancy": 3, "Fortitude": 1, "Potence": 2},
        "discipline_powers": {
            "Necromancy": ["Touch of Oblivion", "Raise Corpse", "Kill the Vibe"],
            "Fortitude": ["Rapid Healing"],
            "Potence": ["Vigor", "Bloody Strangle"],
        },
        "skill_dots": {
            "Curiosity": 2, "Occult": 1,
            "Basic Analytical": 2, "Medicine": 2, "Logistics": 1,
        },
    },
}


def _apply_quickstart(char: dict, key: str) -> None:
    qs = QUICKSTARTS[key]
    char["name"] = qs.get("name", "")
    char["tagline"] = qs.get("tagline", "")
    char["memories"] = qs.get("backstory", "")
    char["clan"] = qs["clan"]
    char["unlocked_disciplines"] = list(qs["disciplines"])
    char["discipline_levels"] = dict(qs.get("discipline_levels", {}))
    char["discipline_powers"] = {k: list(v) for k, v in qs.get("discipline_powers", {}).items()}
    char["skill_dots"] = dict(qs["skill_dots"])
    char["mortal_traits"] = []
    char["vampire_traits"] = []
    if qs.get("mortal_trait"):
        char["mortal_traits"].append(qs["mortal_trait"])
    if qs.get("vampire_trait"):
        char["vampire_traits"].append(qs["vampire_trait"])
    # Reset log and seed entries so refunds can cancel cleanly
    char["xp_log"] = []
    for tree_name, tree in SKILL_TREES.items():
        for skill_name in tree:
            n = qs["skill_dots"].get(skill_name, 0)
            for d in range(n):
                cost = xp_cost_for_next_dot(skill_name, tree_name, {skill_name: d})
                log_xp_spend(char, f"{skill_name} +1 dot", cost)
    for disc_name, level in qs.get("discipline_levels", {}).items():
        for lv in range(level):
            log_xp_spend(char, f"{disc_name} level {lv} → {lv + 1}", xp_cost_for_disc_level(lv))


def _render_quickstart_panel(char: dict) -> None:
    with st.expander("⚡ Quick Start — know your clan? Begin here", expanded=not char.get("clan")):
        st.caption(
            "Pick an archetype to pre-fill name, backstory, clan, traits, disciplines with "
            "starting powers, and a full skill package. Everything can be edited afterwards."
        )

        # Pre-select from applied clan on first render
        if "qs_grid_sel" not in st.session_state:
            for k, v in QUICKSTARTS.items():
                if v["clan"] == char.get("clan"):
                    st.session_state["qs_grid_sel"] = k
                    break

        # 3-column clan-symbol grid
        qs_keys = list(QUICKSTARTS.keys())
        cols = st.columns(3)
        for i, key in enumerate(qs_keys):
            qs_card = QUICKSTARTS[key]
            with cols[i % 3]:
                clan_img = CLANS.get(qs_card["clan"], {}).get("image", "")
                if clan_img:
                    try:
                        st.image(clan_img, width=56)
                    except Exception:
                        pass
                is_sel = st.session_state.get("qs_grid_sel") == key
                if st.button(
                    qs_card["label"],
                    key=f"qs_grid_{key}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary",
                ):
                    st.session_state["qs_grid_sel"] = key
                    st.rerun()

        # Preview + apply for the selected archetype
        sel = st.session_state.get("qs_grid_sel")
        if sel and sel in QUICKSTARTS:
            qs = QUICKSTARTS[sel]
            st.divider()
            traits_preview = []
            if qs.get("mortal_trait"):
                t = qs["mortal_trait"]
                traits_preview.append(f"{t['name']} ({t['cost']:+d}) [mortal]")
            if qs.get("vampire_trait"):
                t = qs["vampire_trait"]
                lbl = t["name"] + (f" — {t['detail']}" if t.get("detail") else "")
                traits_preview.append(f"{lbl} ({t['cost']:+d}) [vampire]")
            disc_levels = qs.get("discipline_levels", {})
            disc_preview = ", ".join(
                f"{d} {'●' * disc_levels.get(d, 1)}" for d in qs["disciplines"]
            )
            skills_preview = ", ".join(
                f"{s} {'●' * d}" for s, d in qs["skill_dots"].items()
            )
            disc_powers = qs.get("discipline_powers", {})
            powers_preview = " &nbsp;·&nbsp; ".join(
                f"<em>{d}:</em> {', '.join(ps)}" for d, ps in disc_powers.items()
            )
            st.markdown(
                f"<div style='background:#1a0812;border:1px solid #5c1a28;border-radius:4px;"
                f"padding:0.9rem 1.2rem;margin:0.4rem 0;line-height:1.7'>"
                f"<b style='color:#c41e3a;font-size:1.1rem'>{qs['label']}</b>"
                f"<span style='color:#9a8f82;font-size:0.9rem'> — {qs['name']}, {qs['clan']}, Chicago 1999</span><br>"
                f"<span style='color:#9a8f82;font-style:italic;font-size:0.92rem'>{qs['tagline']}</span><br>"
                f"<span style='color:#c9bdb0;font-size:0.88rem'>{qs.get('backstory', '')}</span><br><br>"
                f"<b>Disciplines:</b> {disc_preview}<br>"
                f"<span style='font-size:0.85rem;color:#9a8f82'>{powers_preview}</span><br>"
                f"<b>Trait:</b> {' / '.join(traits_preview) or '—'}<br>"
                f"<b>Skills:</b> <span style='font-size:0.85rem'>{skills_preview}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            already_applied = char.get("clan") == qs["clan"]
            if already_applied:
                st.success(f"{qs['label']} already applied.")
            if st.button(
                "Apply" if not already_applied else "Re-apply",
                key="qs_apply",
                type="primary",
                disabled=already_applied,
            ):
                _apply_quickstart(char, sel)
                st.rerun()

    st.divider()


def render_wizard(char: dict) -> None:
    stage = char["wizard_stage"]

    # Stage navigator
    _render_stage_nav(char, stage)
    st.divider()

    if stage == 1:
        _stage_origins(char)
    elif stage == 2:
        _stage_skills(char)
    elif stage == 3:
        _stage_disciplines(char)
    elif stage == 4:
        _stage_clan(char)


# ── Stage navigation ──────────────────────────────────────────────────────────

def _render_stage_nav(char: dict, current: int) -> None:
    cols = st.columns(4)
    for i, (num, label) in enumerate(STAGES.items()):
        with cols[i]:
            if num == current:
                st.markdown(
                    f"<div style='text-align:center;background:#4a1520;padding:0.4rem;border-radius:3px;"
                    f"border:1px solid #c41e3a;font-family:Cinzel,serif;font-size:0.8rem'>"
                    f"● {num}. {label}</div>",
                    unsafe_allow_html=True,
                )
            elif num < current:
                if st.button(f"✓ {num}. {label}", key=f"nav_stage_{num}", use_container_width=True):
                    char["wizard_stage"] = num
                    st.rerun()
            else:
                st.markdown(
                    f"<div style='text-align:center;padding:0.4rem;color:#5c4050;"
                    f"font-size:0.8rem'>○ {num}. {label}</div>",
                    unsafe_allow_html=True,
                )


def _nav_buttons(char: dict, stage: int, next_disabled: bool = False) -> None:
    col_back, col_space, col_next = st.columns([2, 4, 2])
    with col_back:
        if stage > 1:
            if st.button("← Back", key=f"back_{stage}"):
                char["wizard_stage"] = stage - 1
                st.rerun()
    with col_next:
        label = "Continue →" if stage < 4 else "Complete Character ✓"
        if st.button(label, key=f"next_{stage}", type="primary", disabled=next_disabled):
            if stage < 4:
                char["wizard_stage"] = stage + 1
            else:
                char["wizard_complete"] = True
                char["wizard_stage"] = 4
            st.rerun()


# ── Trait grid ────────────────────────────────────────────────────────────────

MORTAL_CATEGORIES = [
    ("personality", "🎭 Personality"),
    ("mental",      "🧠 Mental"),
    ("body",        "💪 Body"),
    ("sensory",     "👁 Sensory"),
]

_MEMORIES_PLACEHOLDER = (
    "Where were you born, and in what era? What did you do for a living?\n"
    "What shaped you — events, losses, turning points? What did you believe in?\n"
    "Who matters to you?\n\n"
    "Who was your Sire, and when and how did they Embrace you?\n"
    "Were you recruited, seduced, or taken by surprise?\n"
    "What were you told — and what weren't you told?"
)


def _cost_badge(cost) -> str:
    if cost is None:
        return "<span style='background:#2a2010;color:#9a8060;padding:0.1rem 0.4rem;border-radius:2px;font-size:0.75rem'>variable</span>"
    sign = "+" if cost >= 0 else ""
    if cost > 0:
        bg, fg = "#0a2010", "#4a9a6a"
    elif cost < 0:
        bg, fg = "#2a0a10", "#c41e3a"
    else:
        bg, fg = "#1a1a24", "#9a8f82"
    return (
        f"<span style='background:{bg};color:{fg};padding:0.1rem 0.4rem;"
        f"border-radius:2px;font-size:0.75rem;font-weight:bold'>{sign}{cost}</span>"
    )


def _render_trait_card(char: dict, trait_list_key: str, trait_def: dict, form_key: str) -> None:
    key = trait_def["key"]
    name = trait_def["name"]
    desc = trait_def.get("description", "")
    cost = trait_def.get("cost")
    variable = trait_def.get("variable_cost", False)
    requires_detail = trait_def.get("requires_detail", False)
    requires_sub = trait_def.get("requires_sub_choice", False)
    max_times = trait_def.get("max_times", 1)
    is_simple = not variable and not requires_detail and not requires_sub

    selected_list = char[trait_list_key]
    times_taken = sum(1 for t in selected_list if t["key"] == key)
    is_selected = times_taken > 0
    can_add_more = times_taken < max_times and get_trait_count(char) < MAX_TRAITS

    expand_key = f"expand_{form_key}_{key}"
    is_expanded = st.session_state.get(expand_key, False)

    if is_expanded:
        border = "#7a5a20"
    elif is_selected:
        border = "#5a2a2a" if (cost or 0) < 0 else "#2a5a2a"
    else:
        border = "#2a1a24"

    name_color = "#c9bdb0" if not is_selected else ("#cf8a8a" if (cost or 0) < 0 else "#8acf8a")
    badge = _cost_badge(cost)

    st.markdown(
        f"<div style='background:#120810;border:1px solid {border};border-radius:4px;"
        f"padding:0.6rem 0.8rem;margin-bottom:0.25rem'>"
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:0.4rem'>"
        f"<b style='color:{name_color};font-size:0.88rem'>{name}</b>{badge}</div>"
        f"<div style='font-size:0.77rem;color:#8a7f78;margin-top:0.2rem;line-height:1.35'>{desc}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if is_expanded:
        chosen_cost = cost
        if variable:
            opt_labels = [f"{c:+d} — {d}" for c, d in trait_def["cost_options"]]
            chosen_label = st.selectbox("Severity", opt_labels, key=f"{expand_key}_cost", label_visibility="collapsed")
            chosen_cost = trait_def["cost_options"][opt_labels.index(chosen_label)][0]

        sub_choice = None
        if requires_sub:
            sub_choice = st.selectbox("Choose option", trait_def["sub_options"], key=f"{expand_key}_sub", label_visibility="collapsed")

        detail = ""
        if requires_detail:
            detail = st.text_input(
                trait_def.get("detail_prompt", "Detail"),
                key=f"{expand_key}_detail",
                placeholder=trait_def.get("detail_prompt", ""),
                label_visibility="collapsed",
            )

        ready = not (requires_detail and not detail.strip())
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✓ Confirm", key=f"{expand_key}_confirm", type="primary", disabled=not ready, use_container_width=True):
                selected_list.append({
                    "key": key, "name": name, "cost": chosen_cost,
                    "detail": detail.strip() or None, "sub_choice": sub_choice,
                })
                st.session_state.pop(expand_key, None)
                st.rerun()
        with c2:
            if st.button("Cancel", key=f"{expand_key}_cancel", use_container_width=True):
                st.session_state.pop(expand_key, None)
                st.rerun()
    else:
        c1, c2 = st.columns(2)
        with c1:
            if can_add_more:
                label = "+ Add" if times_taken == 0 else f"+ Again ({times_taken}/{max_times})"
                if st.button(label, key=f"add_{form_key}_{key}", use_container_width=True):
                    if is_simple:
                        selected_list.append({"key": key, "name": name, "cost": cost, "detail": None, "sub_choice": None})
                        st.rerun()
                    else:
                        st.session_state[expand_key] = True
                        st.rerun()
        with c2:
            if is_selected:
                if st.button("✕ Remove", key=f"rem_{form_key}_{key}", use_container_width=True):
                    for i, t in enumerate(selected_list):
                        if t["key"] == key:
                            selected_list.pop(i)
                            break
                    st.rerun()


def _render_trait_grid(
    char: dict,
    trait_list_key: str,
    traits_source: list,
    form_key: str,
    categories: list | None = None,
) -> None:
    def _render_group(group: list) -> None:
        cols = st.columns(3)
        for i, trait_def in enumerate(group):
            with cols[i % 3]:
                _render_trait_card(char, trait_list_key, trait_def, form_key)

    if categories:
        for cat_key, cat_label in categories:
            group = [t for t in traits_source if t.get("category") == cat_key]
            if group:
                st.markdown(f"**{cat_label}**")
                _render_group(group)
                st.markdown("")
    else:
        _render_group(traits_source)

    # Custom trait expander
    with st.expander("✏️ Add a Custom Trait"):
        col_name, col_cost = st.columns([3, 1])
        with col_name:
            custom_name = st.text_input("Trait name", key=f"{form_key}_custom_name",
                                        placeholder="e.g., Notorious Criminal")
        with col_cost:
            custom_cost = st.number_input("Cost", min_value=-5, max_value=5, value=-1,
                                          key=f"{form_key}_custom_cost")
        custom_detail = st.text_input("Detail (optional)", key=f"{form_key}_custom_detail",
                                      placeholder="Any clarifying notes")
        custom_warnings = []
        if get_trait_count(char) >= MAX_TRAITS:
            custom_warnings.append(f"Maximum {MAX_TRAITS} traits reached.")
        if not custom_name.strip():
            custom_warnings.append("Enter a trait name.")
        for w in custom_warnings:
            st.warning(w)
        if st.button("Add Custom Trait", key=f"{form_key}_custom_add", disabled=bool(custom_warnings)):
            char[trait_list_key].append({
                "key": f"custom_{custom_name.strip().lower().replace(' ', '_')}",
                "name": custom_name.strip(),
                "cost": int(custom_cost),
                "detail": custom_detail.strip() or None,
                "sub_choice": None,
                "custom": True,
            })
            st.rerun()


# ── Stage 1: Origins & Traits ─────────────────────────────────────────────────

def _stage_origins(char: dict) -> None:
    section_header("Stage 1 — Origins & Traits")
    info_box("All fields are optional — fill in what inspires you. Everything can be edited later.")
    _render_quickstart_panel(char)

    col1, col2 = st.columns([2, 1])
    with col1:
        char["name"] = st.text_input("Name", value=char.get("name", ""), placeholder="Character name", key="s1_name")
    with col2:
        char["tagline"] = st.text_input("Tagline", value=char.get("tagline", ""), placeholder="e.g. Former NSA analyst", key="s1_tagline")

    char["memories"] = st.text_area(
        "Memories",
        value=char.get("memories", ""),
        placeholder=_MEMORIES_PLACEHOLDER,
        height=180,
        key="s1_memories",
    )

    st.divider()

    # Trait budget summary
    total_cost = get_total_trait_cost(char)
    count = get_trait_count(char)
    over_budget = total_cost > MAX_TRAIT_COST
    sign = "+" if total_cost >= 0 else ""
    budget_color = "#c41e3a" if over_budget else "#4a9a6a" if total_cost <= 0 else "#c9bdb0"
    st.markdown(
        f"<span style='font-size:0.95rem'>Trait cost: "
        f"<b style='color:{budget_color}'>{sign}{total_cost} / +{MAX_TRAIT_COST}</b>"
        f" &nbsp;·&nbsp; {count} / {MAX_TRAITS} traits</span>",
        unsafe_allow_html=True,
    )
    if over_budget:
        st.error(f"Combined cost exceeds +{MAX_TRAIT_COST}. Add negative vampire traits or remove positive mortal traits to continue.")

    tab_mortal, tab_vampire = st.tabs(["Mortal Traits", "Vampire Traits"])

    with tab_mortal:
        _render_trait_grid(char, "mortal_traits", MORTAL_TRAITS, "m1", MORTAL_CATEGORIES)

    with tab_vampire:
        _render_trait_grid(char, "vampire_traits", VAMPIRE_TRAITS, "v1")

    st.divider()
    _nav_buttons(char, 1, next_disabled=over_budget)


# ── Stage 2: Skills ───────────────────────────────────────────────────────────

def _stage_skills(char: dict) -> None:
    section_header("Stage 2 — Skills")

    skill_xp_spent = total_skill_xp(char["skill_dots"], char["custom_skills"])
    remaining = CREATION_SKILL_XP - skill_xp_spent
    st.markdown(
        f"**Creation XP:** {skill_xp_spent} / {CREATION_SKILL_XP} spent &nbsp; "
        f"({'**' + str(remaining) + ' remaining**' if remaining > 0 else '✓ budget used'})"
    )
    if remaining < 0:
        st.error(f"Over budget by {-remaining} XP! Remove some dots.")

    st.divider()

    tree_names = list(SKILL_TREES.keys()) + ["Custom"]
    tabs = st.tabs(tree_names)

    for i, tree_name in enumerate(SKILL_TREES.keys()):
        with tabs[i]:
            _render_skill_tree(char, tree_name, budget_remaining=remaining)

    with tabs[-1]:
        _render_custom_skills(char, budget_remaining=remaining)

    st.divider()
    _nav_buttons(char, 2)


def _render_skill_tree(char: dict, tree_name: str, budget_remaining: int) -> None:
    own = char["skill_dots"]
    skills = SKILL_TREES[tree_name]

    for skill_name, skill in skills.items():
        d = own.get(skill_name, 0)
        eff = get_effective_level(skill_name, tree_name, own)
        xp_next = xp_cost_for_next_dot(skill_name, tree_name, own)

        can_add = can_add_dot(skill_name, tree_name, own) and xp_next <= budget_remaining + d
        # budget check: spending xp_next requires enough remaining (d already counted)
        can_add = can_add_dot(skill_name, tree_name, own) and budget_remaining >= xp_next
        can_rem = can_remove_dot(skill_name, tree_name, own)

        branch = skill.get("branches_from")
        depth = 0
        if branch:
            if isinstance(branch, list):
                depth = 1
            else:
                depth = 1
                # Extra depth for skills branching from branching skills
                parent_name, _ = branch
                parent_skill = skills.get(parent_name, {})
                if parent_skill.get("branches_from") is not None:
                    depth = 2

        add_key = f"add_{tree_name}_{skill_name}"
        rem_key = f"rem_{tree_name}_{skill_name}"

        dot_str = dots(d, skill["max_dots"])
        indent = "　" * depth

        b_info = ""
        if branch:
            if isinstance(branch, list):
                parts = " *or* ".join(f"{p} {t}●" for p, t in branch)
                b_info = f" <small style='color:#9a8f82'>← {parts}</small>"
            else:
                p, t = branch
                b_info = f" <small style='color:#9a8f82'>← {p} {t}●</small>"

        unlocked = can_add_dot(skill_name, tree_name, own) or d > 0
        lock_icon = "" if unlocked else "🔒 "

        col1, col2, col3 = st.columns([5, 3, 2])
        with col1:
            st.markdown(
                f"{indent}{lock_icon}**{skill_name}**{b_info}",
                unsafe_allow_html=True,
            )
            st.caption(f"{skill['description']}")
        with col2:
            base = get_static_base(skill_name, tree_name)
            if base > 0:
                achieved = get_achieved_base(skill_name, tree_name, own)
                base_str = "●" * achieved + "○" * (base - achieved)
                level_str = f"{base_str} + {dot_str}  `/{skill['max_dots']}`"
            else:
                level_str = f"{dot_str}  `/{skill['max_dots']}`"
            st.markdown(level_str)
            if can_add:
                st.caption(f"Next: {xp_next} XP")
        with col3:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("−", key=rem_key, disabled=not can_rem):
                    refund = get_static_base(skill_name, tree_name) + d
                    own[skill_name] = d - 1
                    log_xp_refund(char, f"{skill_name} −1 dot", refund, cancel_description=f"{skill_name} +1 dot")
                    st.rerun()
            with c2:
                if st.button("+", key=add_key, disabled=not can_add):
                    own[skill_name] = d + 1
                    log_xp_spend(char, f"{skill_name} +1 dot", xp_next)
                    st.rerun()

        st.markdown("---" if depth == 0 else "")


def _render_custom_skills(char: dict, budget_remaining: int) -> None:
    section_header("Custom Skills")
    info_box("Add custom skills like Dance, Chess, Agriculture — standalone skills with no branching.")

    own = char["skill_dots"]
    custom_skills = char["custom_skills"]

    for i, cs in enumerate(custom_skills):
        cname = cs["name"]
        d = own.get(cname, 0)
        max_d = cs["max_dots"]
        xp_next = d + 1  # no base, cost = own + 1
        can_add = d < max_d and budget_remaining >= xp_next
        can_rem = d > 0

        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            st.markdown(f"**{cname}**")
        with col2:
            st.markdown(f"{dots(d, max_d)} `/{max_d}`")
        with col3:
            if st.button("−", key=f"rem_custom_{i}", disabled=not can_rem):
                own[cname] = d - 1
                log_xp_refund(char, f"{cname} −1 dot", d, cancel_description=f"{cname} +1 dot")
                st.rerun()
            if st.button("+", key=f"add_custom_{i}", disabled=not can_add):
                own[cname] = d + 1
                log_xp_spend(char, f"{cname} +1 dot", xp_next)
                st.rerun()
        with col4:
            if st.button("✕", key=f"del_custom_{i}"):
                own.pop(cname, None)
                custom_skills.pop(i)
                st.rerun()

    st.divider()
    st.markdown("**Add a Custom Skill**")
    col_name, col_max, col_add = st.columns([3, 2, 2])
    with col_name:
        new_name = st.text_input("Skill name", key="custom_skill_name", label_visibility="collapsed", placeholder="e.g. Chess")
    with col_max:
        new_max = st.number_input("Max dots", min_value=1, max_value=7, value=5, key="custom_skill_max", label_visibility="collapsed")
    with col_add:
        if st.button("Add Custom Skill", key="add_custom_skill_btn"):
            if new_name.strip():
                existing_names = [cs["name"] for cs in custom_skills] + list(SKILL_TREES.get("Custom", {}).keys())
                if new_name.strip() not in existing_names:
                    custom_skills.append({"name": new_name.strip(), "max_dots": int(new_max)})
                    st.rerun()
                else:
                    st.error(f"Skill '{new_name}' already exists.")


# ── Stage 4: Disciplines ──────────────────────────────────────────────────────

def _stage_disciplines(char: dict) -> None:
    section_header("Stage 3 — Disciplines")

    unlocked = char["unlocked_disciplines"]

    if len(unlocked) < MAX_DISCIPLINES:
        _select_disciplines(char)
    else:
        _spend_disc_xp(char)

    st.divider()
    _nav_buttons(char, 3)


def _select_disciplines(char: dict) -> None:
    unlocked = char["unlocked_disciplines"]
    remaining_slots = MAX_DISCIPLINES - len(unlocked)

    st.markdown(
        f"Choose **{MAX_DISCIPLINES} Disciplines** to unlock. "
        f"Currently selected: **{len(unlocked)} / {MAX_DISCIPLINES}**"
    )
    if unlocked:
        st.markdown("**Selected:** " + ", ".join(f"`{d}`" for d in unlocked))

    st.divider()
    cols = st.columns(3)
    for i, disc_name in enumerate(ALL_DISCIPLINE_NAMES):
        with cols[i % 3]:
            already = disc_name in unlocked
            img = DISCIPLINES[disc_name]["image"]
            if not img.startswith("http"):
                try:
                    st.image(img, width=48)
                except Exception:
                    pass
            else:
                st.image(img, width=48)

            desc = DISC_SHORT_DESC.get(disc_name, "")
            if already:
                if st.button(f"✓ {disc_name}", key=f"unsel_disc_{disc_name}", type="secondary", help=desc):
                    unlocked.remove(disc_name)
                    char["discipline_levels"].pop(disc_name, None)
                    char["discipline_powers"].pop(disc_name, None)
                    char["xp_log"] = [
                        e for e in char.get("xp_log", [])
                        if not e["description"].startswith(f"{disc_name} level ")
                    ]
                    st.rerun()
            else:
                disabled = remaining_slots == 0
                if st.button(disc_name, key=f"sel_disc_{disc_name}", disabled=disabled, help=desc):
                    unlocked.append(disc_name)
                    char["discipline_levels"][disc_name] = 0
                    char["discipline_powers"][disc_name] = []
                    st.rerun()


def _spend_disc_xp(char: dict) -> None:
    disc_spent = total_disc_xp(char["discipline_levels"])
    remaining = CREATION_DISC_XP - disc_spent

    st.markdown(
        f"**Creation XP:** {disc_spent} / {CREATION_DISC_XP} spent &nbsp; "
        f"({'**' + str(remaining) + ' remaining**' if remaining > 0 else '✓ budget used'})"
    )
    if remaining < 0:
        st.error(f"Over budget by {-remaining} XP!")

    if st.button("← Change Discipline Selection", key="change_disc_sel"):
        disc_names = list(char.get("unlocked_disciplines", []))
        char["xp_log"] = [
            e for e in char.get("xp_log", [])
            if not any(e["description"].startswith(f"{d} level ") for d in disc_names)
        ]
        char["unlocked_disciplines"] = []
        char["discipline_levels"] = {}
        char["discipline_powers"] = {}
        st.rerun()

    st.divider()

    for disc_name in char["unlocked_disciplines"]:
        _render_discipline_editor(char, disc_name, remaining)
        st.divider()


def _render_discipline_editor(char: dict, disc_name: str, budget_remaining: int) -> None:
    disc = DISCIPLINES[disc_name]
    level = char["discipline_levels"].get(disc_name, 0)
    powers = char["discipline_powers"].setdefault(disc_name, [])

    col_img, col_info = st.columns([1, 5])
    with col_img:
        img = disc["image"]
        if not img.startswith("http"):
            try:
                st.image(img, width=60)
            except Exception:
                pass
        else:
            st.image(img, width=60)
    with col_info:
        st.markdown(f"### {disc_name}")
        xp_up = xp_cost_for_disc_level(level)
        can_up = level < 5 and budget_remaining >= xp_up

        col_dots_d, col_minus_d, col_plus_d = st.columns([4, 1, 1])
        with col_dots_d:
            st.markdown(f"Level: {level} / 5 &nbsp; {dots(level, 5)}")
        with col_minus_d:
            if st.button("−", key=f"disc_minus_{disc_name}", disabled=level == 0):
                if powers:
                    powers.pop()
                refund = level
                char["discipline_levels"][disc_name] = level - 1
                log_xp_refund(char, f"{disc_name} level {level} → {level-1}", refund, cancel_description=f"{disc_name} level {level-1} → {level}")
                st.rerun()
        with col_plus_d:
            if st.button("+", key=f"disc_plus_{disc_name}", disabled=not can_up):
                new_level = level + 1
                char["discipline_levels"][disc_name] = new_level
                log_xp_spend(char, f"{disc_name} level {level} → {new_level}", xp_up)
                # Automatically pick the first available power if only one choice
                available = get_available_powers(disc_name, new_level, powers)
                if len(available) == 1:
                    powers.append(available[0]["name"])
                st.rerun()

    if level > 0:
        st.markdown(f"**Acquired powers ({len(powers)} / {level}):**")
        _power_selector(disc_name, disc, level, powers)


def _power_selector(disc_name: str, disc: dict, level: int, powers: list[str]) -> None:
    """Show all powers of a discipline; allow acquiring / releasing."""
    powers_by_level: dict[int, list] = {}
    for p in disc["powers"]:
        powers_by_level.setdefault(p["level"], []).append(p)

    slots_used = len(powers)
    slots_total = level

    for lvl in sorted(powers_by_level):
        if lvl > level:
            continue
        st.markdown(f"<small style='color:#9a8f82'>Level {lvl} powers:</small>", unsafe_allow_html=True)
        for power in powers_by_level[lvl]:
            acquired = power["name"] in powers
            req = power["requires"]
            req_met = req is None or req in powers
            can_acquire = (
                not acquired
                and req_met
                and slots_used < slots_total
            )
            dependents = [p2 for p2 in disc["powers"] if p2.get("requires") == power["name"] and p2["name"] in powers]
            can_release = acquired and not dependents

            col_chk, col_p = st.columns([1, 7])
            with col_chk:
                if acquired:
                    if st.button("■", key=f"release_{disc_name}_{power['name']}", disabled=not can_release):
                        powers.remove(power["name"])
                        st.rerun()
                else:
                    if st.button("□", key=f"acquire_{disc_name}_{power['name']}", disabled=not can_acquire):
                        powers.append(power["name"])
                        st.rerun()
            with col_p:
                req_note = f" *(requires {req})*" if req and not req_met else ""
                st.markdown(
                    f"**{power['name']}**{req_note}  \n"
                    f"<small style='color:#9a8f82'>{power['description']}</small>",
                    unsafe_allow_html=True,
                )


# ── Stage 5: Clan ─────────────────────────────────────────────────────────────

def _stage_clan(char: dict) -> None:
    section_header("Stage 4 — Clan")
    info_box(
        "Clans are optional. Check if you meet a Clan's requirements. "
        "You can qualify for at most one Clan. Your Traits and Disciplines determine eligibility."
    )

    eligible = get_eligible_clans(char)
    current_clan = char.get("clan")

    if not eligible:
        st.warning("Your current Traits and Disciplines don't qualify you for any Clan. You may continue without one, or go back and adjust your choices.")

    if current_clan:
        st.success(f"**Clan:** {current_clan}")
        if st.button("Leave Clan", key="leave_clan"):
            char["clan"] = None
            st.rerun()

    st.divider()

    for clan_name, clan in CLANS.items():
        is_eligible = clan_name in eligible
        is_joined = clan_name == current_clan

        with st.expander(
            f"{'✓ ' if is_joined else ('🩸 ' if is_eligible else '🔒 ')}{clan_name}",
            expanded=is_joined,
        ):
            col_img, col_info = st.columns([1, 4])
            with col_img:
                try:
                    st.image(clan["image"], width=80)
                except Exception:
                    pass
            with col_info:
                st.markdown(f"*{clan['description']}*")
                st.markdown(f"**Recruitment:** {clan['recruitment']}")
                st.markdown(f"**Bonus:** {clan['bonus']}")
                st.markdown(f"**Suggested Disciplines:** {', '.join(clan['suggested_disciplines'])}")

            # Requirements
            reqs = clan["requirements"]
            st.markdown("**Requirements:**")
            if reqs.get("trait_any_malkavian"):
                st.markdown("- Must have at least one mental illness trait (Paranoid, Dissociative Episodes, Depressive Episodes, Manic Episodes, Psychotic Episodes, Panic Disorder, Post-Traumatic Stress, Delusional Belief, Selective Mutism)")
            if "trait_any" in reqs:
                st.markdown(f"- Must have one of these traits: {', '.join(reqs['trait_any'])}")
            if "discipline_all" in reqs:
                st.markdown(f"- Must have unlocked: {', '.join(reqs['discipline_all'])}")
            if "discipline_any" in reqs:
                st.markdown(f"- Must have unlocked one of: {', '.join(reqs['discipline_any'])}")

            if is_eligible and not is_joined:
                if st.button(f"Join {clan_name}", key=f"join_{clan_name}", type="primary"):
                    char["clan"] = clan_name
                    st.rerun()
            elif not is_eligible:
                st.error("Requirements not met.")

    st.divider()

    if char["wizard_complete"]:
        st.success("Character creation complete! Head to the Character Sheet.")
    else:
        col_back, _, col_finish = st.columns([2, 4, 2])
        with col_back:
            if st.button("← Back", key="back_4"):
                char["wizard_stage"] = 3
                st.rerun()
        with col_finish:
            if st.button("Complete Character ✓", key="finish_wizard", type="primary"):
                char["wizard_complete"] = True
                st.success("Character complete! Navigate to the Character Sheet.")
                st.rerun()
