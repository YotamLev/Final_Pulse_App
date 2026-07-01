"""Struggle Screen for Final Pulse 2E."""

from __future__ import annotations

import uuid

import streamlit as st

from pulse.ui.components import section_header, info_box, dots


# ── Card Events data ──────────────────────────────────────────────────────────

CARD_EVENTS: dict[str, dict] = {
    "Clubs": {
        "icon": "♣",
        "theme": "Conflict",
        "description": "Matters of conflict: territorial transgressions, rivalries, violence.",
        "examples": [
            "A rival vampire transgressed into another's territory",
            "You find a lead to a rival's herd",
            "A rival recently frenzied in the presence of others",
            "A mortal close to a vampire recently had a falling-out with them",
        ],
    },
    "Hearts": {
        "icon": "♥",
        "theme": "Passion",
        "description": "Matters of passion: events, opportunities, emotional currents.",
        "examples": [
            "A festival, holiday, or sports event brings lots of excited mortals",
            "A local movement is gaining momentum",
            "A capable mortal is available for recruitment",
            "A mortal you care about is in danger",
        ],
    },
    "Diamonds": {
        "icon": "♦",
        "theme": "Prudence",
        "description": "Matters of prudence: deals, resources, practical opportunities.",
        "examples": [
            "A vampire needs something you can provide (safe haven, feeding permission) — willing to do a small Boon",
            "A company went bankrupt; selling cheaply",
            "The local drug supply runs dry",
            "A mortal institution is vulnerable to infiltration",
        ],
    },
    "Spades": {
        "icon": "♠",
        "theme": "Whispers",
        "description": "Matters of whispers: secrets, hidden things, supernatural events.",
        "examples": [
            "An ancient and valuable item is discovered hiding in plain sight, but not freely available",
            "Vampire hunters are searching for targets",
            "A witch is active in the area",
            "You find an old Kindred Boon debt, if you can navigate Vampire politics subtly enough to purchase it",
        ],
    },
}

VALUE_TIERS: list[dict] = [
    {"icon": "♟", "label": "2 – 4",  "meaning": "Moderate opportunity"},
    {"icon": "♞", "label": "5 – 7",  "meaning": "Great opportunity"},
    {"icon": "♝", "label": "8 – 10", "meaning": "Rare opportunity"},
    {"icon": "♜", "label": "Jack",   "meaning": "Less risk than usual"},
    {"icon": "♛", "label": "Queen",  "meaning": "Can add another card (even another player's) for a great bonus"},
    {"icon": "♚", "label": "King",   "meaning": "Can add a dot to an asset"},
    {"icon": "🂡", "label": "Ace",    "meaning": "Can interrupt a rival's action"},
]

ASSET_TYPES = ["Institution", "Servants", "Object", "Haven", "Herd"]


# ── Main entry ────────────────────────────────────────────────────────────────

def render_struggle(char: dict) -> None:
    section_header("Struggle")
    info_box(
        "The Struggle screen tracks your Schemes and Assets during political conflict. "
        "Draw a card to see what the session brings."
    )

    tab_cards, tab_schemes, tab_assets, tab_graveyard, tab_rules = st.tabs(
        ["🃏 Card Events", "📋 Schemes", "🏛 Assets", "⚰ Graveyard", "📖 Rules"]
    )

    with tab_cards:
        _tab_card_events()
    with tab_schemes:
        _tab_schemes(char)
    with tab_assets:
        _tab_assets(char)
    with tab_graveyard:
        _tab_graveyard(char)
    with tab_rules:
        _tab_rules()


# ── Card Events ───────────────────────────────────────────────────────────────

