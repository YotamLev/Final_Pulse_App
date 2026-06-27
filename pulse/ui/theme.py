"""Masquerade-inspired dark gothic theme for Streamlit."""

from __future__ import annotations

import streamlit as st

# Palette: deep black, blood crimson, parchment text, neo-noir purple undertones
# Inspired by VTMB / Bloodlines dark UI (black canvases, crimson accents)

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Crimson Pro', Georgia, serif;
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Cinzel', 'Times New Roman', serif !important;
    color: #e8ddd0 !important;
    letter-spacing: 0.04em;
}

.stApp {
    background: linear-gradient(165deg, #08080a 0%, #12101a 35%, #1a0a10 70%, #0a0808 100%);
    color: #d4c8b8;
}

.stApp header[data-testid="stHeader"] {
    background: rgba(8, 8, 10, 0.92);
    border-bottom: 1px solid #4a1520;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c0a0e 0%, #140c12 100%);
    border-right: 1px solid #5c1a28;
}

section[data-testid="stSidebar"] .stMarkdown {
    color: #c9bdb0;
}

.pulse-hero {
    text-align: center;
    padding: 0.5rem 0 1.5rem;
    border-bottom: 1px solid #5c1a28;
    margin-bottom: 1.5rem;
}

.pulse-hero h1 {
    font-size: 2.2rem !important;
    color: #c41e3a !important;
    text-shadow: 0 0 24px rgba(196, 30, 58, 0.35);
    margin-bottom: 0.2rem !important;
}

.pulse-hero .subtitle {
    font-family: 'Crimson Pro', serif;
    color: #9a8f82;
    font-style: italic;
    font-size: 1.05rem;
}

.pulse-step-badge {
    display: inline-block;
    background: linear-gradient(135deg, #3d1018, #6b1c2a);
    color: #f0e6d8;
    padding: 0.25rem 0.85rem;
    border-radius: 2px;
    font-family: 'Cinzel', serif;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 1px solid #8b2940;
    margin-bottom: 0.75rem;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #9b1c2e 0%, #6b1420 100%) !important;
    border: 1px solid #c41e3a !important;
    color: #fff8f0 !important;
    font-family: 'Cinzel', serif !important;
    letter-spacing: 0.06em;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #b82238 0%, #8b1c2a 100%) !important;
    box-shadow: 0 0 16px rgba(196, 30, 58, 0.45);
}

.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #5c4050 !important;
    color: #d4c8b8 !important;
}

div[data-testid="stMetric"] {
    background: rgba(20, 12, 18, 0.85);
    border: 1px solid #4a2030;
    border-radius: 4px;
    padding: 0.5rem;
}

div[data-testid="stMetric"] label {
    color: #9a8f82 !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #e8ddd0 !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #6b1420, #c41e3a) !important;
}

.stExpander {
    border: 1px solid #3d2830 !important;
    background: rgba(12, 10, 14, 0.6) !important;
}

hr {
    border-color: #4a2030 !important;
}

.stAlert {
    border-radius: 2px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 1px solid #4a2030;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Cinzel', serif;
    color: #9a8f82;
    letter-spacing: 0.04em;
}

.stTabs [aria-selected="true"] {
    color: #c41e3a !important;
    border-bottom-color: #c41e3a !important;
}

[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    color: #c9bdb0 !important;
}

.stInfo, .stSuccess {
    background: rgba(20, 12, 18, 0.75) !important;
    border: 1px solid #4a2030 !important;
    color: #d4c8b8 !important;
}
</style>
"""


def apply_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_hero(title: str = "Final Pulse", subtitle: str = "Character Creation — World of Darkness") -> None:
    st.markdown(
        f'<div class="pulse-hero"><h1>{title}</h1><div class="subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def render_step_badge(step: int, label: str) -> None:
    st.markdown(f'<div class="pulse-step-badge">Step {step} — {label}</div>', unsafe_allow_html=True)
