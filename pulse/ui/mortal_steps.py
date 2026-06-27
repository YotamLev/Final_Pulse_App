from __future__ import annotations

from typing import Any

import streamlit as st

from pulse.constants import (
    ATTRIBUTE_DESCRIPTIONS,
    ATTRIBUTE_GROUPS,
    ATTRIBUTES,
    POOL_PROMPTS,
    SKILL_MAX_DEFAULT,
    TOTAL_SKILL_DOTS,
)
from pulse.data_loader import load_language_suggestions, load_skills, load_trait_suggestions
from pulse.models import assign_skill_dots, ensure_skill
from pulse.validation import total_skill_dots, validate_step


def render_errors(errors: list[str]) -> None:
    for error in errors:
        st.error(error)


def _trait_suggestion_labels(suggestions: list[dict]) -> list[str]:
    return ["— custom —"] + [f"{s['name']} (+{s['plus']}/−{s['minus']})" for s in suggestions]


def _suggestion_from_label(label: str, suggestions: list[dict]) -> dict | None:
    for suggestion in suggestions:
        if f"{suggestion['name']} (+{suggestion['plus']}/−{suggestion['minus']})" == label:
            return suggestion
    return None


def _attrs_used_by_other_traits(index: int, traits: list[dict]) -> set[str]:
    used: set[str] = set()
    for i, trait in enumerate(traits):
        if i == index:
            continue
        plus = st.session_state.get(f"trait_plus_{i}", trait.get("plus", ""))
        minus = st.session_state.get(f"trait_minus_{i}", trait.get("minus", ""))
        for attr in (plus, minus):
            if attr:
                used.add(attr)
    return used


def _filtered_suggestion_labels(
    suggestions: list[dict],
    used_elsewhere: set[str],
    *,
    current_pick: str | None = None,
) -> list[str]:
    labels = ["— custom —"]
    for suggestion in suggestions:
        if suggestion["plus"] in used_elsewhere or suggestion["minus"] in used_elsewhere:
            continue
        labels.append(f"{suggestion['name']} (+{suggestion['plus']}/−{suggestion['minus']})")
    if current_pick and current_pick not in labels and current_pick != "— custom —":
        labels.append(current_pick)
    return labels


def _filtered_attributes(
    used_elsewhere: set[str],
    *,
    exclude: str | None = None,
    current: str | None = None,
) -> list[str]:
    options = [attr for attr in ATTRIBUTES if attr not in used_elsewhere]
    if exclude:
        options = [attr for attr in options if attr != exclude]
    if current and current in ATTRIBUTES and current not in options:
        options.append(current)
    return options


def _trait_pick_label(trait: dict, suggestions: list[dict]) -> str:
    for suggestion in suggestions:
        if (
            suggestion["name"] == trait.get("name")
            and suggestion["plus"] == trait.get("plus")
            and suggestion["minus"] == trait.get("minus")
        ):
            return f"{suggestion['name']} (+{suggestion['plus']}/−{suggestion['minus']})"
    return "— custom —"


def _apply_trait_suggestion(index: int, suggestions: list[dict], labels: list[str]) -> None:
    pick = st.session_state.get(f"trait_pick_{index}", "— custom —")
    if pick == "— custom —":
        return
    chosen = _suggestion_from_label(pick, suggestions)
    if not chosen:
        return
    st.session_state[f"trait_name_{index}"] = chosen["name"]
    st.session_state[f"trait_plus_{index}"] = chosen["plus"]
    st.session_state[f"trait_minus_{index}"] = chosen["minus"]


def clear_trait_widget_state() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(("trait_pick_", "trait_name_", "trait_plus_", "trait_minus_")):
            del st.session_state[key]


def clear_skill_widget_state() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(("skill_dots_", "filter_skills", "custom_name_skills", "custom_cat_skills", "custom_dots_skills")):
            del st.session_state[key]


def step_chronicle(character: dict[str, Any]) -> None:
    st.subheader("Chronicle & Concept")
    st.caption("Create a human born in a time and place appropriate to your chronicle.")

    character.setdefault("character", {})["name"] = st.text_input(
        "Character name",
        value=character.get("character", {}).get("name", ""),
    )
    character.setdefault("chronicle", {})
    character["chronicle"]["name"] = st.text_input(
        "Chronicle name (optional)",
        value=character["chronicle"].get("name", ""),
    )
    character["chronicle"]["time_and_place"] = st.text_input(
        "Time & place *",
        value=character["chronicle"].get("time_and_place", ""),
        placeholder="e.g. Chicago, 2019",
    )

    concept = character.setdefault("concept", {})
    concept["childhood"] = st.text_area("Childhood", value=concept.get("childhood", ""), height=80)
    concept["adulthood"] = st.text_area("Adulthood", value=concept.get("adulthood", ""), height=80)
    concept["personality"] = st.text_area("Personality", value=concept.get("personality", ""), height=80)
    concept["mannerisms"] = st.text_area("Mannerisms", value=concept.get("mannerisms", ""), height=80)


