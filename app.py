"""Final Pulse 2E — Vampire TTRPG Streamlit App."""

from __future__ import annotations

import json

import streamlit as st

from pulse.ui.theme import apply_theme, render_hero
from pulse.ui.wizard import render_wizard
from pulse.ui.character_sheet import render_character_sheet
from pulse.ui.struggle import render_struggle
from pulse.models.character import default_character

st.set_page_config(
    page_title="Final Pulse",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _init_state() -> None:
    if "character" not in st.session_state:
        st.session_state.character = default_character()
    if "nav" not in st.session_state:
        st.session_state.nav = "wizard"


def _sidebar(char: dict) -> str:
    st.sidebar.markdown(
        "<div style='text-align:center;padding:0.5rem 0 1rem'>"
        "<span style='font-family:Cinzel,serif;font-size:1.1rem;color:#c41e3a'>Final Pulse</span>"
        "<div style='color:#9a8f82;font-size:0.8rem;font-style:italic'>Second Edition</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    name = char.get("name") or "Unnamed"
    clan = char.get("clan") or "Clanless"
    st.sidebar.markdown(f"**{name}**  \n*{clan}*")
    st.sidebar.divider()

    nav = st.sidebar.radio(
        "Navigate",
        options=["wizard", "sheet", "struggle"],
        format_func=lambda x: {
            "wizard": "⚡ Character Wizard",
            "sheet": "📜 Character Sheet",
            "struggle": "♟ Struggle",
        }[x],
        index=["wizard", "sheet", "struggle"].index(st.session_state.nav),
        key="nav_radio",
        label_visibility="collapsed",
    )
    st.session_state.nav = nav

    # Stage links in sidebar when in wizard
    if nav == "wizard":
        from pulse.ui.wizard import STAGES
        st.sidebar.divider()
        st.sidebar.markdown("<small style='color:#9a8f82'>Wizard Stages</small>", unsafe_allow_html=True)
        for num, label in STAGES.items():
            icon = "●" if num == char["wizard_stage"] else ("✓" if num < char["wizard_stage"] else "○")
            if st.sidebar.button(f"{icon} {num}. {label}", key=f"sidebar_stage_{num}", use_container_width=True):
                char["wizard_stage"] = num
                st.rerun()

    st.sidebar.divider()

    # Quick reset
    with st.sidebar.expander("⚠ Reset Character"):
        st.warning("This will erase all character data.")
        if st.button("Reset to blank", key="reset_char"):
            st.session_state.character = default_character()
            st.session_state.nav = "wizard"
            st.rerun()

    return nav


def main() -> None:
    apply_theme()
    _init_state()

    char = st.session_state.character
    nav = _sidebar(char)

    render_hero()

    if nav == "wizard":
        render_wizard(char)
    elif nav == "sheet":
        render_character_sheet(char)
    elif nav == "struggle":
        render_struggle(char)


if __name__ == "__main__":
    main()
