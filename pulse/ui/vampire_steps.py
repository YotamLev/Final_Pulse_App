from __future__ import annotations

from typing import Any

import streamlit as st

from pulse.caps import (
    attribute_adjustment_bounds,
    effective_attribute_max,
    get_attribute_values,
    skills_with_predator_room,
)
from pulse.constants import ATTRIBUTES, INNATE_VAMPIRE_ABILITIES, PREDATOR_SKILL_DOTS
from pulse.data_loader import load_clans, load_predator_types
from pulse.models import export_filename
from pulse.sheet import render_character_sheet
from pulse.powers import available_powers, has_predator_bonus, power_by_id, disciplines_list, sorcery_paths_list
from pulse.ui.mortal_steps import render_errors
from pulse.vampire import (
    clan_by_id,
    ensure_predator,
    ensure_vampire,
    get_clan_disciplines,
    discipline_pick_options,
    known_discipline_names,
    non_predator_powers,
    power_entry_from_def,
    predator_powers,
    set_discipline_slot,
    set_predator_powers,
    sync_non_predator_power,
    upsert_non_predator_power,
)


def clear_vampire_widget_state() -> None:
    prefixes = ("l0_", "l1_", "l2_", "pred_", "bane_")
    for key in list(st.session_state.keys()):
        if key.startswith(prefixes):
            del st.session_state[key]


def _power_label(power: dict) -> str:
    tag = " ★ predator bonus" if has_predator_bonus(power) else ""
    return f"{power['name']} ({power['source']}){tag}"


def _init_widget_choice(key: str, saved: str | None, options: list[str]) -> None:
    if key not in st.session_state and saved and saved in options:
        st.session_state[key] = saved


def _power_select(
    character: dict,
    *,
    key: str,
    allowed_sources: list[str],
    include_amalgams: bool = False,
    label: str = "Choose a power",
    saved_power_id: str | None = None,
) -> dict | None:
    options = available_powers(
        character,
        allowed_sources=allowed_sources,
        include_amalgams=include_amalgams,
        keep_power_id=saved_power_id,
    )
    if saved_power_id:
        saved_def = power_by_id(saved_power_id)
        if saved_def and not any(p["id"] == saved_power_id for p in options):
            options = sorted(
                [saved_def] + [p for p in options if p["id"] != saved_power_id],
                key=lambda p: (p["source"], p["name"]),
            )
    if not options:
        st.warning("No powers available. Check prerequisites or Disciplines.")
        return None
    labels = [_power_label(p) for p in options]
    if saved_power_id and key not in st.session_state:
        for power, label_text in zip(options, labels):
            if power["id"] == saved_power_id:
                st.session_state[key] = label_text
                break
    choice = st.selectbox(label, labels, key=key)
    idx = labels.index(choice)
    power = options[idx]
    st.markdown(power.get("summary", ""))
    if power.get("prerequisites"):
        st.caption(f"Requires: {power['prerequisites'].get('raw', '')}")
    return power


def step_embrace(character: dict[str, Any]) -> None:
    st.subheader("The Embrace")
    st.caption("Unluckily for you, you were Embraced. Choose your clan — you now bear its Bane.")

    v = ensure_vampire(character)
    clans = load_clans()
    clan_ids = [c["id"] for c in clans]
    clan_labels = {c["id"]: c["name"] for c in clans}

    current = v.get("clan") or clan_ids[0]
    if current not in clan_ids:
        current = clan_ids[0]

    v["clan"] = st.selectbox(
        "Clan",
        clan_ids,
        index=clan_ids.index(current),
        format_func=lambda x: clan_labels[x],
    )
    clan = clan_by_id(v["clan"])
    if clan:
        st.markdown(f"*{clan['description']}*")
        st.markdown(f"**Disciplines:** {', '.join(clan['disciplines'])}")
        st.info(clan["bane"]["summary"])
        fields = v.setdefault("bane", {}).setdefault("fields", {})
        for field in clan["bane"].get("fields", []):
            if field["type"] == "select":
                fields[field["id"]] = st.selectbox(
                    field["label"],
                    field.get("options", []),
                    index=0,
                    key=f"bane_{field['id']}",
                )
            else:
                fields[field["id"]] = st.text_input(
                    field["label"],
                    value=fields.get(field["id"], ""),
                    key=f"bane_{field['id']}",
                )


