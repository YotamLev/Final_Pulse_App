from __future__ import annotations

from typing import Any

import streamlit as st

from pulse.caps import effective_attribute_max, get_attribute_values, get_skill_dots
from pulse.constants import ATTRIBUTES, INNATE_VAMPIRE_ABILITIES
from pulse.data_loader import load_clans, load_predator_types, skill_category_map
from pulse.models import ensure_skill
from pulse.powers import available_powers, has_predator_bonus, power_by_id, disciplines_list, sorcery_paths_list
from pulse.ui.mortal_steps import render_errors
from pulse.vampire import add_discipline, add_power, clan_by_id, ensure_predator, ensure_vampire, get_clan_disciplines


def _power_select(
    character: dict,
    *,
    key: str,
    allowed_sources: list[str],
    include_amalgams: bool = False,
    label: str = "Choose a power",
) -> dict | None:
    options = available_powers(
        character,
        allowed_sources=allowed_sources,
        include_amalgams=include_amalgams,
    )
    if not options:
        st.warning("No powers available. Check prerequisites or Disciplines.")
        return None
    labels = []
    for p in options:
        tag = " ★ predator bonus" if has_predator_bonus(p) else ""
        labels.append(f"{p['name']} ({p['source']}){tag}")
    choice = st.selectbox(label, labels, key=key)
    idx = labels.index(choice)
    power = options[idx]
    with st.expander("Power details"):
        st.write(power.get("summary", ""))
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
    existing = [d["name"] for d in v.get("disciplines", [])]

    disc = st.selectbox("First Discipline", clan_discs, key="l0_disc")
    pred_powers = [p for p in v.get("powers", []) if p.get("is_predator_power")]
    v["disciplines"] = [{"name": disc, "source": "clan", "acquired_at_level": 0}]

    power = _power_select(character, key="l0_power", allowed_sources=[disc], label="First power")
    v["powers"] = list(pred_powers)
    if power:
        v["powers"].append(
            {
                "id": power["id"],
                "name": power["name"],
                "source": disc,
                "acquired_at_level": 0,
                "is_predator_power": False,
            }
        )
    if v["powers"] and v["disciplines"]:
        v["level"] = 0


def _attr_editor(character: dict, level: int, key_prefix: str) -> None:
    v = ensure_vampire(character)
    block = next((b for b in v["attribute_adjustments"] if b.get("level") == level), None)
    if not block:
        block = {"level": level, "changes": {}}
        v["attribute_adjustments"].append(block)
    changes = block["changes"]
    attrs = get_attribute_values(character)
    st.caption("Assign dots (exactly 2 total).")

    cols = st.columns(3)
    for i, attr in enumerate(ATTRIBUTES):
        cap = effective_attribute_max(character, attr)
        current = attrs.get(attr, 2)
        max_delta = max(0, cap - current)
        widget_key = f"{key_prefix}_{attr}"
        extra = min(int(changes.get(attr, 0)), max_delta)
        if widget_key in st.session_state and int(st.session_state[widget_key]) > max_delta:
            st.session_state[widget_key] = extra
        with cols[i % 3]:
            delta = st.number_input(
                f"{attr} ({current}→ max {cap})",
                min_value=0,
                max_value=max_delta,
                value=extra,
                key=widget_key,
            )
            if delta:
                changes[attr] = delta
            elif attr in changes:
                del changes[attr]


def step_l1_attributes(character: dict[str, Any]) -> None:
    st.subheader("Level 1 — Physical adaptation")
    st.caption("Add 2 attribute dots to your base attributes.")
    _attr_editor(character, 1, "l1_attr")


