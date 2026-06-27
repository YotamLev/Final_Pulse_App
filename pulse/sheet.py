from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Any

from pulse.constants import ATTRIBUTE_GROUPS, SCHEMA_VERSION, SKILL_POOLS


def render_character_sheet(character: dict[str, Any]) -> str:
    mortal = character.get("mortal", {})
    attrs = mortal.get("attributes", {})
    traits = mortal.get("traits", [])
    skills = mortal.get("skills", {})
    languages = mortal.get("languages", [])
    specialties = mortal.get("specialties", [])
    char_name = html.escape(character.get("character", {}).get("name", "") or "Unnamed")
    chronicle = html.escape(character.get("chronicle", {}).get("name", "") or "")
    time_place = html.escape(character.get("chronicle", {}).get("time_and_place", "") or "")
    exported = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    trait_rows = "".join(
        f"<tr><td>{html.escape(t.get('name', ''))}</td>"
        f"<td>+{html.escape(t.get('plus', ''))}</td>"
        f"<td>−{html.escape(t.get('minus', ''))}</td></tr>"
        for t in traits
    )

    attr_sections = []
    for group, names in ATTRIBUTE_GROUPS.items():
        rows = "".join(
            f"<tr><td>{html.escape(name)}</td><td>{attrs.get(name, '')}</td></tr>" for name in names
        )
        attr_sections.append(f"<h3>{group}</h3><table><tr><th>Attribute</th><th>Rating</th></tr>{rows}</table>")

    skill_rows = []
    for skill_name, entry in sorted(skills.items()):
        if int(entry.get("dots", 0)) <= 0:
            continue
        pools = entry.get("pools", {})
        pool_bits = ", ".join(f"{p[:4]}:{pools.get(p, 0)}" for p in SKILL_POOLS if pools.get(p, 0))
        skill_rows.append(
            f"<tr><td>{html.escape(skill_name)}</td><td>{entry.get('dots', 0)}</td>"
            f"<td>{html.escape(entry.get('category', ''))}</td><td>{html.escape(pool_bits)}</td></tr>"
        )
    skills_table = "".join(skill_rows) or "<tr><td colspan='4'><em>No skills</em></td></tr>"

    spec_items = "".join(
        f"<li>{html.escape(s.get('skill', ''))} ({html.escape(s.get('text', ''))})</li>" for s in specialties
    )
    lang_items = "".join(f"<li>{html.escape(str(lang))}</li>" for lang in languages)

    concept = character.get("concept", {})
    concept_bits = "<br>".join(
        html.escape(f"{key.title()}: {value}")
        for key, value in concept.items()
        if str(value).strip()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{char_name} — Final Pulse</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 720px; margin: 2rem auto; color: #111; }}
    h1, h2, h3 {{ font-family: "Segoe UI", sans-serif; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.35rem 0.5rem; text-align: left; }}
    th {{ background: #f4f4f4; }}
    .meta {{ color: #555; font-size: 0.9rem; }}
    @media print {{ body {{ margin: 0.5in; }} }}
  </style>
</head>
<body>
  <h1>{char_name}</h1>
  <p class="meta">Chronicle: {chronicle or "—"} · {time_place or "—"} · Exported {exported}</p>
  <h2>Concept</h2>
  <p>{concept_bits or "—"}</p>
  <h2>Attributes</h2>
  {''.join(attr_sections)}
  <h2>Traits</h2>
  <table><tr><th>Trait</th><th>+1</th><th>−1</th></tr>{trait_rows}</table>
  <h2>Skills</h2>
  <table><tr><th>Skill</th><th>Dots</th><th>Category</th><th>Pools</th></tr>{skills_table}</table>
  <h2>Languages</h2>
  <ul>{lang_items or "<li>—</li>"}</ul>
  <h2>Specialties</h2>
  <ul>{spec_items or "<li>—</li>"}</ul>
  <h2>Beliefs</h2>
  <p>{html.escape(mortal.get('beliefs', '') or '—')}</p>
  <h2>Relations &amp; Resources</h2>
  <p>{html.escape(mortal.get('relations_and_resources', '') or '—')}</p>
  <p class="meta">Final Pulse · schema v{SCHEMA_VERSION}</p>
</body>
</html>"""
