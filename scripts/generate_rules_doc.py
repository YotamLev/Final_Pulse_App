"""Regenerate Instructions/Final Pulse 2E - Character Building Rules.html from the live data files.

Run whenever pulse/data/traits.py, skill_trees.py, disciplines.py, or clans.py change:

    python scripts/generate_rules_doc.py

The doc's Traits, Skill Trees, Discipline Trees, and Clans sections are fully derived
from those modules (including Discipline/Clan symbol images, embedded as base64 so the
file stays self-contained). The surrounding prose (Overview, XP cost explanations,
Default Vampire Powers) is static and only needs hand-editing if those rules change.
"""
from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pulse.data.traits import MORTAL_TRAITS, VAMPIRE_TRAITS
from pulse.data.skill_trees import SKILL_TREES
from pulse.data.disciplines import DISCIPLINES, DISC_SHORT_DESC
from pulse.data.clans import CLANS

OUTPUT_PATH = REPO_ROOT / "Instructions" / "Final Pulse 2E - Character Building Rules.html"

MORTAL_CATEGORIES = [
    ("personality", "Personality"),
    ("mental", "Mental"),
    ("body", "Body"),
    ("sensory", "Sensory"),
    ("other", "Other"),
]

TRAIT_NAME = {t["key"]: t["name"] for t in MORTAL_TRAITS + VAMPIRE_TRAITS}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def icon_data_uri(rel_path: str) -> str:
    full = REPO_ROOT / rel_path.replace("/", "\\")
    b = full.read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


def icon_html(rel_path: str, size: int = 56) -> str:
    return (
        f"<span class='icon-box' style='width:{size}px;height:{size}px'>"
        f"<img src='{icon_data_uri(rel_path)}' alt=''/></span>"
    )


def cost_str(t: dict) -> str:
    if t.get("variable_cost"):
        opts = t["cost_options"]
        lo = min(o[0] for o in opts)
        hi = max(o[0] for o in opts)
        return f"{lo} to {hi}"
    c = t["cost"]
    sign = "+" if c >= 0 else ""
    return f"{sign}{c}"


def trait_rows(traits: list[dict], with_category: bool = False) -> str:
    rows = []
    for t in traits:
        desc = esc(t["description"])
        if t.get("variable_cost"):
            desc += "<br><small>" + "; ".join(f"{o[0]:+d}: {esc(o[1])}" for o in t["cost_options"]) + "</small>"
        if t.get("requires_sub_choice"):
            desc += "<br><small>Choose one: " + ", ".join(esc(o) for o in t["sub_options"]) + "</small>"
        maxt = t.get("max_times", 1)
        extra = f" <span class='tag'>up to {maxt}x</span>" if maxt > 1 else ""
        cat_attr = f" data-cat='{t.get('category', 'other')}'" if with_category else ""
        rows.append(f"<tr{cat_attr}><td><b>{esc(t['name'])}</b>{extra}</td><td>{cost_str(t)}</td><td>{desc}</td></tr>")
    return "\n".join(rows)


def build_skill_tree(skills: dict[str, dict]) -> str:
    children: dict[str, list[str]] = {name: [] for name in skills}
    roots = []
    for name, s in skills.items():
        branch = s.get("branches_from")
        if branch is None:
            roots.append(name)
        elif s.get("branches_or"):
            parent = branch[0][0]
            children.setdefault(parent, []).append(name)
        else:
            parent = branch[0]
            children.setdefault(parent, []).append(name)

    def branch_note(s: dict) -> str:
        branch = s.get("branches_from")
        if branch is None:
            return ""
        if s.get("branches_or"):
            parts = " or ".join(f"{p} {th} dots" for p, th in branch)
            return f"<span class='tag'>branches from {parts}</span>"
        parent, th = branch
        return f"<span class='tag'>branches from {parent} {th} dots</span>"

    def render(name: str) -> str:
        s = skills[name]
        note = branch_note(s)
        html = f"<li><b>{esc(name)}</b> <span class='tag'>up to {s['max_dots']} dots</span> {note}<br><small>{esc(s['description'])}</small>"
        kids = children.get(name, [])
        if kids:
            html += "<ul>" + "".join(render(k) for k in kids) + "</ul>"
        html += "</li>"
        return html

    return "<ul>" + "".join(render(r) for r in roots) + "</ul>"