def _tab_card_events() -> None:
    section_header("Card Events")
    info_box("Pick a suit, then pick a value tier to read the event.")

    suit_keys = list(CARD_EVENTS.keys())

    # ── Suit row ──────────────────────────────────────────────────────────────
    suit_cols = st.columns(len(suit_keys))
    for i, s in enumerate(suit_keys):
        ev = CARD_EVENTS[s]
        sel = st.session_state.get("card_suit_sel") == s
        with suit_cols[i]:
            if st.button(
                f"{ev['icon']}  {s}",
                key=f"suit_btn_{s}",
                type="primary" if sel else "secondary",
                use_container_width=True,
            ):
                st.session_state["card_suit_sel"] = s
                st.session_state.pop("card_tier_sel", None)
                st.rerun()

    suit_sel = st.session_state.get("card_suit_sel")

    # ── Card preview ──────────────────────────────────────────────────────────
    tier_sel_idx = st.session_state.get("card_tier_sel")
    tier = VALUE_TIERS[tier_sel_idx] if tier_sel_idx is not None else None

    if suit_sel:
        ev = CARD_EVENTS[suit_sel]
        suit_icon = ev["icon"]
        value_icon = tier["icon"] if tier else "?"
        value_label = tier["label"] if tier else "—"
        value_meaning = tier["meaning"] if tier else "Choose a value below"

        st.markdown(
            f"<div style='background:#1a0812;border:1px solid #5c1a28;border-radius:4px;"
            f"padding:1.2rem 1.5rem;margin:0.9rem 0'>"
            f"<div style='font-size:3rem;text-align:center;letter-spacing:0.15em'>"
            f"{suit_icon} <span style='color:#9a8f82'>{value_icon}</span></div>"
            f"<h3 style='color:#c41e3a;text-align:center;margin:0.3rem 0'>"
            f"{suit_sel} — {ev['theme']}</h3>"
            f"<p style='text-align:center;color:#9a8f82;font-style:italic'>"
            f"{value_label} &nbsp;·&nbsp; {value_meaning}</p>"
            f"<hr style='border-color:#4a2030'>"
            f"<p>{ev['description']}</p>"
            f"<ul>{''.join(f'<li>{e}</li>' for e in ev['examples'])}</ul>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='background:#0e080c;border:1px dashed #3d2030;border-radius:4px;"
            "padding:2rem;text-align:center;color:#5c4050;margin:0.9rem 0'>"
            "Pick a suit above</div>",
            unsafe_allow_html=True,
        )

    # ── Value tier row ────────────────────────────────────────────────────────
    tier_cols = st.columns(len(VALUE_TIERS))
    for i, t in enumerate(VALUE_TIERS):
        sel = tier_sel_idx == i
        with tier_cols[i]:
            if st.button(
                f"{t['icon']}\n{t['label']}",
                key=f"tier_btn_{i}",
                type="primary" if sel else "secondary",
                use_container_width=True,
                disabled=suit_sel is None,
            ):
                st.session_state["card_tier_sel"] = i
                st.rerun()


# ── Schemes ───────────────────────────────────────────────────────────────────

def _tab_schemes(char: dict) -> None:
    schemes = char.setdefault("struggle_schemes", [])
    active = [s for s in schemes if not s.get("in_graveyard", False)]
    graveyard = [s for s in schemes if s.get("in_graveyard", False)]

    section_header(f"Active Schemes ({len(active)})")

    with st.expander("➕ New Scheme"):
        _new_scheme_form(schemes)

    for i, scheme in enumerate(active):
        _render_scheme_card(schemes, scheme, i)

    if not active:
        st.caption("No active schemes.")


def _new_scheme_form(schemes: list) -> None:
    with st.form("new_scheme_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Scheme Name", placeholder="e.g., Infiltrate Police Department")
            dots_req = st.number_input("Dots Required", min_value=1, max_value=10, value=3)
        with col2:
            goal = st.text_input("Stated Goal", placeholder="e.g., Install a loyal informant")
            is_secret = st.checkbox("Secret (face-down)")
        notes = st.text_area("Notes", height=60)
        submitted = st.form_submit_button("Create Scheme")
        if submitted and name.strip():
            schemes.append({
                "id": str(uuid.uuid4()),
                "name": name.strip(),
                "goal": goal.strip(),
                "notes": notes.strip(),
                "dots_acquired": 0,
                "dots_required": int(dots_req),
                "is_secret": is_secret,
                "in_graveyard": False,
            })
            st.rerun()


