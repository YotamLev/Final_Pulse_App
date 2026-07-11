"""Browser-side persistence for the active character via localStorage."""

from __future__ import annotations

import json

import streamlit as st
from streamlit_local_storage import LocalStorage

from pulse.models.character import char_from_dict, char_to_dict, default_character

STORAGE_KEY = "fp_character"


def resolve_initial_character() -> dict:
    """Load the persisted character on first app entry, or return a blank one."""
    raw = LocalStorage().getItem(STORAGE_KEY)
    if raw:
        try:
            return char_from_dict(json.loads(raw))
        except (ValueError, TypeError):
            return default_character()
    return default_character()


def save_if_changed(char: dict) -> None:
    """Persist the character to localStorage, but only when it actually changed."""
    char_json = json.dumps(char_to_dict(char), sort_keys=True)
    if char_json == st.session_state.get("_last_saved_json"):
        return
    LocalStorage().setItem(STORAGE_KEY, char_json, key="fp_storage_save")
    st.session_state["_last_saved_json"] = char_json


def clear_storage() -> None:
    """Wipe any persisted character (used by the sidebar reset action)."""
    LocalStorage().deleteAll(key="fp_storage_clear")
    st.session_state.pop("_last_saved_json", None)