def skill_tree_sections() -> str:
    out = []
    for tree_name, skills in SKILL_TREES.items():
        out.append(f"<h3>{esc(tree_name)}</h3>")
        out.append(build_skill_tree(skills))
    return "\n".join(out)


def discipline_sections() -> str:
    out = []
    for disc_name, data in DISCIPLINES.items():
        short = DISC_SHORT_DESC.get(disc_name, "")
        out.append(f"<div class='disc-block' data-disc=\"{esc(disc_name)}\">")
        out.append(f"<h3 class='with-icon'>{icon_html(data['image'])}{esc(disc_name)}</h3>")
        out.append(f"<p class='desc'>{esc(short)}</p>")
        by_level: dict[int, list[dict]] = {}
        for p in data["powers"]:
            by_level.setdefault(p["level"], []).append(p)
        out.append("<ul>")
        for lvl in sorted(by_level):
            out.append(f"<li><i>Level {lvl}</i><ul>")
            for p in by_level[lvl]:
                req = f" <span class='tag req'>requires {esc(p['requires'])}</span>" if p["requires"] else ""
                out.append(f"<li><b>{esc(p['name'])}</b>{req}<br><small>{esc(p['description'])}</small></li>")
            out.append("</ul></li>")
        out.append("</ul>")
        out.append("</div>")
    return "\n".join(out)


def req_text(reqs: dict) -> str:
    parts = []
    if reqs.get("trait_any_malkavian"):
        parts.append(
            "At least one qualifying mental-illness Trait (Paranoid, Dissociative Episodes, "
            "Depressive Episodes, Manic Episodes, Psychotic Episodes, Panic Disorder, "
            "Post-Traumatic Stress, Delusional Belief, or Selective Mutism), from before or "
            "caused by the Embrace"
        )
    if "trait_any" in reqs:
        names = [TRAIT_NAME.get(k, k) for k in reqs["trait_any"]]
        parts.append("Trait: " + " or ".join(names))
    if "discipline_all" in reqs:
        parts.append("Discipline: " + " and ".join(reqs["discipline_all"]))
    if "discipline_any" in reqs:
        parts.append("Discipline: " + " or ".join(reqs["discipline_any"]))
    return "; ".join(parts)


def clan_sections() -> str:
    out = []
    for name, c in CLANS.items():
        out.append("<div class='clan-card'>")
        out.append(f"<h3 class='with-icon'>{icon_html(c['image'])}{esc(name)}</h3>")
        out.append(f"<p><i>{esc(c['description'])}</i></p>")
        out.append(f"<p><strong>Recruitment:</strong> {esc(c['recruitment'])}</p>")
        out.append(f"<p><strong>Requirements:</strong> {req_text(c['requirements'])}</p>")
        out.append(f"<p><strong>Bonus:</strong> {esc(c['bonus'])}</p>")
        out.append(f"<p><strong>Suggested Disciplines:</strong> {', '.join(c['suggested_disciplines'])}</p>")
        out.append("</div>")
    return "\n".join(out)


def mortal_category_options() -> str:
    return "\n".join(f"<option value='{k}'>{esc(l)}</option>" for k, l in MORTAL_CATEGORIES)


def discipline_options() -> str:
    return "\n".join(f"<option value=\"{esc(n)}\">{esc(n)}</option>" for n in DISCIPLINES)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Final Pulse 2E — Character Building Rules</title>