def step_traits(character: dict[str, Any]) -> None:
    st.subheader("Traits")
    st.caption(
        "Assign three traits. Each gives +1 to one attribute and −1 to another. "
        "No attribute overlap. Result: 3 at 3, 3 at 2, 3 at 1."
    )

    mortal = character.setdefault("mortal", {})
    traits = mortal.setdefault("traits", [{}, {}, {}])
    suggestions = load_trait_suggestions()
    suggestion_labels = _trait_suggestion_labels(suggestions)

    for index in range(3):
        st.markdown(f"**Trait {index + 1}**")
        cols = st.columns([2, 1, 1, 1])
        pick_key = f"trait_pick_{index}"
        used_elsewhere = _attrs_used_by_other_traits(index, traits)
        filtered_labels = _filtered_suggestion_labels(
            suggestions,
            used_elsewhere,
            current_pick=st.session_state.get(pick_key),
        )

        if pick_key not in st.session_state:
            initial = _trait_pick_label(traits[index], suggestions)
            if initial not in filtered_labels:
                initial = "— custom —"
            st.session_state[pick_key] = initial
            _apply_trait_suggestion(index, suggestions, suggestion_labels)
        elif st.session_state[pick_key] not in filtered_labels:
            st.session_state[pick_key] = "— custom —"

        cols[0].selectbox(
            f"Suggestion##{index}",
            filtered_labels,
            label_visibility="collapsed",
            key=pick_key,
            on_change=_apply_trait_suggestion,
            args=(index, suggestions, suggestion_labels),
        )

        current_plus = st.session_state.get(f"trait_plus_{index}", traits[index].get("plus", ATTRIBUTES[0]))
        current_minus = st.session_state.get(f"trait_minus_{index}", traits[index].get("minus", ATTRIBUTES[1]))
        plus_options = _filtered_attributes(used_elsewhere, exclude=current_minus, current=current_plus)
        minus_options = _filtered_attributes(used_elsewhere, exclude=current_plus, current=current_minus)

        plus_key = f"trait_plus_{index}"
        minus_key = f"trait_minus_{index}"
        if plus_key in st.session_state and st.session_state[plus_key] not in plus_options and plus_options:
            st.session_state[plus_key] = plus_options[0]
            current_plus = plus_options[0]
        if minus_key in st.session_state and st.session_state[minus_key] not in minus_options and minus_options:
            st.session_state[minus_key] = minus_options[0]
            current_minus = minus_options[0]

        traits[index]["name"] = cols[1].text_input(
            "Name",
            value=traits[index].get("name", ""),
            key=f"trait_name_{index}",
        )
        traits[index]["plus"] = cols[2].selectbox(
            "+1",
            plus_options,
            index=plus_options.index(current_plus) if current_plus in plus_options else 0,
            key=f"trait_plus_{index}",
        )
        traits[index]["minus"] = cols[3].selectbox(
            "−1",
            minus_options,
            index=minus_options.index(current_minus) if current_minus in minus_options else 0,
            key=f"trait_minus_{index}",
        )

        for s in suggestions:
            if s["name"] == traits[index].get("name"):
                st.caption(s.get("blurb", ""))
                break


def step_attributes(character: dict[str, Any]) -> None:
    st.subheader("Attributes")
    st.caption("Computed from your traits. Return to step 2 to change.")

    attrs = character.get("mortal", {}).get("attributes", {})
    for group, names in ATTRIBUTE_GROUPS.items():
        st.markdown(f"**{group}**")
        cols = st.columns(len(names))
        for col, name in zip(cols, names):
            col.metric(name, attrs.get(name, 2))
            col.caption(ATTRIBUTE_DESCRIPTIONS.get(name, ""))


