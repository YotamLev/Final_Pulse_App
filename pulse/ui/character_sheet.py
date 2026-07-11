"""Interactive Character Sheet for Final Pulse 2E."""

from __future__ import annotations

import json

import streamlit as st

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
    total_disc_xp,
    xp_cost_for_disc_level,
    get_available_powers,
)
from pulse.data.clans import CLANS
from pulse.models.character import (
    CREATION_SKILL_XP,
    CREATION_DISC_XP,
    BASE_HP,
    BASE_WILLPOWER,
    BASE_BLOOD,
    get_hp_max,
    get_total_trait_cost,
    get_earned_xp_available,
    can_spend_skill_xp,
    can_spend_disc_xp,
    log_xp_spend,
    log_xp_refund,
    normalize_character,
    char_to_dict,
    char_from_dict,
)
from pulse.ui.components import dots, section_header, info_box, render_trait_pill, load_image, sync_text_field


# ── Main entry ────────────────────────────────────────────────────────────────

def render_character_sheet(char: dict) -> None:
    normalize_character(char)

    if not char.get("wizard_complete") and not char.get("name"):
        st.info("Complete the Character Creator to populate the sheet, or upload a saved character below.")

    _render_hero(char)
    st.divider()

    tab_summary, tab_bg, tab_traits, tab_skills, tab_disc, tab_xp, tab_notes, tab_export = st.tabs(
        ["📋 Summary", "📖 Background", "🩸 Traits", "⚔ Skills", "🌑 Disciplines", "⚡ XP", "📝 Notes", "💾 Export"]
    )

    with tab_summary:
        _tab_summary(char)
    with tab_bg:
        _tab_background(char)
    with tab_traits:
        _tab_traits(char)
    with tab_skills:
        _tab_skills(char)
    with tab_disc:
        _tab_disciplines(char)
    with tab_xp:
        _tab_xp(char)
    with tab_notes:
        _tab_notes(char)
    with tab_export:
        _tab_export(char)


# ── Hero header ───────────────────────────────────────────────────────────────

def _render_hero(char: dict) -> None:
    name = char.get("name") or "Unnamed Vampire"
    clan = char.get("clan") or "Clanless"
    tagline = char.get("tagline") or ""
    hp_max = get_hp_max(char)
    hp_cur = char.get("hp_current", BASE_HP)
    wp_cur = char.get("willpower_current", BASE_WILLPOWER)
    bl_cur = char.get("blood_current", BASE_BLOOD)

    blood_neg = f"  <span style='color:#c41e3a'>(Blood {bl_cur})</span>" if bl_cur < 0 else ""
    st.markdown(
        f"<div style='background:linear-gradient(135deg,#0c080e,#1a0812);border:1px solid #5c1a28;"
        f"border-radius:4px;padding:1rem 1.5rem;margin-bottom:0.5rem'>"
        f"<h2 style='color:#c41e3a;font-family:Cinzel,serif;margin:0'>{name}</h2>"
        f"<div style='color:#9a8f82;font-style:italic'>{clan}{' &nbsp;·&nbsp; ' + tagline if tagline else ''}</div>"
        f"<div style='margin-top:0.6rem;font-size:1.2rem;letter-spacing:0.06em'>"
        f"HP {dots(max(0, hp_cur), hp_max)} &nbsp; "
        f"WP {dots(max(0, wp_cur), BASE_WILLPOWER)} &nbsp; "
        f"Blood {dots(max(0, bl_cur), BASE_BLOOD)}{blood_neg}"
        f"</div></div>",
        unsafe_allow_html=True,
    )


# ── Tabs ──────────────────────────────────────────────────────────────────────

def _tab_background(char: dict) -> None:
    section_header("Background & History")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input(
            "Name", value=char.get("name", ""), placeholder="Character name", key="sheet_name",
            on_change=sync_text_field, args=(char, "name", "sheet_name"),
        )
    with col2:
        st.text_input(
            "Tagline", value=char.get("tagline", ""), placeholder="e.g. Former NSA analyst", key="sheet_tagline",
            on_change=sync_text_field, args=(char, "tagline", "sheet_tagline"),
        )

    from pulse.ui.wizard import _MEMORIES_PLACEHOLDER
    st.text_area(
        "Memories",
        value=char.get("memories", ""),
        placeholder=_MEMORIES_PLACEHOLDER,
        height=220,
        key="sheet_memories",
        on_change=sync_text_field, args=(char, "memories", "sheet_memories"),
    )

    # Default vampire powers
    st.divider()
    section_header("Default Vampire Powers")
    powers = [
        ("Blood Surge", "Pay 1 or more Blood, add 1 red die per Blood spent to a roll."),
        ("Blood Heal", "Pay 1 Blood, heal 1 HP. Max once per turn."),
        ("Blush of Life", "Pay 1 Blood, become warm and able to blush for a scene."),
        ("Blood Bond", "Makes mortals Ghouls, makes vampires supernaturally like you."),
        ("The Kiss", "Mortals experience ecstasy when bitten. You can close wounds by licking."),
        ("Willpower Reroll", "Spend 1 Willpower to reroll up to 3 black dice."),
    ]
    for name, desc in powers:
        st.markdown(f"**{name}** — {desc}")

    # Vampire dangers
    st.divider()
    section_header("Dangers")
    st.markdown("- **Sunlight & Fire** cause damage")
    st.markdown("- **Reaching 0 HP** → Torpor (can be days; for ancients — years)")
    st.markdown("- **Wood through heart** → paralyzed")