def _render_scheme_card(schemes: list, scheme: dict, display_idx: int) -> None:
    sid = scheme["id"]
    acquired = scheme["dots_acquired"]
    required = scheme["dots_required"]
    progress = min(acquired, required)

    secret_badge = "🔒 SECRET" if scheme.get("is_secret") else ""
    st.markdown(
        f"<div style='background:#120810;border:1px solid #3d1828;border-radius:4px;padding:0.8rem 1rem;margin:0.4rem 0'>"
        f"<b>{scheme['name']}</b> {secret_badge}"
        f"<div style='color:#9a8f82;font-size:0.9rem'>{scheme['goal']}</div>"
        f"<div style='margin:0.3rem 0'>Progress: {dots(progress, required)} ({acquired}/{required} dots)</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if st.button("−dot", key=f"scheme_minus_{sid}") and acquired > 0:
            scheme["dots_acquired"] -= 1
            st.rerun()
    with col2:
        if st.button("+dot", key=f"scheme_plus_{sid}") and acquired < required:
            scheme["dots_acquired"] += 1
            st.rerun()
    with col3:
        toggle_label = "🔓 Reveal" if scheme.get("is_secret") else "🔒 Secret"
        if st.button(toggle_label, key=f"scheme_secret_{sid}"):
            scheme["is_secret"] = not scheme.get("is_secret", False)
            st.rerun()
    with col4:
        if st.button("Edit", key=f"scheme_edit_{sid}"):
            st.session_state[f"editing_scheme_{sid}"] = True
    with col5:
        if st.button("⚰ Bury", key=f"scheme_bury_{sid}"):
            scheme["in_graveyard"] = True
            st.rerun()
    with col6:
        if st.button("🗑 Delete", key=f"scheme_delete_{sid}"):
            schemes[:] = [s for s in schemes if s["id"] != sid]
            st.rerun()

    if st.session_state.get(f"editing_scheme_{sid}"):
        with st.form(f"edit_scheme_{sid}"):
            scheme["name"] = st.text_input("Name", value=scheme["name"])
            scheme["goal"] = st.text_input("Goal", value=scheme["goal"])
            scheme["notes"] = st.text_area("Notes", value=scheme.get("notes", ""), height=80)
            scheme["dots_required"] = st.number_input("Dots Required", min_value=1, value=scheme["dots_required"])
            if st.form_submit_button("Save"):
                st.session_state.pop(f"editing_scheme_{sid}", None)
                st.rerun()

    if scheme.get("notes"):
        st.caption(f"Notes: {scheme['notes']}")


# ── Assets ────────────────────────────────────────────────────────────────────

def _tab_assets(char: dict) -> None:
    assets = char.setdefault("struggle_assets", [])
    active = [a for a in assets if not a.get("in_graveyard", False)]

    section_header(f"Active Assets ({len(active)})")

    with st.expander("➕ New Asset"):
        _new_asset_form(assets)

    for asset in active:
        _render_asset_card(assets, asset)

    if not active:
        st.caption("No active assets.")


def _new_asset_form(assets: list) -> None:
    with st.form("new_asset_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Asset Name", placeholder="e.g., The Crimson Club")
            asset_type = st.selectbox("Type", ASSET_TYPES)
        with col2:
            asset_dots = st.number_input("Dots (1–5)", min_value=1, max_value=5, value=2)
            is_secret = st.checkbox("Secret")
        description = st.text_area("Description", height=60)
        submitted = st.form_submit_button("Create Asset")
        if submitted and name.strip():
            assets.append({
                "id": str(uuid.uuid4()),
                "name": name.strip(),
                "asset_type": asset_type,
                "description": description.strip(),
                "dots": int(asset_dots),
                "damage": 0,
                "is_bolstered": False,
                "bolster_note": "",
                "is_secret": is_secret,
                "in_graveyard": False,
            })
            st.rerun()


def _render_asset_card(assets: list, asset: dict) -> None:
    aid = asset["id"]
    effective_dots = asset["dots"] - asset.get("damage", 0)
    secret_badge = "🔒 SECRET" if asset.get("is_secret") else ""
    bolster_badge = "⬆ BOLSTERED" if asset.get("is_bolstered") else ""

    st.markdown(
        f"<div style='background:#080c12;border:1px solid #1a2838;border-radius:4px;padding:0.8rem 1rem;margin:0.4rem 0'>"
        f"<b>{asset['name']}</b> [{asset['asset_type']}] {secret_badge} {bolster_badge}"
        f"<div style='color:#9a8f82;font-size:0.9rem'>{asset.get('description', '')}</div>"
        f"<div style='margin:0.3rem 0'>"
        f"Dots: {dots(max(0,effective_dots), asset['dots'])} ({effective_dots}/{asset['dots']})"
        f"{' ⚠ Damaged' if asset.get('damage',0) > 0 else ''}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if st.button("💥 Damage", key=f"asset_dmg_{aid}"):
            asset["damage"] = min(asset["dots"], asset.get("damage", 0) + 1)
            if asset["damage"] >= asset["dots"]:
                st.warning(f"**{asset['name']}** is destroyed!")
            st.rerun()
    with col2:
        if st.button("🔧 Repair", key=f"asset_rep_{aid}") and asset.get("damage", 0) > 0:
            asset["damage"] = asset["damage"] - 1
            asset["is_bolstered"] = False
            st.rerun()
    with col3:
        boost_label = "⬆ Bolstered" if asset.get("is_bolstered") else "⬆ Bolster"
        if st.button(boost_label, key=f"asset_bolt_{aid}"):
            asset["is_bolstered"] = not asset.get("is_bolstered", False)
            st.rerun()
    with col4:
        toggle_label = "🔓 Reveal" if asset.get("is_secret") else "🔒 Secret"
        if st.button(toggle_label, key=f"asset_sec_{aid}"):
            asset["is_secret"] = not asset.get("is_secret", False)
            st.rerun()
    with col5:
        if st.button("⚰ Bury", key=f"asset_bury_{aid}"):
            asset["in_graveyard"] = True
            st.rerun()
    with col6:
        if st.button("🗑 Delete", key=f"asset_del_{aid}"):
            assets[:] = [a for a in assets if a["id"] != aid]
            st.rerun()


# ── Graveyard ─────────────────────────────────────────────────────────────────

def _tab_graveyard(char: dict) -> None:
    section_header("Graveyard")

    schemes = char.get("struggle_schemes", [])
    assets = char.get("struggle_assets", [])

    dead_schemes = [s for s in schemes if s.get("in_graveyard")]
    dead_assets = [a for a in assets if a.get("in_graveyard")]

    if not dead_schemes and not dead_assets:
        st.caption("Nothing in the graveyard yet.")
        return

    if dead_schemes:
        st.markdown("**Buried Schemes**")
        for scheme in dead_schemes:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"~~{scheme['name']}~~ — *{scheme['goal']}*")
            with col2:
                if st.button("↩ Restore", key=f"restore_scheme_{scheme['id']}"):
                    scheme["in_graveyard"] = False
                    st.rerun()

    if dead_assets:
        st.markdown("**Destroyed / Buried Assets**")
        for asset in dead_assets:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"~~{asset['name']}~~ [{asset['asset_type']}] — {asset['dots']}●")
            with col2:
                if st.button("↩ Restore", key=f"restore_asset_{asset['id']}"):
                    asset["in_graveyard"] = False
                    asset["damage"] = 0
                    st.rerun()


