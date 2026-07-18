"""Rules tab — embeds the generated character-building rules doc in the app."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

RULES_HTML_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "Instructions"
    / "Final Pulse 2E - Character Building Rules.html"
)


@st.cache_data
def _load_rules_html() -> str:
    return RULES_HTML_PATH.read_text(encoding="utf-8")


def render_rules_page() -> None:
    components.html(_load_rules_html(), height=900, scrolling=True)