def _tab_traits(char: dict) -> None:
    section_header("Character Traits")
    total = get_total_trait_cost(char)
    sign = "+" if total >= 0 else ""
    st.markdown(f"**Total trait cost:** {sign}{total} / +2 max")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Mortal Traits**")
        for t in char.get("mortal_traits", []):
            c = t["cost"]
            s = "+" if c >= 0 else ""
            det = t.get("detail") or t.get("sub_choice") or ""
            st.markdown(
                f"<div style='background:#1a1020;padding:0.3rem 0.7rem;border-radius:3px;margin:0.15rem 0'>"
                f"**{t['name']}** ({s}{c}){' — ' + det if det else ''}</div>",
                unsafe_allow_html=True,
            )
        if not char.get("mortal_traits"):
            st.caption("None selected.")

    with col2:
        st.markdown("**Vampire Traits**")
        for t in char.get("vampire_traits", []):
            c = t["cost"]
            s = "+" if c >= 0 else ""
            det = t.get("detail") or t.get("sub_choice") or ""
            st.markdown(
                f"<div style='background:#1a1020;padding:0.3rem 0.7rem;border-radius:3px;margin:0.15rem 0'>"
                f"**{t['name']}** ({s}{c}){' — ' + det if det else ''}</div>",
                unsafe_allow_html=True,
            )
        if not char.get("vampire_traits"):
            st.caption("None selected.")

    st.divider()
    with st.expander("Edit Traits (go back to creator)"):
        st.info("Both mortal and vampire traits are on Stage 1 of the Character Creator.")
        if st.button("→ Stage 1: Origins & Traits"):
            char["wizard_stage"] = 1
            st.session_state.nav = "wizard"
            st.rerun()


def _tab_skills(char: dict) -> None:
    section_header("Skill Trees")

    skill_xp = total_skill_xp(char["skill_dots"], char["custom_skills"])
    earned_avail = get_earned_xp_available(char)
    creation_used = min(skill_xp, CREATION_SKILL_XP)

    st.markdown(
        f"Creation skill XP: **{creation_used} / {CREATION_SKILL_XP}** &nbsp;|&nbsp; "
        f"Earned XP available: **{max(0, earned_avail)}**"
    )

    tree_names = list(SKILL_TREES.keys()) + ["Custom"]
    tabs = st.tabs(tree_names)

    for i, tree_name in enumerate(SKILL_TREES.keys()):
        with tabs[i]:
            _sheet_skill_tree(char, tree_name, earned_avail)

    with tabs[-1]:
        _sheet_custom_skills(char, earned_avail)


def _sheet_skill_tree(char: dict, tree_name: str, earned_avail: int) -> None:
    own = char["skill_dots"]
    skills = SKILL_TREES[tree_name]

    creation_remaining = max(0, CREATION_SKILL_XP - total_skill_xp(own, char["custom_skills"]))
    for skill_name, skill in skills.items():
        d = own.get(skill_name, 0)
        eff = get_effective_level(skill_name, tree_name, own)
        xp_next = xp_cost_for_next_dot(skill_name, tree_name, own)

        can_add = can_add_dot(skill_name, tree_name, own) and xp_next <= creation_remaining + max(0, earned_avail)
        can_rem = can_remove_dot(skill_name, tree_name, own)

        branch = skill.get("branches_from")
        depth = 0
        if branch:
            depth = 1
            if not isinstance(branch, list):
                parent_name, _ = branch
                parent_skill = skills.get(parent_name, {})
                if parent_skill.get("branches_from") is not None:
                    depth = 2

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
            st.markdown(f"{indent}{lock_icon}**{skill_name}**{b_info}", unsafe_allow_html=True)
            st.caption(skill["description"])
        with col2:
            base = get_static_base(skill_name, tree_name)
            own_str = dots(d, skill['max_dots'])
            if base > 0:
                achieved = get_achieved_base(skill_name, tree_name, own)
                base_str = "●" * achieved + "○" * (base - achieved)
                level_str = f"{base_str} + {own_str}  `/{skill['max_dots']}`"
            else:
                level_str = f"{own_str}  `/{skill['max_dots']}`"
            st.markdown(level_str)
            if can_add:
                st.caption(f"Next: {xp_next} XP")
        with col3:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("−", key=f"sheet_rem_{tree_name}_{skill_name}", disabled=not can_rem):
                    refund = get_static_base(skill_name, tree_name) + d
                    own[skill_name] = d - 1
                    log_xp_refund(char, f"{skill_name} −1 dot", refund, skill=skill_name)
                    st.rerun()
            with c2:
                if st.button("+", key=f"sheet_add_{tree_name}_{skill_name}", disabled=not can_add):
                    own[skill_name] = d + 1
                    log_xp_spend(char, f"{skill_name} +1 dot", xp_next, skill=skill_name)
                    st.rerun()


