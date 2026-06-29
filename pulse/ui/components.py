"""Reusable UI components for Final Pulse 2E."""

from __future__ import annotations

import streamlit as st

FILLED = "●"
EMPTY = "○"


def dots(current: int, maximum: int) -> str:
    """Return a Unicode dot string: filled dots then empty dots."""
    current = max(0, min(current, maximum))
    return FILLED * current + EMPTY * (maximum - current)


def render_tracker(label: str, current: int, maximum: int, key_prefix: str) -> int:
    """
    Render an HP/Willpower/Blood dot-tracker with + and - buttons.
    Returns the (possibly updated) current value.
    """
    col_label, col_dots, col_minus, col_plus = st.columns([2, 3, 1, 1])
    with col_label:
        st.markdown(f"**{label}**")
    with col_dots:
        if current >= 0:
            disp = dots(current, maximum)
        else:
            disp = f"{'●' * maximum}  **({current})**"
        st.markdown(f"<span style='font-size:1.3rem; letter-spacing:0.05em'>{disp}</span>", unsafe_allow_html=True)
    with col_minus:
        if st.button("−", key=f"{key_prefix}_minus"):
            current -= 1
    with col_plus:
        if st.button("+", key=f"{key_prefix}_plus"):
            current += 1
    return current


def render_blood_tracker(current: int, key_prefix: str) -> int:
    """Blood tracker — can go below 0."""
    col_label, col_dots, col_minus, col_plus = st.columns([2, 3, 1, 1])
    with col_label:
        st.markdown("**Blood**")
    with col_dots:
        if current > 0:
            disp = dots(current, 10)
        elif current == 0:
            disp = EMPTY * 10
        else:
            disp = f"{EMPTY * 10} **({current})**"
        st.markdown(f"<span style='font-size:1.3rem; letter-spacing:0.05em'>{disp}</span>", unsafe_allow_html=True)
    with col_minus:
        if st.button("−", key=f"{key_prefix}_minus"):
            current -= 1
    with col_plus:
        if st.button("+", key=f"{key_prefix}_plus"):
            current = min(10, current + 1)
    return current


def render_skill_row(
    skill_name: str,
    skill: dict,
    tree_name: str,
    own_dots_value: int,
    effective_level: int,
    xp_next: int,
    can_add: bool,
    can_remove: bool,
    on_add_key: str,
    on_remove_key: str,
    depth: int = 0,
) -> None:
    """
    Render one row of the skill tree table.
    Uses Streamlit columns. Caller must handle button presses via session_state flags.
    """
    indent = "　" * depth  # full-width space for visual indent
    max_d = skill["max_dots"]
    branch = skill.get("branches_from")

    # Dot display
    dot_str = dots(own_dots_value, max_d)

    col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
    with col1:
        label = f"{indent}**{skill_name}**"
        if branch:
            if isinstance(branch, list):
                parents = " *or* ".join(f"{p} {t}●" for p, t in branch)
                label += f"  <small style='color:#9a8f82'>branches from {parents}</small>"
            else:
                p, t = branch
                label += f"  <small style='color:#9a8f82'>branches from {p} {t}●</small>"
        st.markdown(label, unsafe_allow_html=True)
        st.caption(skill["description"])
    with col2:
        base = effective_level - own_dots_value
        if base > 0:
            display = f"{'●' * base} + {dot_str}  `/{max_d}`"
        else:
            display = f"{dot_str}  `/{max_d}`"
        st.markdown(display)
    with col3:
        st.caption(f"Next: {xp_next} XP" if can_add else "—")
    with col4:
        c1, c2 = st.columns(2)
        with c1:
            st.button("−", key=on_remove_key, disabled=not can_remove)
        with c2:
            st.button("+", key=on_add_key, disabled=not can_add)


def render_trait_pill(trait: dict, remove_key: str) -> None:
    """Render a single trait as a pill with a remove button."""
    cost = trait["cost"]
    sign = "+" if cost > 0 else ""
    detail = trait.get("detail") or trait.get("sub_choice") or ""
    label = f"{trait['name']} ({sign}{cost})"
    if detail:
        label += f" — *{detail}*"

    col1, col2 = st.columns([5, 1])
    with col1:
        color = "#4a1a28" if cost < 0 else "#1a3a28" if cost > 0 else "#2a2a3a"
        st.markdown(
            f"<div style='background:{color}; padding:0.3rem 0.7rem; border-radius:3px; "
            f"margin:0.2rem 0; font-size:0.95rem'>{label}</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.button("✕", key=remove_key)


def render_power_pill(power_name: str, disc_name: str) -> None:
    """Render an acquired discipline power as a small pill."""
    st.markdown(
        f"<span style='background:#2a1a30; padding:0.15rem 0.5rem; border-radius:2px; "
        f"font-size:0.85rem; margin:0.1rem; display:inline-block'>{power_name}</span>",
        unsafe_allow_html=True,
    )


def section_header(text: str) -> None:
    st.markdown(f"### {text}")
    st.markdown("<hr style='margin:0.3rem 0 1rem'>", unsafe_allow_html=True)


def info_box(text: str) -> None:
    st.markdown(
        f"<div style='background:rgba(20,12,18,0.7); border:1px solid #4a2030; "
        f"border-radius:3px; padding:0.6rem 1rem; margin:0.5rem 0; color:#c9bdb0'>{text}</div>",
        unsafe_allow_html=True,
    )
