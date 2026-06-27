from __future__ import annotations

from typing import Any

import streamlit as st

from pulse.constants import MORTAL_STEPS, MORTAL_STEP_COUNT
from pulse.models import character_from_json, character_to_json, export_filename, new_character
from pulse.sheet import render_character_sheet
from pulse.ui.mortal_steps import render_step
from pulse.validation import validate_step

st.set_page_config(page_title="Final Pulse — Character Creation", page_icon="🩸", layout="wide")


def init_session() -> None:
    if "character" not in st.session_state:
        st.session_state.character = new_character()


def render_sidebar(character: dict[str, Any]) -> None:
    st.sidebar.title("Final Pulse")
    st.sidebar.caption("Character creation")

    step = character.get("wizard_step", 1)
    st.sidebar.markdown("**Progress**")
    for num, label in MORTAL_STEPS.items():
        if num < step:
            st.sidebar.markdown(f"✓ {num}. {label}")
        elif num == step:
            st.sidebar.markdown(f"**→ {num}. {label}**")
        else:
            st.sidebar.markdown(f"○ {num}. {label}")

    st.sidebar.divider()
    if st.sidebar.button("New character", use_container_width=True):
        st.session_state.character = new_character()
        st.rerun()

    uploaded = st.sidebar.file_uploader("Load character JSON", type=["json"])
    if uploaded is not None:
        try:
            st.session_state.character = character_from_json(uploaded.getvalue().decode("utf-8"))
            st.sidebar.success("Character loaded.")
            st.rerun()
        except Exception as exc:
            st.sidebar.error(f"Could not load file: {exc}")

    st.sidebar.download_button(
        "Save JSON",
        data=character_to_json(character),
        file_name=export_filename(character),
        mime="application/json",
        use_container_width=True,
    )

    html_sheet = render_character_sheet(character)
    st.sidebar.download_button(
        "Download HTML sheet",
        data=html_sheet,
        file_name=export_filename(character).replace(".json", ".html"),
        mime="text/html",
        use_container_width=True,
    )


def main() -> None:
    init_session()
    character: dict[str, Any] = st.session_state.character
    step = int(character.get("wizard_step", 1))

    render_sidebar(character)

    st.title("Character Creation")
    st.caption(f"Step {step} of {MORTAL_STEP_COUNT} — {MORTAL_STEPS.get(step, '')}")

    render_step(character, step)

    errors = validate_step(character, step)
    if errors and step != 11:
        st.divider()
        render_errors(errors)

    col_prev, col_next, _ = st.columns([1, 1, 4])
    with col_prev:
        if step > 1 and st.button("← Back", use_container_width=True):
            character["wizard_step"] = step - 1
            st.rerun()
    with col_next:
        if step < MORTAL_STEP_COUNT:
            if st.button("Next →", type="primary", use_container_width=True):
                if not errors:
                    character["wizard_step"] = step + 1
                    st.rerun()
        elif step == MORTAL_STEP_COUNT:
            st.info("Vampire creation (Embrace & Level 0) will continue here in the next release.")


def render_errors(errors: list[str]) -> None:
    for error in errors:
        st.error(error)


if __name__ == "__main__":
    main()