def _sheet_custom_skills(char: dict, earned_avail: int) -> None:
    from pulse.data.skill_trees import SKILL_TREES as _ST
    own = char["skill_dots"]
    custom_skills = char["custom_skills"]

    if not custom_skills:
        st.caption("No custom skills yet.")

    for i, cs in enumerate(custom_skills):
        cname = cs["name"]
        d = own.get(cname, 0)
        max_d = cs["max_dots"]
        xp_next = d + 1
        can_add = d < max_d and can_spend_skill_xp(char, xp_next)
        can_rem = d > 0

        col1, col2, col3, col4 = st.columns([4, 3, 2, 1])
        with col1:
            st.markdown(f"**{cname}**")
            if can_add:
                st.caption(f"Next: {xp_next} XP")
        with col2:
            st.markdown(f"{dots(d, max_d)} `/{max_d}`")
        with col3:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("−", key=f"sheet_rem_custom_{i}", disabled=not can_rem):
                    log_xp_refund(char, f"{cname} −1 dot", d, skill=cname)
                    own[cname] = d - 1
                    st.rerun()
            with c2:
                if st.button("+", key=f"sheet_add_custom_{i}", disabled=not can_add):
                    log_xp_spend(char, f"{cname} +1 dot", xp_next, skill=cname)
                    own[cname] = d + 1
                    st.rerun()
        with col4:
            if st.button("✕", key=f"sheet_del_custom_{i}"):
                own.pop(cname, None)
                custom_skills.pop(i)
                st.rerun()

    st.divider()
    st.markdown("**Add a Custom Skill**")
    with st.form(key="sheet_custom_skill_form", clear_on_submit=True):
        col_name, col_max, col_add = st.columns([3, 2, 2])
        with col_name:
            new_name = st.text_input("Name", key="sheet_custom_skill_name",
                                     label_visibility="collapsed", placeholder="e.g. Chess")
        with col_max:
            new_max = st.number_input("Max dots", min_value=1, max_value=7, value=5,
                                      key="sheet_custom_skill_max", label_visibility="collapsed")
        with col_add:
            submitted = st.form_submit_button("Add Skill")

    if submitted:
        name = new_name.strip()
        existing = [cs["name"] for cs in custom_skills] + [s for t in _ST.values() for s in t]
        if not name:
            st.error("Enter a skill name.")
        elif name in existing:
            st.error(f"'{name}' already exists.")
        else:
            custom_skills.append({"name": name, "max_dots": int(new_max)})
            st.rerun()


def _tab_disciplines(char: dict) -> None:
    section_header("Disciplines")

    disc_xp = total_disc_xp(char["discipline_levels"])
    earned_avail = get_earned_xp_available(char)

    st.markdown(
        f"Creation disc XP: **{min(disc_xp, CREATION_DISC_XP)} / {CREATION_DISC_XP}** &nbsp;|&nbsp; "
        f"Earned XP available: **{max(0, earned_avail)}**"
    )

    unlocked = char.get("unlocked_disciplines", [])
    if not unlocked:
        st.info("No Disciplines unlocked yet. Complete the Character Creator first.")
        return

    for disc_name in unlocked:
        _sheet_disc_editor(char, disc_name)
        st.divider()


