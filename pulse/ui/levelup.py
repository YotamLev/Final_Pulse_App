from __future__ import annotations

from typing import Any

import streamlit as st

from pulse.caps import effective_attribute_max, effective_skill_max, get_attribute_values, get_skill_dots, known_power_names
from pulse.constants import ATTRIBUTES
from pulse.data_loader import skill_category_map
from pulse.powers import available_powers, power_by_id
from pulse.ui.mortal_steps import render_errors
from pulse.vampire import add_power, ensure_vampire
from pulse.vampire_validation import validate_level_up


def _render_masterwork_choice(character: dict[str, Any]) -> None:
    v = ensure_vampire(character)
    if "Masterwork" not in known_power_names(character):
        return
    if v.get("cap_choices", {}).get("masterwork"):
        return

    st.markdown("#### Masterwork — skill cap bonus")
    st.caption("Choose how Masterwork raises your permanent skill maximums.")
    skills = sorted(skill_category_map().keys())
    mode = st.radio(
        "Bonus layout",
        ["one_skill_plus_two", "two_skills_plus_one"],
        format_func=lambda m: "+2 max on one skill" if m == "one_skill_plus_two" else "+1 max on two skills",
        key="mw_mode",
    )
    if mode == "one_skill_plus_two":
        skill = st.selectbox("Skill (+2 cap)", skills, key="mw_one")
        if st.button("Confirm Masterwork", key="mw_confirm_one"):
            v.setdefault("cap_choices", {})["masterwork"] = {
                "mode": mode,
                "skills": [skill],
            }
            st.session_state.pop("masterwork_pending", None)
            st.rerun()
    else:
        s1 = st.selectbox("First skill (+1 cap)", skills, key="mw_a")
        s2 = st.selectbox("Second skill (+1 cap)", skills, key="mw_b")
        if s1 == s2:
            st.warning("Choose two different skills.")
        elif st.button("Confirm Masterwork", key="mw_confirm_two"):
            v.setdefault("cap_choices", {})["masterwork"] = {
                "mode": mode,
                "skills": [s1, s2],
            }
            st.session_state.pop("masterwork_pending", None)
            st.rerun()


def render_level_up_panel(character: dict[str, Any]) -> None:
    v = ensure_vampire(character)
    if v.get("level", 0) < 2:
        st.info("Complete creation through Level 2 first.")
        return

    st.markdown(f"**Current level:** {v.get('level', 0)}")
    _render_masterwork_choice(character)
    if st.session_state.get("masterwork_pending"):
        st.info("Finish configuring Masterwork before taking another advancement.")
        return

    choice = st.radio(
        "Advancement (pick one per level)",
        [
            ("attr", "+1 attribute dot"),
            ("power", "+1 Discipline power"),
            ("skills", "+2 skill dots"),
            ("specialties", "+3 specialties"),
        ],
        format_func=lambda x: x[1],
        key="levelup_choice",
    )
    choice_id = choice[0]
    details: dict = {}

    if choice_id == "attr":
        attrs = get_attribute_values(character)
        options = [a for a in ATTRIBUTES if attrs.get(a, 0) < effective_attribute_max(character, a)]
        if not options:
            st.warning("All attributes are at maximum.")
        else:
            details["attribute"] = st.selectbox("Attribute", options, key="lu_attr")
            details["dots"] = 1
    elif choice_id == "power":
        known = [d["name"] for d in v.get("disciplines", [])]
        options = available_powers(character, allowed_sources=known, include_amalgams=True)
        if not options:
            st.warning("No powers available.")
        else:
            labels = [f"{p['name']} ({p['source']})" for p in options]
            pick = st.selectbox("Power", labels, key="lu_power")
            power = options[labels.index(pick)]
            details["id"] = power["id"]
            st.caption(power.get("summary", "")[:300])
    elif choice_id == "skills":
        st.caption("Assign 2 dots total.")
        cats = skill_category_map()
        details = {}
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.selectbox("Skill 1", sorted(cats.keys()), key="lu_sk1")
            d1 = st.number_input("Dots", 0, 2, 1, key="lu_d1")
            if d1:
                details[s1] = d1
        with c2:
            s2 = st.selectbox("Skill 2", sorted(cats.keys()), key="lu_sk2")
            d2 = st.number_input("Dots ", 0, 2, 1, key="lu_d2")
            if d2 and s2 != s1:
                details[s2] = details.get(s2, 0) + d2
            elif d2 and s2 == s1:
                details[s1] = details.get(s1, 0) + d2
    elif choice_id == "specialties":
        skills = sorted(k for k, v in get_skill_dots(character).items() if v > 0)
        specs = []
        for i in range(3):
            c1, c2 = st.columns(2)
            with c1:
                sk = st.selectbox(f"Skill {i+1}", skills or [""], key=f"lu_sp_sk_{i}")
            with c2:
                tx = st.text_input(f"Specialty {i+1}", key=f"lu_sp_tx_{i}")
            specs.append({"skill": sk, "text": tx})
        details["specialties"] = specs

    errors = validate_level_up(character, choice_id, details)
    if errors:
        render_errors(errors)

    if st.button("Apply level-up", type="primary", disabled=bool(errors), key="lu_apply"):
        _apply_level_up(character, choice_id, details)
        st.success(f"Advanced to level {v['level']}!")
        st.rerun()

    if v.get("level_ups"):
        st.markdown("**Level-up history**")
        for entry in v["level_ups"]:
            st.caption(f"→ Level {entry['to_level']}: {entry['choice']}")


def _apply_level_up(character: dict, choice: str, details: dict) -> None:
    v = ensure_vampire(character)
    new_level = int(v.get("level", 2)) + 1
    entry = {"to_level": new_level, "choice": choice, "details": details}

    if choice == "attr":
        for block in v["attribute_adjustments"]:
            if block.get("level") == new_level:
                break
        else:
            v["attribute_adjustments"].append({"level": new_level, "changes": {details["attribute"]: 1}})
    elif choice == "power":
        power = power_by_id(details["id"])
        if power:
            add_power(character, power, new_level)
            if power["name"] == "Masterwork":
                st.session_state["masterwork_pending"] = True
    elif choice == "skills":
        v["skill_adjustments"].append({"level": new_level, "added": dict(details)})
    elif choice == "specialties":
        v.setdefault("specialty_adjustments", []).append({"level": new_level, "added": details["specialties"]})
        mortal_specs = character["mortal"].setdefault("specialties", [])
        mortal_specs.extend(details["specialties"])

    v["level_ups"].append(entry)
    v["level"] = new_level
