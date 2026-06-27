from __future__ import annotations

from typing import Any

import streamlit as st

from pulse.constants import (
    ATTRIBUTE_DESCRIPTIONS,
    ATTRIBUTE_GROUPS,
    ATTRIBUTES,
    MORTAL_STEPS,
    POOL_BUDGETS,
    POOL_PROMPTS,
    SKILL_POOLS,
    TOTAL_SKILL_DOTS,
)
from pulse.data_loader import load_language_suggestions, load_skills, load_trait_suggestions, skill_category_map
from pulse.models import ensure_skill, recompute_skill_dots
from pulse.validation import pool_total, total_skill_dots, validate_step


def render_errors(errors: list[str]) -> None:
    for error in errors:
        st.error(error)


def _trait_suggestion_labels(suggestions: list[dict]) -> list[str]:
    return ["— custom —"] + [f"{s['name']} (+{s['plus']}/−{s['minus']})" for s in suggestions]


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
    chosen = suggestions[labels.index(pick) - 1]
    st.session_state[f"trait_name_{index}"] = chosen["name"]
    st.session_state[f"trait_plus_{index}"] = chosen["plus"]
    st.session_state[f"trait_minus_{index}"] = chosen["minus"]


def clear_trait_widget_state() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(("trait_pick_", "trait_name_", "trait_plus_", "trait_minus_")):
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
        if pick_key not in st.session_state:
            st.session_state[pick_key] = _trait_pick_label(traits[index], suggestions)
            _apply_trait_suggestion(index, suggestions, suggestion_labels)

        cols[0].selectbox(
            f"Suggestion##{index}",
            suggestion_labels,
            label_visibility="collapsed",
            key=pick_key,
            on_change=_apply_trait_suggestion,
            args=(index, suggestions, suggestion_labels),
        )

        traits[index]["name"] = cols[1].text_input(
            "Name",
            value=traits[index].get("name", ""),
            key=f"trait_name_{index}",
        )
        traits[index]["plus"] = cols[2].selectbox(
            "+1",
            ATTRIBUTES,
            index=ATTRIBUTES.index(traits[index].get("plus", ATTRIBUTES[0])),
            key=f"trait_plus_{index}",
        )
        traits[index]["minus"] = cols[3].selectbox(
            "−1",
            ATTRIBUTES,
            index=ATTRIBUTES.index(traits[index].get("minus", ATTRIBUTES[1])),
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


def _render_skill_pool_step(character: dict[str, Any], pool: str) -> None:
    label = pool.replace("_", " ").title()
    st.subheader(POOL_PROMPTS[pool].split(".")[0].replace("Add", label + " — add"))
    st.caption(POOL_PROMPTS[pool])
    budget = POOL_BUDGETS[pool]
    assigned = pool_total(character, pool)
    st.progress(min(assigned / budget, 1.0), text=f"{label}: {assigned} / {budget} dots")

    categories = skill_category_map()
    filter_cat = st.selectbox("Filter by category", ["All", "Physical", "Social", "Mental"], key=f"filter_{pool}")

    for skill in load_skills():
        if filter_cat != "All" and skill["category"] != filter_cat:
            continue
        entry = ensure_skill(character, skill["name"], skill["category"])
        current = int(entry["pools"].get(pool, 0))
        new_val = st.number_input(
            skill["name"],
            min_value=0,
            max_value=5,
            value=current,
            key=f"skill_{pool}_{skill['name']}",
        )
        entry["pools"][pool] = new_val
        recompute_skill_dots(entry)

    with st.expander("Add custom skill"):
        custom_name = st.text_input("Custom skill name", key=f"custom_name_{pool}")
        custom_cat = st.selectbox("Category", ["Physical", "Social", "Mental"], key=f"custom_cat_{pool}")
        custom_dots = st.number_input("Dots in this pool", min_value=0, max_value=5, value=0, key=f"custom_dots_{pool}")
        if custom_name.strip():
            entry = ensure_skill(character, custom_name.strip(), custom_cat, custom=True)
            entry["pools"][pool] = custom_dots
            recompute_skill_dots(entry)

    st.caption(f"Total skill dots so far: {total_skill_dots(character)} / {TOTAL_SKILL_DOTS}")


def step_professional_skills(character: dict[str, Any]) -> None:
    _render_skill_pool_step(character, "professional")


def step_life_event_skills(character: dict[str, Any]) -> None:
    _render_skill_pool_step(character, "life_event")


def step_leisure_skills(character: dict[str, Any]) -> None:
    _render_skill_pool_step(character, "leisure")


def step_natural_skills(character: dict[str, Any]) -> None:
    _render_skill_pool_step(character, "natural")


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

    errors = validate_step(character, 11)
    if errors:
        st.warning("Some steps still need attention before this milestone is fully valid:")
        render_errors(errors)


STEP_RENDERERS = {
    1: step_chronicle,
    2: step_traits,
    3: step_attributes,
    4: step_professional_skills,
    5: step_life_event_skills,
    6: step_leisure_skills,
    7: step_natural_skills,
    8: step_languages,
    9: step_specialties,
    10: step_beliefs,
    11: step_mortal_complete,
}


def render_step(character: dict[str, Any], step: int) -> None:
    renderer = STEP_RENDERERS.get(step)
    if renderer:
        renderer(character)