def _sheet_disc_editor(char: dict, disc_name: str) -> None:
    disc = DISCIPLINES[disc_name]
    level = char["discipline_levels"].get(disc_name, 0)
    powers = char["discipline_powers"].setdefault(disc_name, [])
    xp_up = xp_cost_for_disc_level(level)
    can_up = level < 5 and can_spend_disc_xp(char, xp_up)

    col_img, col_info = st.columns([1, 5])
    with col_img:
        img = disc["image"]
        try:
            st.image(load_image(img) if not img.startswith("http") else img, width=60)
        except Exception:
            pass
    with col_info:
        st.markdown(f"### {disc_name}")
        col_d, col_m, col_p = st.columns([4, 1, 1])
        with col_d:
            st.markdown(f"Level: **{level} / 5** &nbsp; {dots(level, 5)}")
            if can_up:
                st.caption(f"Next level: {xp_up} XP")
        with col_m:
            if st.button("−", key=f"sheet_disc_minus_{disc_name}", disabled=level == 0):
                refund = level
                char["discipline_levels"][disc_name] = level - 1
                if powers:
                    powers.pop()
                log_xp_refund(char, f"{disc_name} level {level} → {level - 1}", refund, disc=disc_name, from_level=level - 1, to_level=level)
                st.rerun()
        with col_p:
            if st.button("+", key=f"sheet_disc_plus_{disc_name}", disabled=not can_up):
                new_lv = level + 1
                char["discipline_levels"][disc_name] = new_lv
                log_xp_spend(char, f"{disc_name} level {level} → {new_lv}", xp_up, disc=disc_name, from_level=level, to_level=new_lv)
                available = get_available_powers(disc_name, new_lv, powers)
                if len(available) == 1:
                    powers.append(available[0]["name"])
                st.rerun()

    if level > 0:
        with st.expander(f"Powers ({len(powers)}/{level})", expanded=True):
            _power_selector_sheet(disc_name, disc, level, powers)


def _power_selector_sheet(disc_name: str, disc: dict, level: int, powers: list[str]) -> None:
    powers_by_level: dict[int, list] = {}
    for p in disc["powers"]:
        powers_by_level.setdefault(p["level"], []).append(p)

    for lvl in sorted(powers_by_level):
        if lvl > level:
            continue
        st.markdown(f"<small style='color:#9a8f82'>Level {lvl} powers:</small>", unsafe_allow_html=True)
        for power in powers_by_level[lvl]:
            acquired = power["name"] in powers
            req = power["requires"]
            req_met = req is None or req in powers
            can_acquire = not acquired and req_met and len(powers) < level
            dependents = [p2 for p2 in disc["powers"] if p2.get("requires") == power["name"] and p2["name"] in powers]
            can_release = acquired and not dependents

            col_chk, col_p = st.columns([1, 7])
            with col_chk:
                if acquired:
                    if st.button("■", key=f"sheet_release_{disc_name}_{power['name']}", disabled=not can_release):
                        powers.remove(power["name"])
                        st.rerun()
                else:
                    if st.button("□", key=f"sheet_acquire_{disc_name}_{power['name']}", disabled=not can_acquire):
                        powers.append(power["name"])
                        st.rerun()
            with col_p:
                req_note = f" *(requires {req})*" if req and not req_met else ""
                st.markdown(
                    f"**{power['name']}**{req_note}  \n"
                    f"<small style='color:#9a8f82'>{power['description']}</small>",
                    unsafe_allow_html=True,
                )


