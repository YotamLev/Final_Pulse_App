from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Any

from pulse.caps import get_attribute_values, get_skill_dots
from pulse.constants import ATTRIBUTE_GROUPS, INNATE_VAMPIRE_ABILITIES, SCHEMA_VERSION, SKILL_POOLS
from pulse.powers import power_by_id
from pulse.vampire import clan_by_id


def _esc(text: str) -> str:
    return html.escape(text)


def format_level_up_summary(entry: dict[str, Any]) -> str:
    """Human-readable summary of one level-up audit entry."""
    choice = entry.get("choice", "")
    details = entry.get("details") or {}
    if choice == "attr":
        attr = details.get("attribute", "?")
        dots = int(details.get("dots", 1))
        return f"+{dots} {attr}"
    if choice == "power":
        power = power_by_id(details.get("id", ""))
        if power:
            return f"Power: {power['name']} ({power['source']})"
        return f"Power: {details.get('id', '?')}"
    if choice == "skills":
        parts = [f"+{int(dots)} {skill}" for skill, dots in sorted(details.items()) if int(dots) > 0]
        return "Skills: " + ", ".join(parts) if parts else "Skills"
    if choice == "specialties":
        specs = details.get("specialties") or []
        parts = [
            f"{spec.get('skill', '?')} ({spec.get('text', '')})"
            for spec in specs
            if spec.get("skill") or spec.get("text")
        ]
        return "Specialties: " + "; ".join(parts) if parts else "Specialties"
    return str(choice or "—")


def format_level_up_log_html(level_ups: list[dict[str, Any]]) -> str:
    if not level_ups:
        return "<p><em>No level-ups recorded.</em></p>"
    rows = []
    for entry in level_ups:
        level = entry.get("to_level", "?")
        summary = format_level_up_summary(entry)
        rows.append(
            f"<tr><td>{_esc(str(level))}</td><td>{_esc(summary)}</td></tr>"
        )
    return (
        "<table class=\"level-up-log\">"
        "<tr><th>Level</th><th>Advancement</th></tr>"
        f"{''.join(rows)}</table>"
    )


def format_power_html(chosen: dict, power_def: dict | None = None) -> str:
    """Render one character power with full rulebook text for print/export."""
    if power_def is None and chosen.get("id"):
        power_def = power_by_id(chosen["id"])
    power_def = power_def or {}

    title = f"{chosen.get('name', '?')} ({chosen.get('source', '')})"
    if chosen.get("is_predator_power"):
        title += " — predator"

    chunks = [f'<div class="power-block"><h3>{_esc(title)}</h3>']
    for field in ("cost", "duration", "roll"):
        value = power_def.get(field)
        if value:
            chunks.append(f'<p class="power-mechanics">{_esc(str(value))}</p>')

    description = power_def.get("description_text") or power_def.get("summary") or ""
    if description:
        paragraphs = str(description).split("\n\n") if "\n\n" in str(description) else [str(description)]
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                chunks.append(f'<p class="power-text">{_esc(paragraph)}</p>')

    if chosen.get("is_predator_power") and power_def.get("predator_bonus_text"):
        chunks.append(f'<p class="power-predator">{_esc(str(power_def["predator_bonus_text"]))}</p>')

    prereq = power_def.get("prerequisites") or {}
    raw_prereq = prereq.get("raw") if isinstance(prereq, dict) else None
    if raw_prereq:
        chunks.append(f'<p class="power-prereq"><strong>Requirements:</strong> {_esc(str(raw_prereq))}</p>')

    chunks.append("</div>")
    return "".join(chunks)


def render_character_sheet(character: dict[str, Any]) -> str:
    mortal = character.get("mortal", {})
    attrs = get_attribute_values(character)
    traits = mortal.get("traits", [])
    skill_dots = get_skill_dots(character)
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
    for skill_name, dots in sorted(skill_dots.items()):
        if int(dots) <= 0:
            continue
        entry = mortal.get("skills", {}).get(skill_name, {})
        pools = entry.get("pools", {})
        pool_bits = ", ".join(f"{p[:4]}:{pools.get(p, 0)}" for p in SKILL_POOLS if pools.get(p, 0))
        skill_rows.append(
            f"<tr><td>{html.escape(skill_name)}</td><td>{dots}</td>"
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

    vampire = character.get("vampire")
    vampire_html = ""
    if vampire:
        clan = clan_by_id(vampire.get("clan", ""))
        clan_name = html.escape(clan["name"]) if clan else "—"
        power_blocks = "".join(
            format_power_html(p, power_by_id(p.get("id", "")))
            for p in vampire.get("powers", [])
        )
        disc_rows = "".join(
            f"<li>{html.escape(d['name'])} (acquired level {d['acquired_at_level']})</li>"
            for d in vampire.get("disciplines", [])
        )
        innate = "".join(f"<li>{html.escape(a)}</li>" for a in INNATE_VAMPIRE_ABILITIES)
        predator = vampire.get("predator") or {}
        pred_line = html.escape(predator.get("custom_name") or predator.get("type", "—"))
        level_up_log = format_level_up_log_html(vampire.get("level_ups", []))
        vampire_html = f"""
  <h2>Clan &amp; Bane</h2>
  <p><strong>Clan:</strong> {clan_name} · <strong>Level:</strong> {vampire.get('level', 0)}</p>
  <p>{html.escape(vampire.get('bane', {}).get('summary', '')[:500])}</p>
  <h2>Predator</h2>
  <p>{pred_line}</p>
  <h2>Disciplines</h2>
  <ul>{disc_rows or '<li>—</li>'}</ul>
  <h2>Powers</h2>
  {power_blocks or '<p><em>No powers</em></p>'}
  <h2>Level-up log</h2>
  {level_up_log}
  <h2>Innate abilities</h2>
  <ul>{innate}</ul>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{char_name} — Final Pulse</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 720px; margin: 2rem auto; color: #1a1010; background: #faf8f5; }}
    h1 {{ color: #8b1a1a; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.35rem 0.5rem; text-align: left; }}
    th {{ background: #f4f4f4; }}
    .meta {{ color: #555; font-size: 0.9rem; }}
    .power-block {{ margin: 1.25rem 0 1.75rem; padding-bottom: 1rem; border-bottom: 1px solid #ddd; }}
    .power-block h3 {{ color: #8b1a1a; margin-bottom: 0.5rem; font-size: 1.05rem; }}
    .power-mechanics {{ margin: 0.25rem 0; font-size: 0.95rem; }}
    .power-text {{ margin: 0.5rem 0; line-height: 1.45; }}
    .power-predator {{ margin: 0.5rem 0; font-style: italic; color: #5a3030; }}
    .power-prereq {{ margin: 0.5rem 0 0; font-size: 0.9rem; color: #444; }}
    .level-up-log {{ margin-bottom: 1.5rem; }}
    @media print {{
      body {{ margin: 0.5in; max-width: none; }}
      .power-block {{ page-break-inside: avoid; break-inside: avoid; }}
    }}
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
  {vampire_html}
  <p class="meta">Final Pulse · schema v{SCHEMA_VERSION}</p>
</body>
</html>"""