def step_level_0(character: dict[str, Any]) -> None:
    st.subheader("Level 0 — Neonate")
    st.caption("Choose one clan Discipline and your first power. You gain innate vampiric abilities.")

    for line in INNATE_VAMPIRE_ABILITIES:
        st.markdown(f"- {line}")

    v = ensure_vampire(character)
    clan_discs = get_clan_disciplines(character)
    taken = known_discipline_names(character)
    saved_disc = taken[0] if taken else None
    _init_widget_choice("l0_disc", saved_disc, clan_discs)

    disc = st.selectbox("First Discipline", clan_discs, key="l0_disc")
    set_discipline_slot(v, 0, disc, "clan", 0)

    saved_power = non_predator_powers(v)[0]["id"] if non_predator_powers(v) else None
    power = _power_select(
        character,
        key="l0_power",
        allowed_sources=[disc],
        label="First power",
        saved_power_id=saved_power,
    )
    sync_non_predator_power(v, 0, power, 0)
    if v.get("disciplines") and (non_predator_powers(v) or predator_powers(v)):
        v["level"] = max(int(v.get("level", 0)), 0)


def _attr_editor(character: dict, level: int, key_prefix: str) -> None:
    v = ensure_vampire(character)
    block = next((b for b in v["attribute_adjustments"] if b.get("level") == level), None)
    if not block:
        block = {"level": level, "changes": {}}
        v["attribute_adjustments"].append(block)
    changes = block["changes"]
    budget = 2
    st.caption(f"Assign dots (exactly {budget} total).")

    cols = st.columns(3)
    for i, attr in enumerate(ATTRIBUTES):
        base, max_assignable, assigned = attribute_adjustment_bounds(
            character, attr, level_changes=changes, budget=budget
        )
        cap = effective_attribute_max(character, attr)
        widget_key = f"{key_prefix}_{attr}"
        value = min(assigned, max_assignable)
        if assigned != value:
            if value:
                changes[attr] = value
            elif attr in changes:
                del changes[attr]
        if widget_key in st.session_state and int(st.session_state[widget_key]) > max_assignable:
            st.session_state[widget_key] = value
        with cols[i % 3]:
            delta = st.number_input(
                f"{attr} ({base} → max {cap})",
                min_value=0,
                max_value=max_assignable,
                value=value,
                key=widget_key,
            )
            if delta:
                changes[attr] = delta
            elif attr in changes:
                del changes[attr]

    total = sum(int(v) for v in changes.values())
    st.progress(min(total / budget, 1.0), text=f"Assigned {total} / {budget}")


def step_l1_attributes(character: dict[str, Any]) -> None:
    st.subheader("Level 1 — Physical adaptation")
    st.caption("Add 2 attribute dots to your base attributes.")
    _attr_editor(character, 1, "l1_attr")


def step_l1_discipline_power(character: dict[str, Any]) -> None:
    st.subheader("Level 1 — Second Discipline")
    v = ensure_vampire(character)
    clan_discs = get_clan_disciplines(character)
    taken = known_discipline_names(character)
    first = taken[0] if taken else clan_discs[0]
    disc_options = [d for d in clan_discs if d != first]
    saved_second = taken[1] if len(taken) > 1 else None
    _init_widget_choice("l1_disc2", saved_second, disc_options)

    disc2 = st.selectbox("Second clan Discipline", disc_options, key="l1_disc2")
    set_discipline_slot(v, 1, disc2, "clan", 1)

    known_discs = known_discipline_names(character)
    saved_power = non_predator_powers(v)[1]["id"] if len(non_predator_powers(v)) > 1 else None
    power = _power_select(
        character,
        key="l1_power2",
        allowed_sources=known_discs,
        include_amalgams=len(known_discs) >= 2,
        label="Second power (from your known Disciplines)",
        saved_power_id=saved_power,
    )
    sync_non_predator_power(v, 1, power, 1)