def _tab_summary(char: dict) -> None:
    _render_trackers(char)

    st.divider()
    section_header("Traits")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Mortal Traits**")
        for t in char.get("mortal_traits", []):
            c = t["cost"]
            s = "+" if c >= 0 else ""
            det = t.get("detail") or t.get("sub_choice") or ""
            st.markdown(f"**{t['name']}** ({s}{c}){' — ' + det if det else ''}")
        if not char.get("mortal_traits"):
            st.caption("None")
    with col2:
        st.markdown("**Vampire Traits**")
        for t in char.get("vampire_traits", []):
            c = t["cost"]
            s = "+" if c >= 0 else ""
            det = t.get("detail") or t.get("sub_choice") or ""
            st.markdown(f"**{t['name']}** ({s}{c}){' — ' + det if det else ''}")
        if not char.get("vampire_traits"):
            st.caption("None")

    st.divider()
    section_header("Skills")
    own = char.get("skill_dots", {})
    skill_rows = ""
    for tree_name, tree in SKILL_TREES.items():
        for skill_name, skill_data in tree.items():
            d = own.get(skill_name, 0)
            if not d:
                continue
            base = get_static_base(skill_name, tree_name)
            level_str = f"{'●' * base} + {dots(d, skill_data['max_dots'])}" if base > 0 else dots(d, skill_data["max_dots"])
            skill_rows += f"<tr><td style='color:#9a8f82'>{tree_name}</td><td><b>{skill_name}</b></td><td>{level_str}</td></tr>"
    for cs in char.get("custom_skills", []):
        d = own.get(cs["name"], 0)
        if d:
            skill_rows += f"<tr><td style='color:#9a8f82'>Custom</td><td><b>{cs['name']}</b></td><td>{dots(d, cs['max_dots'])}</td></tr>"
    if skill_rows:
        st.markdown(
            "<table style='width:100%;border-collapse:collapse'>"
            "<thead><tr>"
            "<th style='text-align:left;color:#9a8f82;padding:0.25rem 0.5rem'>Tree</th>"
            "<th style='text-align:left;padding:0.25rem 0.5rem'>Skill</th>"
            "<th style='text-align:left;padding:0.25rem 0.5rem'>Level</th>"
            "</tr></thead><tbody>" + skill_rows + "</tbody></table>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No skills invested.")

    st.divider()
    section_header("Disciplines")
    for disc_name in char.get("unlocked_disciplines", []):
        level = char.get("discipline_levels", {}).get(disc_name, 0)
        powers = char.get("discipline_powers", {}).get(disc_name, [])
        st.markdown(f"**{disc_name}** — Level {level} &nbsp; {dots(level, 5)}", unsafe_allow_html=True)
        if powers:
            st.caption(", ".join(powers))
    if not char.get("unlocked_disciplines"):
        st.caption("No disciplines unlocked.")

    if char.get("memories"):
        st.divider()
        section_header("Memories")
        st.markdown(char["memories"])

    if char.get("notes"):
        st.divider()
        section_header("Notes")
        st.markdown(char["notes"])

    st.divider()
    section_header("Experience Points")
    skill_xp = total_skill_xp(char["skill_dots"], char["custom_skills"])
    disc_xp = total_disc_xp(char["discipline_levels"])
    total_xp = CREATION_SKILL_XP + CREATION_DISC_XP + char.get("earned_xp", 0)
    spent_xp = skill_xp + disc_xp
    st.markdown(f"**Total XP:** {total_xp} &nbsp;·&nbsp; **Spent:** {spent_xp} / {total_xp}", unsafe_allow_html=True)
    log = char.get("xp_log", [])
    if log:
        for entry in log:
            cost = entry["cost"]
            desc = entry["description"]
            if cost > 0:
                st.markdown(f"− **{cost} XP** &nbsp; {desc}")
            else:
                st.markdown(f"＋ **{-cost} XP** &nbsp; {desc}")
    else:
        st.caption("No XP activity yet.")


def _render_trackers(char: dict) -> None:
    section_header("Status Trackers")
    hp_max = get_hp_max(char)

    # HP
    st.markdown("### Hit Points")
    hp_cur = max(0, char.get("hp_current", hp_max))
    char["hp_current"] = hp_cur
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"<span style='font-size:1.4rem;letter-spacing:0.06em'>{dots(hp_cur, hp_max)}</span>", unsafe_allow_html=True)
        st.caption(f"{hp_cur} / {hp_max}")
    with col2:
        if st.button("−", key="hp_minus", disabled=hp_cur <= 0):
            char["hp_current"] = hp_cur - 1
            st.rerun()
    with col3:
        if st.button("+", key="hp_plus"):
            char["hp_current"] = min(hp_max, hp_cur + 1)
            st.rerun()

    # Willpower
    st.markdown("### Willpower")
    wp_cur = max(0, char.get("willpower_current", BASE_WILLPOWER))
    char["willpower_current"] = wp_cur
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"<span style='font-size:1.4rem;letter-spacing:0.06em'>{dots(wp_cur, BASE_WILLPOWER)}</span>", unsafe_allow_html=True)
        st.caption(f"{wp_cur} / {BASE_WILLPOWER}")
    with col2:
        if st.button("−", key="wp_minus", disabled=wp_cur <= 0):
            char["willpower_current"] = wp_cur - 1
            st.rerun()
    with col3:
        if st.button("+", key="wp_plus"):
            char["willpower_current"] = min(BASE_WILLPOWER, wp_cur + 1)
            st.rerun()

    # Blood / Hunger
    bl_cur = char.get("blood_current", BASE_BLOOD)
    _HUNGER_RED = "#ff3030"
    in_hunger = bl_cur < 0
    if in_hunger:
        st.markdown(f"<h3 style='color:{_HUNGER_RED}'>Hunger</h3>", unsafe_allow_html=True)
    else:
        st.markdown("### Blood")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        if bl_cur > 0:
            track = dots(bl_cur, BASE_BLOOD)
            st.markdown(f"<span style='font-size:1.4rem;letter-spacing:0.06em'>{track}</span>", unsafe_allow_html=True)
        elif bl_cur == 0:
            st.markdown(f"<span style='font-size:1.4rem;letter-spacing:0.06em'>{'○' * BASE_BLOOD}</span>", unsafe_allow_html=True)
        else:
            empty = "○" * BASE_BLOOD
            st.markdown(
                f"<span style='font-size:1.4rem;letter-spacing:0.06em;color:{_HUNGER_RED}'>"
                f"{empty} +{abs(bl_cur)}</span>",
                unsafe_allow_html=True,
            )
        cap_style = f"color:{_HUNGER_RED}" if in_hunger else ""
        st.markdown(f"<span style='font-size:0.8rem;{cap_style}'>{bl_cur} / {BASE_BLOOD}</span>", unsafe_allow_html=True)
        if bl_cur <= -4:
            st.warning("Stigmata threshold reached (if that trait is active).")
    with col2:
        if st.button("−", key="bl_minus"):
            char["blood_current"] = bl_cur - 1
            st.rerun()
    with col3:
        if st.button("+", key="bl_plus"):
            char["blood_current"] = min(BASE_BLOOD, bl_cur + 1)
            st.rerun()

    st.divider()
    if st.button("Full Restore (HP + WP + Blood to max)", key="full_restore"):
        char["hp_current"] = hp_max
        char["willpower_current"] = BASE_WILLPOWER
        char["blood_current"] = BASE_BLOOD
        st.rerun()


