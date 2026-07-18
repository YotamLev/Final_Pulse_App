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


# components.v1.html can't auto-size to its content (that needs the full
# component JS API, not the plain html() helper), so this is a fixed height
# sized to the doc's content at typical embed widths (~900px wide ->
# ~24.7K px tall). scrolling=True is a fallback for narrower widths, where
# more text wrapping makes the content taller than this. Bump this if the
# rules doc grows enough to need the fallback scrollbar regularly.
RULES_FRAME_HEIGHT = 24900


def render_rules_page() -> None:
    components.html(_load_rules_html(), height=RULES_FRAME_HEIGHT, scrolling=True)