def step_l1_discipline_power(character: dict[str, Any]) -> None:
    st.subheader("Level 1 — Second Discipline")
    v = ensure_vampire(character)
    clan_discs = get_clan_disciplines(character)
    taken = [d["name"] for d in v.get("disciplines", [])]
    options = [d for d in clan_discs if d not in taken] or clan_discs

    disc2 = st.selectbox("Second clan Discipline", options, key="l1_disc2")
    if len(taken) < 2:
        add_discipline(character, disc2, "clan", 1)
    elif taken[1] != disc2:
        v["disciplines"] = [v["disciplines"][0], {"name": disc2, "source": "clan", "acquired_at_level": 1}]

    known_discs = [d["name"] for d in v.get("disciplines", [])]
    power = _power_select(
        character,
        key="l1_power2",
        allowed_sources=known_discs,
        include_amalgams=len(known_discs) >= 2,
        label="Second power (from either Discipline)",
    )
    if power:
        non_pred = [p for p in v.get("powers", []) if not p.get("is_predator_power")]
        preds = [p for p in v.get("powers", []) if p.get("is_predator_power")]
        entry = {
            "id": power["id"],
            "name": power["name"],
            "source": power["source"],
            "acquired_at_level": 1,
            "is_predator_power": False,
        }
        if len(non_pred) < 2:
            if len(non_pred) == 1:
                non_pred.append(entry)
            else:
                non_pred = [entry]
        else:
            non_pred[1] = entry
        v["powers"] = non_pred + preds


def step_predator(character: dict[str, Any]) -> None:
    st.subheader("Level 1 — Predator type")
    st.caption("Your feeding style grants 2 skill dots, a specialty, and a predator power.")

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
        sk = st.text_input("Skill for +2 dots", value=(predator.get("skill_choice") or {}).get("skill", ""))
        predator["skill_choice"] = {"skill": sk, "dots": 2}
        predator["specialty"] = {
            "skill": sk,
            "text": st.text_input("Specialty", value=(predator.get("specialty") or {}).get("text", "")),
        }
        sources = disciplines_list() + sorcery_paths_list()
    else:
        predator["source"] = "curated"
        pdef = next(t for t in types if t["id"] == pick)
        st.markdown(f"*{pdef['description']}*")
        if pdef.get("status") == "tbd":
            st.warning("This type has no curated skill list — assign freely.")
        branches = pdef.get("skill_branches") or [{"skills": list(skill_category_map().keys())[:5], "specialty_examples": [""]}]
        branch_idx = st.radio("Skill branch", range(len(branches)), format_func=lambda i: " or ".join(branches[i]["skills"]), key="pred_branch")
        branch = branches[branch_idx]
        skill = st.selectbox("Skill (+2 dots)", branch["skills"], key="pred_skill")
        predator["skill_choice"] = {"skill": skill, "dots": 2}
        ex = branch.get("specialty_examples", [""])
        predator["specialty"] = {
            "skill": skill,
            "text": st.text_input("Specialty", value=ex[0] if ex else "", key="pred_spec"),
        }
        sources = pdef.get("relevant_disciplines") or disciplines_list()
        if not sources:
            sources = disciplines_list()

    needed = 1
    pdef = next((t for t in types if t["id"] == predator.get("type")), None) if predator.get("source") == "curated" else None
    if pdef and pdef.get("special_rules", {}) and pdef["special_rules"].get("predator_power_count") == 2:
        needed = 2
        st.info("Leech: choose 2 powers from the same Discipline.")

    v["powers"] = [p for p in v.get("powers", []) if not p.get("is_predator_power")]
    pred_entries = []
    for i in range(needed):
        power = _power_select(
            character,
            key=f"pred_power_{i}",
            allowed_sources=sources if sources else disciplines_list(),
            include_amalgams=True,
            label=f"Predator power {i + 1}",
        )
        if power:
            pred_entries.append(
                {
                    "id": power["id"],
                    "name": power["name"],
                    "source": power["source"],
                    "acquired_at_level": 1,
                    "is_predator_power": True,
                }
            )
    v["powers"] = v["powers"] + pred_entries

    if pdef and pdef.get("special_rules", {}).get("feeding_restriction"):
        st.caption("Feeding restriction: vampires only (like Ventrue bane).")

    v["level"] = 1


