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
    xp_cost_for_next_dot,
    total_skill_xp,
)
from pulse.data.disciplines import (
    DISCIPLINES,
    ALL_DISCIPLINE_NAMES,
    MAX_DISCIPLINES,
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
from pulse.ui.components import dots, section_header, info_box, render_trait_pill


# ── Stage labels ──────────────────────────────────────────────────────────────

STAGES = {
    1: "Mortal",
    2: "Vampire",
    3: "Skills",
    4: "Disciplines",
    5: "Clan",
}


def render_wizard(char: dict) -> None:
    stage = char["wizard_stage"]

    # Stage navigator
    _render_stage_nav(char, stage)
    st.divider()

    if stage == 1:
        _stage_mortal(char)
    elif stage == 2:
        _stage_vampire(char)
    elif stage == 3:
        _stage_skills(char)
    elif stage == 4:
        _stage_disciplines(char)
    elif stage == 5:
        _stage_clan(char)


# ── Stage navigation ──────────────────────────────────────────────────────────

def _render_stage_nav(char: dict, current: int) -> None:
    cols = st.columns(5)
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
        label = "Continue →" if stage < 5 else "Complete Character ✓"
        if st.button(label, key=f"next_{stage}", type="primary", disabled=next_disabled):
            if stage < 5:
                char["wizard_stage"] = stage + 1
            else:
                char["wizard_complete"] = True
                char["wizard_stage"] = 5
            st.rerun()


# ── Trait helpers ─────────────────────────────────────────────────────────────

def _trait_form(char: dict, trait_list_key: str, traits_source: list, form_key: str) -> None:
    """Generic add-trait form for mortal or vampire traits."""
    with st.expander("➕ Add a Trait"):
        trait_names = [t["name"] for t in traits_source]
        sel_name = st.selectbox("Select trait", trait_names, key=f"{form_key}_select")
        trait_def = next(t for t in traits_source if t["name"] == sel_name)

        # Cost selection
        chosen_cost = trait_def.get("cost")
        if trait_def.get("variable_cost"):
            opt_labels = [f"{c:+d} — {desc}" for c, desc in trait_def["cost_options"]]
            chosen_label = st.selectbox("Severity / cost", opt_labels, key=f"{form_key}_cost")
            idx = opt_labels.index(chosen_label)
            chosen_cost = trait_def["cost_options"][idx][0]

        # Sub-choice (e.g., Folkloric Bane)
        sub_choice = None
        if trait_def.get("requires_sub_choice"):
            sub_choice = st.selectbox("Choose option", trait_def["sub_options"], key=f"{form_key}_sub")

        # Detail text
        detail = ""
        if trait_def.get("requires_detail"):
            detail = st.text_input(trait_def["detail_prompt"], key=f"{form_key}_detail")

        # Validation
        current_cost = get_total_trait_cost(char)
        current_count = get_trait_count(char)
        new_cost = current_cost + chosen_cost
        times_taken = sum(1 for t in char[trait_list_key] if t["key"] == trait_def["key"])
        max_times = trait_def.get("max_times", 1)

        warnings = []
        if current_count >= MAX_TRAITS:
            warnings.append(f"Already at maximum of {MAX_TRAITS} traits.")
        if times_taken >= max_times:
            warnings.append(f"This trait can only be taken {max_times} time(s).")
        if trait_def.get("requires_detail") and not detail.strip():
            warnings.append("Please fill in the required detail.")

        for w in warnings:
            st.warning(w)

        if st.button("Add Trait", key=f"{form_key}_add", disabled=bool(warnings)):
            char[trait_list_key].append({
                "key": trait_def["key"],
                "name": trait_def["name"],
                "cost": chosen_cost,
                "detail": detail.strip() or None,
                "sub_choice": sub_choice,
            })
            st.rerun()


def _render_trait_list(char: dict, trait_list_key: str, section_label: str) -> None:
    traits = char[trait_list_key]
    if not traits:
        st.caption(f"No {section_label} traits selected.")
        return
    total = sum(t["cost"] for t in traits)
    sign = "+" if total >= 0 else ""
    st.markdown(f"**{section_label} Traits** (total cost: {sign}{total})")
    for i, trait in enumerate(traits):
        render_trait_pill(trait, remove_key=f"remove_{trait_list_key}_{i}")
        if st.session_state.get(f"remove_{trait_list_key}_{i}"):
            traits.pop(i)
            st.rerun()


# ── Stage 1: Mortal ───────────────────────────────────────────────────────────

def _stage_mortal(char: dict) -> None:
    section_header("Stage 1 — Who Were You?")
    info_box(
        "Think about: childhood, adulthood, job, hobbies, life-changing events, "
        "personality, mannerisms, beliefs. All fields are optional — fill in what inspires you."
    )

    col1, col2 = st.columns(2)
    with col1:
        char["name"] = st.text_input("Character Name", value=char["name"], key="s1_name")
        char["birthplace"] = st.text_input("Birth Place", value=char["birthplace"], key="s1_birthplace")
    with col2:
        char["birthtime"] = st.text_input("Birth Time / Era", value=char["birthtime"], key="s1_birthtime")

    char["mortal_history"] = st.text_area(
        "Mortal History (who you were as a mortal)",
        value=char["mortal_history"],
        height=120,
        key="s1_history",
    )
    char["beliefs"] = st.text_area("Beliefs", value=char["beliefs"], height=80, key="s1_beliefs")
    char["connections"] = st.text_area(
        "Important Characters & Connections",
        value=char["connections"],
        height=80,
        key="s1_connections",
    )

    st.divider()
    section_header("Mortal Traits")

    total_cost = get_total_trait_cost(char)
    count = get_trait_count(char)
    sign = "+" if total_cost >= 0 else ""
    st.markdown(
        f"**Current trait cost:** {sign}{total_cost} &nbsp;|&nbsp; "
        f"**Traits:** {count} / {MAX_TRAITS} (recommended ≤ 6)"
    )
    st.caption(f"The combined mortal + vampire cost must be ≤ +{MAX_TRAIT_COST} by the end of Stage 2. You can go higher here and balance it with negative vampire traits.")

    _render_trait_list(char, "mortal_traits", "Mortal")
    st.markdown("")
    _trait_form(char, "mortal_traits", MORTAL_TRAITS, "m1")

    st.divider()
    _nav_buttons(char, 1)


# ── Stage 2: Vampire ──────────────────────────────────────────────────────────

def _stage_vampire(char: dict) -> None:
    section_header("Stage 2 — Your Embrace")
    info_box("Who Embraced You? When and why? Were you recruited to a Clan?")

    col1, col2 = st.columns(2)
    with col1:
        char["sire"] = st.text_input("Sire's Name", value=char["sire"], key="s2_sire")
    with col2:
        char["embrace_time"] = st.text_input(
            "When were you Embraced?", value=char["embrace_time"], key="s2_embrace_time"
        )

    char["embrace_backstory"] = st.text_area(
        "The Embrace Story",
        value=char["embrace_backstory"],
        height=130,
        key="s2_backstory",
    )

    st.divider()
    section_header("Vampire Traits")

    total_cost = get_total_trait_cost(char)
    count = get_trait_count(char)
    sign = "+" if total_cost >= 0 else ""
    over_budget = total_cost > MAX_TRAIT_COST
    st.markdown(
        f"**Combined trait cost (mortal + vampire):** {sign}{total_cost} / +{MAX_TRAIT_COST} max &nbsp;|&nbsp; "
        f"**Traits:** {count} / {MAX_TRAITS}"
    )
    if over_budget:
        st.error(f"Combined cost is {sign}{total_cost} — must be ≤ +{MAX_TRAIT_COST} to continue. Add negative vampire traits or remove positive mortal traits.")

    _render_trait_list(char, "vampire_traits", "Vampire")
    st.markdown("")
    _trait_form(char, "vampire_traits", VAMPIRE_TRAITS, "v2")

    st.divider()
    _nav_buttons(char, 2, next_disabled=over_budget)


# ── Stage 3: Skills ───────────────────────────────────────────────────────────

def _stage_skills(char: dict) -> None:
    section_header("Stage 3 — Skills")

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
    _nav_buttons(char, 3)


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
            eff_label = f"  eff. **{eff}**" if d > 0 else ""
            st.markdown(f"{dot_str} `/{skill['max_dots']}`{eff_label}")
            if can_add:
                st.caption(f"Next: {xp_next} XP")
        with col3:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("−", key=rem_key, disabled=not can_rem):
                    refund = xp_cost_for_next_dot(skill_name, tree_name, {**own, skill_name: d - 1}) + 0
                    # Actual refund = cost of that last dot = xp_next at old state
                    refund = get_static_base(skill_name, tree_name) + d
                    own[skill_name] = d - 1
                    log_xp_refund(char, f"{skill_name} −1 dot", refund)
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
                log_xp_refund(char, f"{cname} −1 dot", d)
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
    section_header("Stage 4 — Disciplines")

    unlocked = char["unlocked_disciplines"]

    if len(unlocked) < MAX_DISCIPLINES:
        _select_disciplines(char)
    else:
        _spend_disc_xp(char)

    st.divider()
    _nav_buttons(char, 4)


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
                    # Necromancy.png is 1280×960 landscape; scale width so height ≈ 48px
                    w = 64 if "Necromancy" in img else 48
                    st.image(img, width=w)
                except Exception:
                    pass
            else:
                st.image(img, width=48)

            if already:
                if st.button(f"✓ {disc_name}", key=f"unsel_disc_{disc_name}", type="secondary"):
                    unlocked.remove(disc_name)
                    # Remove level & powers too
                    char["discipline_levels"].pop(disc_name, None)
                    char["discipline_powers"].pop(disc_name, None)
                    st.rerun()
            else:
                disabled = remaining_slots == 0
                if st.button(disc_name, key=f"sel_disc_{disc_name}", disabled=disabled):
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
                # Necromancy.png is 1280×960 landscape; scale width so height ≈ 60px
                w = 80 if "Necromancy" in img else 60
                st.image(img, width=w)
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
                # Remove last acquired power
                if powers:
                    powers.pop()
                refund = level  # cost of that last level
                char["discipline_levels"][disc_name] = level - 1
                log_xp_refund(char, f"{disc_name} level {level} → {level-1}", refund)
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
            # Can release if acquired AND no other power requires this one
            dependents = [p2 for p2 in disc["powers"] if p2.get("requires") == power["name"] and p2["name"] in powers]
            can_release = acquired and not dependents

            col_p, col_btn = st.columns([5, 1])
            with col_p:
                icon = "●" if acquired else ("○" if req_met else "🔒")
                req_note = f" *(requires {req})*" if req and not req_met else ""
                st.markdown(
                    f"&nbsp;&nbsp;{icon} **{power['name']}**{req_note}  \n"
                    f"&nbsp;&nbsp;<small style='color:#9a8f82'>{power['description']}</small>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if acquired:
                    if st.button("✕", key=f"release_{disc_name}_{power['name']}", disabled=not can_release):
                        powers.remove(power["name"])
                        st.rerun()
                else:
                    if st.button("✓", key=f"acquire_{disc_name}_{power['name']}", disabled=not can_acquire):
                        powers.append(power["name"])
                        st.rerun()


# ── Stage 5: Clan ─────────────────────────────────────────────────────────────

def _stage_clan(char: dict) -> None:
    section_header("Stage 5 — Clan")
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
                st.markdown(
                    f"<img src='{clan['image']}' style='width:80px;height:80px;"
                    f"object-fit:contain;filter:invert(1)'>",
                    unsafe_allow_html=True,
                )
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
            if st.button("← Back", key="back_5"):
                char["wizard_stage"] = 4
                st.rerun()
        with col_finish:
            if st.button("Complete Character ✓", key="finish_wizard", type="primary"):
                char["wizard_complete"] = True
                st.success("Character complete! Navigate to the Character Sheet.")
                st.rerun()
