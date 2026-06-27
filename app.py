from __future__ import annotations

from typing import Any

import streamlit as st

from pulse.constants import MORTAL_STEP_COUNT, WIZARD_STEP_COUNT, WIZARD_STEPS
from pulse.models import character_from_json, character_to_json, export_filename, new_character
from pulse.sheet import render_character_sheet
from pulse.ui.mortal_steps import clear_skill_widget_state, clear_trait_widget_state, render_step as render_mortal_step
from pulse.ui.theme import apply_theme, render_hero, render_step_badge
from pulse.ui.vampire_steps import render_vampire_step
from pulse.vampire_validation import validate_wizard_step


st.set_page_config(
    page_title="Final Pulse — Character Creation",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session() -> None:
    if "character" not in st.session_state:
        st.session_state.character = new_character()


def render_errors(errors: list[str]) -> None:
    for error in errors:
        st.error(error)


def render_sidebar(character: dict[str, Any]) -> None:
    st.sidebar.markdown("### The Chronicle")
    st.sidebar.caption("World of Darkness · Final Pulse")

    step = int(character.get("wizard_step", 1))
    for num in range(1, WIZARD_STEP_COUNT + 1):
        label = WIZARD_STEPS.get(num, "")
        if num < step:
            st.sidebar.markdown(f"<span style='color:#8b5a5a'>✓ {num}. {label}</span>", unsafe_allow_html=True)
        elif num == step:
            st.sidebar.markdown(f"**<span style='color:#c41e3a'>→ {num}. {label}</span>**", unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"<span style='color:#5a4a50'>○ {num}. {label}</span>", unsafe_allow_html=True)

    st.sidebar.divider()
    if st.sidebar.button("New character", use_container_width=True):
        clear_trait_widget_state()
        clear_skill_widget_state()
        st.session_state.character = new_character()
        st.rerun()

    uploaded = st.sidebar.file_uploader("Load character JSON", type=["json"])
    if uploaded is not None:
        try:
            clear_trait_widget_state()
            clear_skill_widget_state()
            st.session_state.character = character_from_json(uploaded.getvalue().decode("utf-8"))
            st.sidebar.success("Character loaded.")
            st.rerun()
        except Exception as exc:
            st.sidebar.error(f"Could not load: {exc}")

    st.sidebar.download_button(
        "Save JSON",
        data=character_to_json(character),
        file_name=export_filename(character),
        mime="application/json",
        use_container_width=True,
    )
    st.sidebar.download_button(
        "Download HTML sheet",
        data=render_character_sheet(character),
        file_name=export_filename(character).replace(".json", ".html"),
        mime="text/html",
        use_container_width=True,
    )


def render_step(character: dict[str, Any], step: int) -> None:
    if step <= MORTAL_STEP_COUNT:
        render_mortal_step(character, step)
    else:
        render_vampire_step(character, step)


def main() -> None:
    apply_theme()
    init_session()
    character: dict[str, Any] = st.session_state.character
    step = int(character.get("wizard_step", 1))

    render_sidebar(character)

    render_hero()
    render_step_badge(step, WIZARD_STEPS.get(step, ""))

    render_step(character, step)

    errors = validate_wizard_step(character, step)
    if errors and step != WIZARD_STEP_COUNT:
        st.divider()
        render_errors(errors)

    col_prev, col_next, _ = st.columns([1, 1, 4])
    with col_prev:
        if step > 1 and st.button("← Back", use_container_width=True):
            character["wizard_step"] = step - 1
            st.rerun()
    with col_next:
        if step < WIZARD_STEP_COUNT:
            if st.button("Next →", type="primary", use_container_width=True):
                if not errors:
                    character["wizard_step"] = step + 1
                    st.rerun()


if __name__ == "__main__":
    main()