<style>
  body {{ font-family: Georgia, serif; background: #0a080c; color: #e8ddd0; margin: 2rem auto; max-width: 900px; line-height: 1.5; }}
  h1 {{ color: #c41e3a; font-family: 'Times New Roman', serif; font-size: 2.2rem; margin-bottom: 0.2rem; }}
  h2 {{ color: #c41e3a; font-size: 1.4rem; border-bottom: 1px solid #4a2030; padding-bottom: 0.3rem; margin-top: 2.5rem; }}
  h3 {{ color: #d4c8b8; font-size: 1.1rem; margin-bottom: 0.2rem; }}
  h3.with-icon {{ display: flex; align-items: center; gap: 0.6rem; }}
  h4 {{ color: #c9bdb0; font-size: 0.95rem; margin: 0.8rem 0 0.2rem; }}
  p.subtitle {{ color: #9a8f82; margin-top: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
  th, td {{ padding: 0.4rem 0.8rem; border: 1px solid #4a2030; text-align: left; vertical-align: top; }}
  th {{ background: #1a0a12; color: #c9bdb0; }}
  small, .desc {{ color: #9a8f82; }}
  ul {{ margin: 0.3rem 0; padding-left: 1.3rem; }}
  li {{ margin: 0.15rem 0; }}
  .section {{ background: #12101a; border: 1px solid #3d2830; border-radius: 4px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem; }}
  .toc {{ columns: 2; }}
  .toc a {{ color: #e8ddd0; text-decoration: none; }}
  .toc a:hover {{ color: #c41e3a; }}
  .tag {{ display: inline-block; font-size: 0.75rem; color: #c9bdb0; background: #1a0a12; border: 1px solid #4a2030; border-radius: 3px; padding: 0.05rem 0.4rem; margin-left: 0.4rem; }}
  .req {{ color: #c41e3a; }}
  .clan-card {{ border: 1px solid #3d2830; border-radius: 4px; padding: 0.8rem 1rem; margin-bottom: 1rem; }}
  code {{ background: #1a0a12; padding: 0.05rem 0.3rem; border-radius: 3px; }}
  .icon-box {{ display: inline-flex; align-items: center; justify-content: center; flex: none; }}
  .icon-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
  .filter-bar {{ margin-bottom: 1rem; }}
  .filter-bar label {{ color: #9a8f82; font-size: 0.85rem; margin-right: 0.5rem; }}
  .filter-bar select {{ background: #1a0a12; color: #e8ddd0; border: 1px solid #4a2030; padding: 0.35rem 0.6rem; border-radius: 4px; font-family: inherit; font-size: 0.9rem; }}
  @media print {{ body {{ background: white; color: black; }} .section {{ border: 1px solid #ccc; }} }}
</style>
</head>
<body>

<h1>Final Pulse 2E</h1>
<p class="subtitle">Character Building Rules — generated from the live app's data files</p>

<div class="section toc">
  <a href="#overview">Overview &amp; Creation Order</a>
  <a href="#xp">Experience Points</a>
  <a href="#traits">Traits</a>
  <a href="#skills">Skill Trees</a>
  <a href="#disciplines">Discipline Trees</a>
  <a href="#clans">Clans</a>
  <a href="#powers">Default Vampire Powers</a>
  <a href="#rolls">Rolls</a>
</div>

<div class="section" id="overview">
<h2>Overview &amp; Creation Order</h2>
<p>A character is built in four stages:</p>
<ol>
  <li><strong>Traits</strong> — choose Mortal and Vampire Traits (optional).</li>
  <li><strong>Skills</strong> — spend 15 XP across the Skill Trees.</li>
  <li><strong>Disciplines</strong> — unlock up to 3 Disciplines, then spend 10 XP raising their levels.</li>
  <li><strong>Clan</strong> — optional; join the one Clan (if any) whose requirements your Traits and Disciplines satisfy.</li>
</ol>
</div>

<div class="section" id="xp">
<h2>Experience Points</h2>
<p>Skill XP and Discipline XP are separate pools and cannot be mixed:</p>
<ul>
  <li><strong>Creation Skill XP:</strong> 15, spent only on Skills.</li>
  <li><strong>Creation Discipline XP:</strong> 10, spent only on Disciplines.</li>
</ul>
<p>After creation, the Storyteller awards <strong>Earned XP</strong>, which may be spent on either pool once its creation allotment is exhausted.</p>
<h4>Skill cost</h4>
<p>Each dot you personally invest in a skill costs XP equal to the <em>effective level it brings the skill to</em> — that is, its static base (dots inherited from a parent skill at the branch point, see below) plus the dot number you're buying. So the 1st own dot costs <code>base + 1</code>, the 2nd costs <code>base + 2</code>, and so on. A skill with no parent (base 0) costs 1 XP for its 1st dot, 2 for its 2nd, etc. — the classic <code>1, 2, 3, 4, 5</code> XP curve. Custom skills always have base 0.</p>
<h4>Discipline cost</h4>
<p>Raising a Discipline from level <em>L</em> to <em>L+1</em> costs <em>L+1</em> XP. So level 1 costs 1 XP, level 2 costs 2 more (3 total), up to level 5 costing 5 more (15 total).</p>
</div>

<div class="section" id="traits">
<h2>Traits</h2>
<p>Every Trait has a cost (some, like curses, have <em>negative</em> cost). <strong>Total cost of all Mortal + Vampire Traits combined cannot exceed +2.</strong> You may take up to <strong>8 Traits</strong> total; 6 or fewer is recommended.</p>

<h3>Mortal Traits</h3>
<div class="filter-bar">
  <label for="mortalCatFilter">Category:</label>
  <select id="mortalCatFilter" onchange="filterMortalTraits(this.value)">
    <option value="all">All</option>
    {mortal_cat_options}
  </select>
</div>
<table id="mortalTraitsTable">
<thead><tr><th>Trait</th><th>Cost</th><th>Description</th></tr></thead>
<tbody>
{mortal_trait_rows}
</tbody>
</table>

<h3>Vampire Traits</h3>
<p class="desc">Vampire Traits aren't grouped into categories in the character builder — shown as a single list.</p>
<table>
<thead><tr><th>Trait</th><th>Cost</th><th>Description</th></tr></thead>
<tbody>
{vampire_trait_rows}
</tbody>
</table>
</div>

<div class="section" id="skills">
<h2>Skill Trees</h2>
<p>Skills are grouped into 5 trees. When a skill <em>branches from</em> a parent skill at a given dot threshold, the parent's dots up to that threshold count as a static base added on top of the dots you invest directly in the child — so a skill's effective (practical) level is <code>parent's static base + your own dots</code>. This chains: a skill three branches deep inherits the accumulated base of everything above it.</p>
<p>Below, indentation shows the branching hierarchy — a nested skill branches from the skill directly above it at the dot count noted.</p>

{skill_tree_sections}

<h3>Custom Skills</h3>
<p>Players may invent their own skill (e.g. Dance, Chess, Agriculture) with a Storyteller-set max dots. Custom skills have no parent/base — cost follows the same <code>1, 2, 3…</code> curve from 0.</p>
</div>

<div class="section" id="disciplines">
<h2>Discipline Trees</h2>
<p>A vampire may unlock up to <strong>3 Disciplines</strong>. Each Discipline has a level from 0–5. Raising a Discipline's level lets you acquire that many powers total from it (one power slot per level), chosen from any power at or below your current level whose prerequisite (if any) you already hold.</p>
<div class="filter-bar">
  <label for="discFilter">Discipline:</label>
  <select id="discFilter" onchange="filterDisciplines(this.value)">
    <option value="all">All</option>
    {discipline_options}
  </select>
</div>

{discipline_sections}
</div>

<div class="section" id="clans">
<h2>Clans</h2>
<p>Clans are optional. Each has requirements built from your Traits and unlocked Disciplines — <strong>you may qualify for and join at most one Clan.</strong></p>

{clan_sections}
</div>

<div class="section" id="powers">
<h2>Default Vampire Powers</h2>
<p>Every vampire has access to these regardless of Discipline or Clan:</p>
<table>
<thead><tr><th>Power</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><b>Blood Surge</b></td><td>Pay 1 or more Blood, add 1 red die per Blood spent to a roll.</td></tr>
<tr><td><b>Blood Heal</b></td><td>Pay 1 Blood, heal 1 HP. Max once per turn.</td></tr>
<tr><td><b>Blush of Life</b></td><td>Pay 1 Blood, become warm and able to blush for a scene.</td></tr>
<tr><td><b>Blood Bond</b></td><td>Makes mortals Ghouls, makes vampires supernaturally like you.</td></tr>
<tr><td><b>The Kiss</b></td><td>Mortals experience ecstasy when bitten. You can close wounds by licking.</td></tr>
<tr><td><b>Willpower Reroll</b></td><td>Spend 1 Willpower to reroll up to 3 black dice.</td></tr>
</tbody>
</table>
</div>

<div class="section" id="rolls">
<h2>Rolls</h2>
<p>We use dice when a result would be interesting and dramatic. We typically roll <strong>1 base die + skill</strong>. Sometimes, certain supernatural powers, Traits, situations, and other elements add or subtract from this pool. So, if your character has Awareness 3, they would roll a pool of 4 dice.</p>

<h3>Tests &amp; Opposed Rolls</h3>
<p>We have 2 kinds of rolls:</p>
<ul>
  <li><strong>Test</strong> — the character has to meet-or-beat a certain number of successes. For example: breaking into a bank might be a Larceny test of difficulty 4.</li>
  <li><strong>Opposed</strong> — the character has to meet-or-beat the roll of an opponent. For example: two vampires are locked in combat, rolling Martial Arts and Swordsmanship against each other.</li>
</ul>
<p><strong>Margins</strong> happen when the roll is over or under the difficulty or the opposition roll.</p>
<ul>
  <li>A <strong>negative margin</strong> has consequences: failure to break into the bank and activating an alarm. In combat, negative margin can translate into damage, or a weaker position.</li>
  <li>A <strong>positive margin</strong> has advantages: a hunting roll yields more victims than expected, a combat roll causes extra damage, an Auspex roll allows extra questions.</li>
</ul>

<h3>Turns</h3>
<p>In combat or other intense scenes where every moment matters, the game might use Turns. Each Turn looks like:</p>
<ol>
  <li>Players who want to declare their intended actions for this turn.</li>
  <li>Rivals act their turn, sometimes clashing with the Players and rolling Opposed rolls, sometimes the players simply roll Test rolls.</li>
  <li>Players who have not acted yet may declare their action in reaction to the rival's actions. Waiting may have consequences, but can also be a smart move.</li>
  <li>After all Players &amp; Rivals actions are resolved, next Turn begins.</li>
</ol>

<h3>Dice</h3>
<p>The dice used in the game look like these, or, if d10s are used, then "1" corresponds to blank on black dice and skull on red dice, "2-5" corresponds to blank on black &amp; red dice, "6-9" corresponds to success on black &amp; red dice, and "0" corresponds to critical success on black &amp; red dice.</p>
<div style="text-align:center">
  <img src="{dice_image}" alt="Dice cheat sheet" style="max-width:100%;width:500px;border-radius:4px"/>
</div>
</div>

<script>
function filterMortalTraits(cat) {{
  var rows = document.querySelectorAll('#mortalTraitsTable tbody tr');
  rows.forEach(function(r) {{
    r.style.display = (cat === 'all' || r.getAttribute('data-cat') === cat) ? '' : 'none';
  }});
}}
function filterDisciplines(name) {{
  var blocks = document.querySelectorAll('.disc-block');
  blocks.forEach(function(b) {{
    b.style.display = (name === 'all' || b.getAttribute('data-disc') === name) ? '' : 'none';
  }});
}}
</script>

</body>
</html>
"""


def main() -> None:
    html = TEMPLATE.format(
        mortal_cat_options=mortal_category_options(),
        mortal_trait_rows=trait_rows(MORTAL_TRAITS, with_category=True),
        vampire_trait_rows=trait_rows(VAMPIRE_TRAITS, with_category=False),
        skill_tree_sections=skill_tree_sections(),
        discipline_options=discipline_options(),
        discipline_sections=discipline_sections(),
        clan_sections=clan_sections(),
        dice_image=icon_data_uri("Data/Images/dice_cheat_sheet.png"),
    )
    with io.open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {len(html):,} bytes to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