def _tab_xp(char: dict) -> None:
    section_header("Experience Points")

    skill_xp = total_skill_xp(char["skill_dots"], char["custom_skills"])
    disc_xp = total_disc_xp(char["discipline_levels"])
    earned_avail = get_earned_xp_available(char)

    total_xp = CREATION_SKILL_XP + CREATION_DISC_XP + char.get("earned_xp", 0)
    spent_xp = skill_xp + disc_xp
    over = spent_xp > total_xp

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total XP", total_xp)
    with col2:
        st.metric("Spent XP", f"{spent_xp} / {total_xp}", delta=f"{total_xp - spent_xp} remaining" if not over else f"{spent_xp - total_xp} over budget", delta_color="normal" if not over else "inverse")

    st.caption(
        f"Creation pools: {min(skill_xp, CREATION_SKILL_XP)}/{CREATION_SKILL_XP} skill · "
        f"{min(disc_xp, CREATION_DISC_XP)}/{CREATION_DISC_XP} disc · "
        f"Earned available: {max(0, earned_avail)}"
    )

    st.divider()
    st.markdown("**Storyteller: Award Earned XP**")
    with st.form(key="xp_award_form", clear_on_submit=True):
        col_add, col_note, col_btn = st.columns([2, 3, 2])
        with col_add:
            xp_award = st.number_input("Amount", min_value=1, max_value=100, value=1, key="xp_award_amount", label_visibility="collapsed")
        with col_note:
            xp_note = st.text_input("Reason", key="xp_award_note", placeholder="e.g., Session reward", label_visibility="collapsed")
        with col_btn:
            submitted = st.form_submit_button("Award XP", type="primary")

    if submitted:
        char["earned_xp"] = char.get("earned_xp", 0) + int(xp_award)
        char.setdefault("xp_log", []).append({"description": f"[Award] {xp_note or 'Earned XP'}", "cost": -int(xp_award)})
        st.rerun()

    st.divider()
    section_header("XP Log")
    log = char.get("xp_log", [])
    if not log:
        st.caption("No XP activity yet.")
    else:
        for entry in log:
            cost = entry["cost"]
            desc = entry["description"]
            if cost > 0:
                st.markdown(f"− **{cost} XP** &nbsp; {desc}")
            else:
                st.markdown(f"＋ **{-cost} XP** &nbsp; {desc}")


def _tab_notes(char: dict) -> None:
    section_header("Notes")
    st.text_area(
        "Session notes, observations, contacts…",
        value=char.get("notes", ""),
        height=350,
        key="sheet_notes",
        label_visibility="collapsed",
        on_change=sync_text_field, args=(char, "notes", "sheet_notes"),
    )