# ── Rules Reference ───────────────────────────────────────────────────────────

def _box(content: str, border_color: str = "#4a2030") -> None:
    st.markdown(
        f"<div style='background:#120810;border:1px solid {border_color};"
        f"border-radius:4px;padding:0.9rem 1.2rem;margin:0.5rem 0'>{content}</div>",
        unsafe_allow_html=True,
    )


def _tab_rules() -> None:
    section_header("Struggle Rules")

    # ── Turn Overview ─────────────────────────────────────────────────────────
    st.markdown("#### Each Turn")
    _box(
        "<ol style='margin:0;padding-left:1.4rem;line-height:2'>"
        "<li><b>Draw a card.</b> If you now hold more than 3, discard down to 3.</li>"
        "<li><b>Scheme action</b> (choose one): <em>Start a new scheme</em> or <em>Advance an existing scheme</em>.</li>"
        "<li><b>Direct action</b> (choose one): <em>Bolster</em>, <em>Investigate</em>, <em>Attack</em>, or <em>Feed</em>.</li>"
        "</ol>",
        border_color="#5c2a1a",
    )

    # ── Assets ────────────────────────────────────────────────────────────────
    st.markdown("#### Assets")
    st.markdown(
        "Each side starts with their assets. Assets range from **1 to 5 dots** and fall into one of six types:"
    )
    col1, col2, col3 = st.columns(3)
    for col, label in zip([col1, col2, col1, col2, col3, col3],
                           ["🏛 Institutions", "👤 Servants", "📦 Objects",
                            "📜 Debts", "🏠 Haven", "🐑 Herd"]):
        with col:
            st.markdown(f"- {label}")

    st.divider()

    # ── Schemes ───────────────────────────────────────────────────────────────
    st.markdown("#### Schemes")
    st.markdown(
        "Schemes are represented as pieces of paper. "
        "A **secret scheme** is placed face-down (harder to advance). "
        "Other players may contribute to your schemes."
    )

    with st.expander("Creating or Reforming an Asset"):
        st.markdown(
            "Place red tokens on the scheme to track progress. "
            "The Storyteller sets the number of **required tasks** based on the desired asset size and control. "
            "Tasks can be assigned to different domains."
        )
        st.markdown(
            "When enough tokens are placed, the scheme resolves and the asset enters play. "
            "Dot value reflects size and control — agree with the Storyteller before starting."
        )
        _box(
            "<em>Example: A vampire wants to create a 'cult of the faithful' — medium size, strong control, "
            "roughly 6 families. The Storyteller rules this a 2-dot Institution and requires 3 tasks: "
            "1 for recruitment, 2 for incentive / dogma / resources.</em>",
            border_color="#2a3a1a",
        )

    with st.expander("Schemes Against a Rival Asset"):
        st.markdown(
            "Describe the plan and the desired damage. The Storyteller sets the number of tasks. "
            "As the scheme advances, **cards** equal to the desired damage are placed on it. "
            "When complete, those cards slide under the target asset — damaging it. "
            "A small scheme can be a single card."
        )
        st.markdown(
            "A **Trap** is a secret scheme that, when triggered, joins a battle as though it were an asset."
        )

    with st.expander("Advancing a Scheme"):
        st.markdown(
            "Spend your scheme action to define a task and roll against a difficulty. "
            "Success places a red token. Once the required number of tokens is reached, the scheme resolves."
        )

    st.divider()

    # ── Direct Actions ────────────────────────────────────────────────────────
    st.markdown("#### Direct Actions")

    with st.expander("⬆ Bolster an Asset"):
        st.markdown(
            "Grant a temporary advantage to one asset — extra weapons, a surge of cash, etc. "
            "The bonus lasts until that asset's **next roll**. "
            "Bolstering can also **repair one point of damage**. "
            "For a *permanent* improvement, start a scheme to reform the asset instead."
        )

    with st.expander("🔍 Investigate a Rival"):
        st.markdown("Roll to **reveal a hidden (face-down) scheme**.")

    with st.expander("⚔ Attack a Rival Asset"):
        st.markdown(
            "The only way to **destroy** an asset. Attacks can be Mental, Social, Physical, or a combination — "
            "and must be described concretely. "
            "You use a **primary asset** to lead the attack, and may add supporting assets if relevant. "
            "Adding irrelevant assets gives diminishing returns. Attacking alone is possible but dangerous."
        )
        _box(
            "<b>Mental:</b> tipping off police, lawsuits, covert money siphoning<br>"
            "<b>Social:</b> persuading people to quit or boycott, bribing guards<br>"
            "<b>Physical:</b> showing up and blowing it up",
            border_color="#1a2838",
        )
        st.markdown("The defender may add assets under the same relevance rules.")

    with st.expander("🩸 Feed"):
        st.markdown("Seek out prey to replenish Blood.")

    st.divider()

    # ── Combat Resolution ─────────────────────────────────────────────────────
    st.markdown("#### Combat Resolution (Attacking an Asset)")
    _box(
        "<ol style='margin:0;padding-left:1.4rem;line-height:2.1'>"
        "<li>Each side sums: <b>main asset dots</b> + helper asset bonuses + bolstering − damage cards already on the asset.</li>"
        "<li>Both sides roll.</li>"
        "<li>The <b>margin</b> of the winning roll is inflicted as damage on the loser's primary asset.</li>"
        "<li>Remaining damage spills to other assets that participated, in order.</li>"
        "<li>An asset is <b>destroyed</b> when its damage equals its dots.</li>"
        "</ol>",
        border_color="#5c1a28",
    )