def _predator_branch_hints(pdef: dict) -> str:
    parts: list[str] = []
    for branch in pdef.get("skill_branches") or []:
        skills = branch.get("skills") or []
        examples = branch.get("specialty_examples") or []
        if not skills:
            continue
        hint = " / ".join(skills)
        if examples and examples[0]:
            hint += f" ({examples[0]})"
        parts.append(hint)
    return " · ".join(parts)


def _predator_specialty_placeholder(pdef: dict | None, skill: str) -> str:
    if not pdef or not skill:
        return ""
    for branch in pdef.get("skill_branches") or []:
        if skill in (branch.get("skills") or []):
            examples = branch.get("specialty_examples") or []
            return examples[0] if examples else ""
    return ""


def _predator_skill_and_specialty(
    character: dict[str, Any],
    predator: dict[str, Any],
    *,
    skill_key: str,
    spec_key: str,
    pdef: dict | None = None,
) -> None:
    eligible = skills_with_predator_room(character)
    saved_sk = (predator.get("skill_choice") or {}).get("skill", "")
    if saved_sk and saved_sk not in eligible:
        eligible = [saved_sk] + [s for s in eligible if s != saved_sk]
    if not eligible:
        st.error("No specialty has room for +2 predator dots (max 5 effective). Remove dots elsewhere first.")
        skill = ""
    else:
        skill = st.selectbox(
            "Skill for +2 dots",
            eligible,
            index=eligible.index(saved_sk) if saved_sk in eligible else 0,
            key=skill_key,
        )
    predator["skill_choice"] = {"skill": skill, "dots": PREDATOR_SKILL_DOTS}
    saved_spec = predator.get("specialty") or {}
    spec_default = saved_spec.get("text", "") if saved_spec.get("skill") == skill else ""
    placeholder = _predator_specialty_placeholder(pdef, skill) or "Specialty for this skill"
    predator["specialty"] = {
        "skill": skill,
        "text": st.text_input(
            "Specialty",
            value=spec_default,
            placeholder=placeholder,
            key=spec_key,
        ),
    }


def step_predator(character: dict[str, Any]) -> None:
    st.subheader("Level 1 — Predator type")
    st.caption(
        f"Your feeding style grants {PREDATOR_SKILL_DOTS} skill dots, a specialty, and a predator power. "
        f"Skill dots cannot exceed 5 effective rating per specialty at creation."
    )

    v = ensure_vampire(character)
    types = load_predator_types()
    type_ids = [t["id"] for t in types] + ["__custom__"]
    labels = {t["id"]: t["name"] for t in types}
    labels["__custom__"] = "Custom predator type…"

    predator = ensure_predator(v)
    current = predator.get("type") or type_ids[0]
    pick = st.selectbox("Predator type", type_ids, format_func=lambda x: labels.get(x, x), key="pred_type")
    predator["type"] = pick if pick != "__custom__" else predator.get("type", "")

    if pick == "__custom__":
        predator["source"] = "custom"
        predator["custom_name"] = st.text_input("Custom name", value=predator.get("custom_name", ""))
        predator["custom_description"] = st.text_area(
            "Description",
            value=predator.get("custom_description", ""),
        )
        predator["type"] = "custom"
        _predator_skill_and_specialty(
            character,
            predator,
            skill_key="pred_custom_skill",
            spec_key="pred_custom_spec",
        )
        sources = disciplines_list() + sorcery_paths_list()
    else:
        predator["source"] = "curated"
        pdef = next(t for t in types if t["id"] == pick)
        st.markdown(f"*{pdef['description']}*")
        if pdef.get("status") == "tbd":
            st.warning("This predator type is not fully curated — power suggestions may be incomplete.")
        hints = _predator_branch_hints(pdef)
        if hints:
            st.caption(f"Suggested skills (any skill allowed): {hints}")
        _predator_skill_and_specialty(
            character,
            predator,
            skill_key="pred_skill",
            spec_key="pred_spec",
            pdef=pdef,
        )
        sources = pdef.get("relevant_disciplines") or disciplines_list()
        if not sources:
            sources = disciplines_list()

    needed = 1
    pdef = next((t for t in types if t["id"] == predator.get("type")), None) if predator.get("source") == "curated" else None
    rules = (pdef.get("special_rules") if pdef else None) or {}
    if rules.get("predator_power_count") == 2:
        needed = 2
        st.info("Leech: choose 2 powers from the same Discipline.")

    existing_pred = predator_powers(v)
    pred_entries: list[dict] = []
    for i in range(needed):
        saved_id = existing_pred[i]["id"] if i < len(existing_pred) else None
        power = _power_select(
            character,
            key=f"pred_power_{i}",
            allowed_sources=sources if sources else disciplines_list(),
            include_amalgams=True,
            label=f"Predator power {i + 1}",
            saved_power_id=saved_id,
        )
        if power:
            pred_entries.append(power_entry_from_def(power, 1, is_predator_power=True))
        elif i < len(existing_pred):
            pred_entries.append(existing_pred[i])
    set_predator_powers(v, pred_entries)

    if rules.get("feeding_restriction"):
        st.caption("Feeding restriction: vampires only (like Ventrue bane).")

    v["level"] = 1