def _tab_export(char: dict) -> None:
    section_header("Export & Save")

    slug = (char.get("name") or "character").replace(" ", "_")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Export Character File")
        st.caption("One `.html` file — looks great in a browser and can be loaded back into the app.")
        html = _generate_html(char)
        st.download_button(
            "⬇ Export Character File",
            data=html.encode("utf-8"),
            file_name=f"{slug}.html",
            mime="text/html",
            key="dl_character",
            use_container_width=True,
            type="primary",
        )
    with col2:
        st.markdown("### Load Character")
        st.caption("Upload a previously exported `.html` file.")
        uploaded = st.file_uploader("Upload character file", type=["html", "json"], key="upload_char", label_visibility="collapsed")
        if uploaded is not None:
            try:
                raw = uploaded.read().decode("utf-8")
                if uploaded.name.endswith(".html"):
                    marker = '<script type="application/json" id="fp-character-data">'
                    start = raw.index(marker) + len(marker)
                    end = raw.index("</script>", start)
                    data = json.loads(raw[start:end])
                else:
                    data = json.loads(raw)
                char.update(char_from_dict(data))
                st.success("Character loaded!")
                st.rerun()
            except (ValueError, KeyError) as e:
                st.error(f"Could not read character data: {e}")


# ── HTML export ───────────────────────────────────────────────────────────────