def step_skills(character: dict[str, Any]) -> None:
    st.subheader("Skills")
    st.caption(
        f"Assign {TOTAL_SKILL_DOTS} dots across your skills (max {SKILL_MAX_DEFAULT} per skill). "
        "Consider your profession, life events, hobbies, and natural talents."
    )
    for prompt in POOL_PROMPTS.values():
        st.markdown(f"- {prompt}")

    assigned = total_skill_dots(character)
    st.progress(min(assigned / TOTAL_SKILL_DOTS, 1.0), text=f"Skills: {assigned} / {TOTAL_SKILL_DOTS} dots")

    filter_cat = st.selectbox("Filter by category", ["All", "Physical", "Social", "Mental"], key="filter_skills")

    filtered = [
        skill
        for skill in load_skills()
        if filter_cat == "All" or skill["category"] == filter_cat
    ]

    columns_per_row = 3
    for row_start in range(0, len(filtered), columns_per_row):
        row_skills = filtered[row_start : row_start + columns_per_row]
        cols = st.columns(columns_per_row)
        for col, skill in zip(cols, row_skills):
            with col:
                entry = ensure_skill(character, skill["name"], skill["category"])
                current = int(entry.get("dots", 0))
                new_val = st.number_input(
                    skill["name"],
                    min_value=0,
                    max_value=SKILL_MAX_DEFAULT,
                    value=current,
                    key=f"skill_dots_{skill['name']}",
                )
                assign_skill_dots(entry, new_val)

    with st.expander("Add custom skill"):
        custom_name = st.text_input("Custom skill name", key="custom_name_skills")
        custom_cat = st.selectbox("Category", ["Physical", "Social", "Mental"], key="custom_cat_skills")
        custom_dots = st.number_input(
            "Dots",
            min_value=0,
            max_value=SKILL_MAX_DEFAULT,
            value=0,
            key="custom_dots_skills",
        )
        if custom_name.strip():
            entry = ensure_skill(character, custom_name.strip(), custom_cat, custom=True)
            assign_skill_dots(entry, custom_dots)


def step_languages(character: dict[str, Any]) -> None:
    st.subheader("Languages")
    intelligence = int(character.get("mortal", {}).get("attributes", {}).get("Intelligence", 2))
    st.caption(f"Choose {intelligence} language(s) — one per Intelligence dot.")

    mortal = character.setdefault("mortal", {})
    languages = mortal.setdefault("languages", [])
    while len(languages) < intelligence:
        languages.append("")
    while len(languages) > intelligence:
        languages.pop()

    suggestions = [""] + load_language_suggestions()
    for index in range(intelligence):
        pick = st.selectbox(
            f"Language {index + 1}",
            suggestions,
            index=suggestions.index(languages[index]) if languages[index] in suggestions else 0,
            key=f"lang_pick_{index}",
        )
        if pick:
            languages[index] = pick
        else:
            languages[index] = st.text_input(
                "Or type a language",
                value=languages[index],
                key=f"lang_custom_{index}",
            )


def step_specialties(character: dict[str, Any]) -> None:
    st.subheader("Specialties")
    st.caption("Two specialties on two different skills (each skill needs at least 1 dot).")

    mortal = character.setdefault("mortal", {})
    specialties = mortal.setdefault("specialties", [{"skill": "", "text": ""}, {"skill": "", "text": ""}])
    skill_names = sorted(
        name for name, entry in mortal.get("skills", {}).items() if int(entry.get("dots", 0)) > 0
    )
    options = [""] + skill_names

    for index in range(2):
        st.markdown(f"**Specialty {index + 1}**")
        cols = st.columns([1, 2])
        current = specialties[index].get("skill", "")
        specialties[index]["skill"] = cols[0].selectbox(
            "Skill",
            options,
            index=options.index(current) if current in options else 0,
            key=f"spec_skill_{index}",
        )
        specialties[index]["text"] = cols[1].text_input(
            "Specialty",
            value=specialties[index].get("text", ""),
            placeholder="e.g. drugs, cars, trick shots",
            key=f"spec_text_{index}",
        )


def step_beliefs(character: dict[str, Any]) -> None:
    st.subheader("Beliefs & Relations")
    mortal = character.setdefault("mortal", {})
    mortal["beliefs"] = st.text_area(
        "Beliefs",
        value=mortal.get("beliefs", ""),
        placeholder="Closely-held beliefs about life, or general disposition…",
        height=120,
    )
    mortal["relations_and_resources"] = st.text_area(
        "Relations & resources",
        value=mortal.get("relations_and_resources", ""),
        placeholder="Important people, assets, debts…",
        height=120,
    )


def step_mortal_complete(character: dict[str, Any]) -> None:
    st.subheader("You have now created a human!")
    st.success("You have now created a human! Continue to the Embrace when ready.")

    attrs = character.get("mortal", {}).get("attributes", {})
    c1, c2, c3 = st.columns(3)
    c1.metric("Skill dots", total_skill_dots(character))
    c2.metric("Languages", len(character.get("mortal", {}).get("languages", [])))
    c3.metric("Top attribute", max(attrs, key=attrs.get) if attrs else "—")

    errors = validate_step(character, 8)
    if errors:
        st.warning("Some steps still need attention before this milestone is fully valid:")
        render_errors(errors)


STEP_RENDERERS = {
    1: step_chronicle,
    2: step_traits,
    3: step_attributes,
    4: step_skills,
    5: step_languages,
    6: step_specialties,
    7: step_beliefs,
    8: step_mortal_complete,
}


def render_step(character: dict[str, Any], step: int) -> None:
    renderer = STEP_RENDERERS.get(step)
    if renderer:
        renderer(character)