def step_l2_attributes(character: dict[str, Any]) -> None:
    st.subheader("Level 2 — Eternal body")
    st.caption("Add 2 attribute dots.")
    _attr_editor(character, 2, "l2_attr")


def step_l2_discipline_power(character: dict[str, Any]) -> None:
    st.subheader("Level 2 — Third Discipline")
    v = ensure_vampire(character)
    clan_discs = get_clan_disciplines(character)
    all_discs = disciplines_list()
    all_paths = sorcery_paths_list()
    taken_names = known_discipline_names(character)
    pool = clan_discs + all_discs + all_paths
    disc_options = discipline_pick_options(character, 2, pool)
    saved_third = taken_names[2] if len(taken_names) > 2 else None
    _init_widget_choice("l2_disc3", saved_third, disc_options)

    disc3 = st.selectbox("Third Discipline (clan or any)", disc_options, key="l2_disc3")
    source = "clan" if disc3 in clan_discs else "other"
    set_discipline_slot(v, 2, disc3, source, 2)

    known = known_discipline_names(character)
    non_pred = non_predator_powers(v)
    saved_power = non_pred[2]["id"] if len(non_pred) > 2 else None
    power = _power_select(
        character,
        key="l2_power4",
        allowed_sources=known,
        include_amalgams=True,
        label="Fourth power (from your known Disciplines)",
        saved_power_id=saved_power,
    )
    sync_non_predator_power(v, 2, power, 2)
    v["level"] = max(int(v.get("level", 0)), 2)


def step_complete(character: dict[str, Any]) -> None:
    from pulse.ui.levelup import render_level_up_panel

    st.subheader("The Damned — Character Complete")
    st.success("You have survived creation. Export your sheet or continue leveling up.")

    v = ensure_vampire(character)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vampire level", v.get("level", 0))
    c2.metric("Disciplines", len(v.get("disciplines", [])))
    c3.metric("Powers", len(v.get("powers", [])))
    c4.metric("Clan", clan_by_id(v.get("clan", ""))["name"] if v.get("clan") else "—")

    sheet_name = export_filename(character).replace(".json", ".html")
    st.download_button(
        "Export character sheet",
        data=render_character_sheet(character),
        file_name=sheet_name,
        mime="text/html",
        type="primary",
        use_container_width=True,
        key="complete_export_sheet",
    )

    st.divider()
    st.markdown("**Disciplines**")
    for d in v.get("disciplines", []):
        st.markdown(f"- {d['name']} (level {d['acquired_at_level']})")
    st.markdown("**Powers**")
    for p in v.get("powers", []):
        tag = " — predator" if p.get("is_predator_power") else ""
        st.markdown(f"- {p['name']} ({p['source']}){tag}")

    st.divider()
    st.subheader("Level up")
    render_level_up_panel(character, apply_label="Level up")


VAMPIRE_STEP_RENDERERS = {
    9: step_embrace,
    10: step_level_0,
    11: step_l1_attributes,
    12: step_l1_discipline_power,
    13: step_predator,
    14: step_l2_attributes,
    15: step_l2_discipline_power,
    16: step_complete,
}


def render_vampire_step(character: dict[str, Any], step: int) -> None:
    renderer = VAMPIRE_STEP_RENDERERS.get(step)
    if renderer:
        renderer(character)