def _generate_html(char: dict) -> str:
    from pulse.models.character import get_hp_max
    from pulse.data.skill_trees import get_effective_level, get_static_base, total_skill_xp
    from pulse.data.disciplines import total_disc_xp
    from pulse.data.traits import MORTAL_TRAITS, VAMPIRE_TRAITS
    from pulse.models.character import CREATION_SKILL_XP, CREATION_DISC_XP, get_earned_xp_available

    name = char.get("name", "Unnamed")
    clan = char.get("clan") or "Clanless"
    tagline = char.get("tagline") or ""
    hp_max = get_hp_max(char)
    hp_cur = char.get("hp_current", hp_max)
    wp_cur = char.get("willpower_current", 10)
    bl_cur = char.get("blood_current", 10)

    _all_traits = {t["key"]: t for t in MORTAL_TRAITS + VAMPIRE_TRAITS}

    def dot_html(current: int, maximum: int) -> str:
        c = max(0, min(current, maximum))
        return "●" * c + "○" * (maximum - c)

    def _trait_li(t: dict) -> str:
        sign = "+" if t["cost"] >= 0 else ""
        extra = t.get("detail") or t.get("sub_choice") or ""
        desc = "" if t.get("custom") else _all_traits.get(t["key"], {}).get("description", "")
        parts = f"<b>{t['name']}</b> ({sign}{t['cost']})"
        if extra:
            parts += f" — {extra}"
        if desc:
            parts += f"<br><small style='color:#9a8f82'>{desc}</small>"
        return f"<li>{parts}</li>"

    # Traits
    mortal_t = "".join(_trait_li(t) for t in char.get("mortal_traits", []))
    vampire_t = "".join(_trait_li(t) for t in char.get("vampire_traits", []))

    # Skills
    skill_rows = ""
    own = char.get("skill_dots", {})
    for tree_name, skills in SKILL_TREES.items():
        for skill_name, skill in skills.items():
            d = own.get(skill_name, 0)
            if d == 0:
                continue
            base = get_static_base(skill_name, tree_name)
            desc = skill.get("description", "")
            skill_cell = f"{skill_name}"
            if desc:
                skill_cell += f"<br><small style='color:#9a8f82'>{desc}</small>"
            own_dots_html = dot_html(d, skill['max_dots'])
            level_cell = f"{'●' * base} + {own_dots_html}" if base > 0 else own_dots_html
            skill_rows += f"<tr><td>{tree_name}</td><td>{skill_cell}</td><td>{level_cell}</td></tr>"
    for cs in char.get("custom_skills", []):
        d = own.get(cs["name"], 0)
        if d > 0:
            skill_rows += f"<tr><td>Custom</td><td>{cs['name']}</td><td>{dot_html(d, cs['max_dots'])}</td></tr>"

    # Disciplines
    _power_lookup = {
        disc_name: {p["name"]: p for p in disc_data["powers"]}
        for disc_name, disc_data in DISCIPLINES.items()
    }
    disc_rows = ""
    for disc_name in char.get("unlocked_disciplines", []):
        level = char.get("discipline_levels", {}).get(disc_name, 0)
        powers_list = char.get("discipline_powers", {}).get(disc_name, [])
        powers_html = ""
        for pname in powers_list:
            pdata = _power_lookup.get(disc_name, {}).get(pname)
            desc = pdata["description"] if pdata else ""
            powers_html += f"<li><b>{pname}</b>"
            if desc:
                powers_html += f"<br><small style='color:#9a8f82'>{desc}</small>"
            powers_html += "</li>"
        disc_rows += (
            f"<tr><td>{disc_name}</td><td>{dot_html(level, 5)} (Level {level})</td>"
            f"<td><ul style='margin:0;padding-left:1.2rem'>{powers_html or '<li>—</li>'}</ul></td></tr>"
        )

    # XP summary
    skill_xp = total_skill_xp(char.get("skill_dots", {}), char.get("custom_skills", []))
    disc_xp  = total_disc_xp(char.get("discipline_levels", {}))
    total_xp = CREATION_SKILL_XP + CREATION_DISC_XP + char.get("earned_xp", 0)
    spent_xp = skill_xp + disc_xp
    xp_log_rows = ""
    for entry in char.get("xp_log", []):
        cost = entry["cost"]
        desc = entry["description"]
        if cost > 0:
            xp_log_rows += f"<tr><td>{desc}</td><td style='color:#c41e3a;text-align:right'>−{cost}</td></tr>"
        else:
            xp_log_rows += f"<tr><td>{desc}</td><td style='color:#4a9a6a;text-align:right'>+{-cost}</td></tr>"

    char_json = json.dumps(char_to_dict(char), ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{name} — Final Pulse Character Sheet</title>
<style>
  body {{ font-family: Georgia, serif; background: #0a080c; color: #e8ddd0; margin: 2rem; }}
  h1 {{ color: #c41e3a; font-family: 'Times New Roman', serif; font-size: 2.2rem; }}
  h2 {{ color: #c41e3a; font-size: 1.3rem; border-bottom: 1px solid #4a2030; padding-bottom: 0.3rem; }}
  h3 {{ color: #d4c8b8; font-size: 1rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
  th, td {{ padding: 0.4rem 0.8rem; border: 1px solid #4a2030; }}
  th {{ background: #1a0a12; color: #c9bdb0; }}
  .tracker {{ font-size: 1.5rem; letter-spacing: 0.1em; }}
  ul {{ margin: 0.3rem 0; padding-left: 1.2rem; }}
  .section {{ background: #12101a; border: 1px solid #3d2830; border-radius: 4px; padding: 1rem; margin-bottom: 1rem; }}
  @media print {{ body {{ background: white; color: black; }} .section {{ border: 1px solid #ccc; }} }}
</style>
</head>
<body>
<h1>{name}</h1>
<p><strong>Clan:</strong> {clan}{(' &nbsp;·&nbsp; ' + tagline) if tagline else ''}</p>

<div class="section">
<h2>Trackers</h2>
<p><strong>HP:</strong> <span class="tracker">{dot_html(max(0,hp_cur), hp_max)}</span> ({max(0,hp_cur)}/{hp_max})</p>
<p><strong>Willpower:</strong> <span class="tracker">{dot_html(max(0,wp_cur), 10)}</span> ({max(0,wp_cur)}/10)</p>
<p><strong>{'Hunger' if bl_cur < 0 else 'Blood'}:</strong> <span class="tracker" {'style="color:#ff3030"' if bl_cur < 0 else ''}>{dot_html(max(0,bl_cur), 10)}{(' +' + str(abs(bl_cur))) if bl_cur < 0 else ''}</span> ({bl_cur}/10)</p>
</div>

<div class="section">
<h2>Traits</h2>
<div style="display:flex;gap:2rem">
<div><h3>Mortal</h3><ul>{mortal_t or '<li>None</li>'}</ul></div>
<div><h3>Vampire</h3><ul>{vampire_t or '<li>None</li>'}</ul></div>
</div>
</div>

<div class="section">
<h2>Skills</h2>
<table><thead><tr><th>Tree</th><th>Skill &amp; Description</th><th>Level</th></tr></thead>
<tbody>{skill_rows or '<tr><td colspan=3>No skills invested</td></tr>'}</tbody></table>
</div>

<div class="section">
<h2>Disciplines</h2>
<table><thead><tr><th>Discipline</th><th>Level</th><th>Powers &amp; Descriptions</th></tr></thead>
<tbody>{disc_rows or '<tr><td colspan=3>No disciplines</td></tr>'}</tbody></table>
</div>

<div class="section">
<h2>Memories</h2>
<p style="white-space:pre-wrap">{char.get('memories', '—')}</p>
</div>

<div class="section">
<h2>Notes</h2>
<p>{char.get('notes', '—')}</p>
</div>

<div class="section">
<h2>Experience Points</h2>
<p><strong>Total XP:</strong> {total_xp} &nbsp;·&nbsp; <strong>Spent:</strong> {spent_xp} / {total_xp}</p>
{"<table><thead><tr><th style='text-align:left'>Description</th><th style='text-align:right'>XP</th></tr></thead><tbody>" + xp_log_rows + "</tbody></table>" if xp_log_rows else "<p style='color:#9a8f82'>No XP activity logged.</p>"}
</div>
<script type="application/json" id="fp-character-data">
{char_json}
</script>
</body>
</html>"""