def step_l2_skill_removal(character: dict[str, Any]) -> None:
    st.subheader("Level 2 — Forgotten skills")
    st.caption("Lose 2 skill dots you forgot.")

    v = ensure_vampire(character)
    block = next((b for b in v["skill_adjustments"] if b.get("level") == 2), None)
    if not block:
        block = {"level": 2, "removed": {}}
        v["skill_adjustments"].append(block)
    removed = block["removed"]
    skills = {k: v for k, v in get_skill_dots(character).items() if v > 0}
    if not skills:
        st.warning("No skills to remove.")
        return
    total_removed = 0
    for skill_name, dots in sorted(skills.items()):
        max_remove = min(dots, 2 - total_removed + int(removed.get(skill_name, 0)))
        val = st.number_input(
            f"Remove from {skill_name} ({dots} dots)",
            min_value=0,
            max_value=dots,
            value=int(removed.get(skill_name, 0)),
            key=f"rm_{skill_name}",
        )
        if val:
            removed[skill_name] = val
        elif skill_name in removed:
            del removed[skill_name]
    total_removed = sum(removed.values())
    st.progress(min(total_removed / 2, 1.0), text=f"Removed {total_removed} / 2")


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
    taken = {d["name"] for d in v.get("disciplines", [])}

    disc_options = sorted(set(clan_discs + all_discs + all_paths) - taken)
    disc3 = st.selectbox("Third Discipline (clan or any)", disc_options, key="l2_disc3")
    source = "clan" if disc3 in clan_discs else "other"
    if len(v.get("disciplines", [])) < 3:
        add_discipline(character, disc3, source, 2)
    else:
        v["disciplines"][2] = {"name": disc3, "source": source, "acquired_at_level": 2}

    known = [d["name"] for d in v.get("disciplines", [])]
    power = _power_select(
        character,
        key="l2_power4",
        allowed_sources=known,
        include_amalgams=True,
        label="Fourth power",
    )
    non_pred = [p for p in v.get("powers", []) if not p.get("is_predator_power")]
    preds = [p for p in v.get("powers", []) if p.get("is_predator_power")]
    if power:
        entry = {
            "id": power["id"],
            "name": power["name"],
            "source": power["source"],
            "acquired_at_level": 2,
            "is_predator_power": False,
        }
        if len(non_pred) < 4:
            if len(non_pred) == 3:
                non_pred.append(entry)
            else:
                non_pred.append(entry)
        else:
            non_pred[3] = entry
    v["powers"] = non_pred + preds
    v["level"] = 2


def step_complete(character: dict[str, Any]) -> None:
    from pulse.ui.levelup import render_level_up_panel

    st.subheader("The Damned — Character Complete")
    st.success("You have survived creation. Review your hunter of the night, save, or continue leveling up.")

    v = ensure_vampire(character)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vampire level", v.get("level", 0))
    c2.metric("Disciplines", len(v.get("disciplines", [])))
    c3.metric("Powers", len(v.get("powers", [])))
    c4.metric("Clan", clan_by_id(v.get("clan", ""))["name"] if v.get("clan") else "—")

    tab_review, tab_level = st.tabs(["Summary", "Level up (3+)"])
    with tab_review:
        st.markdown("**Disciplines**")
        for d in v.get("disciplines", []):
            st.markdown(f"- {d['name']} (level {d['acquired_at_level']})")
        st.markdown("**Powers**")
        for p in v.get("powers", []):
            tag = " — predator" if p.get("is_predator_power") else ""
            st.markdown(f"- {p['name']} ({p['source']}){tag}")
    with tab_level:
        render_level_up_panel(character)


VAMPIRE_STEP_RENDERERS = {
    9: step_embrace,
    10: step_level_0,
    11: step_l1_attributes,
    12: step_l1_discipline_power,
    13: step_predator,
    14: step_l2_skill_removal,
    15: step_l2_attributes,
    16: step_l2_discipline_power,
    17: step_complete,
}


def render_vampire_step(character: dict[str, Any], step: int) -> None:
    renderer = VAMPIRE_STEP_RENDERERS.get(step)
    if renderer:
        renderer(character)
