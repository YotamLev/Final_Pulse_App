from __future__ import annotations

import streamlit as st

from pulse.ui.theme import apply_theme, render_hero

st.set_page_config(
    page_title="Final Pulse",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    apply_theme()
    render_hero()

    st.info("App overhaul in progress.")


if __name__ == "__main__":
    main()
