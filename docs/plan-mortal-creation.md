# Plan: Character Creation — Mortal (Final Pulse)

**Part of:** unified character creation ([plan-character-creation.md](plan-character-creation.md)) — steps **1–11** of a single wizard. Flow continues immediately to Embrace and **vampire Level 0** (step 12+); see [plan-vampire-creation.md](plan-vampire-creation.md).

**Source:** *Final Pulse text — Second Edition*, Character Creation pp. **4–5** (mortal human).

**Not a standalone scope:** mortal is the opening act of character creation (`mortal → vampire level 0 → level up`), not a separate app phase shipped alone.

**Decisions (locked for v1):**

| Topic | Decision |
|---|---|
| Traits | Free-form; app offers generic suggestions (curated list, TBD) |
| Point budgets | Hard-enforced — cannot advance until valid |
| Output | Save/load JSON + printable character sheet |
| Chronicle | Fully player-defined (no baked-in setting) |

---

## 1. Rules summary (what we implement)

### 1.1 Chronicle & concept (free text)

Player defines the chronicle and character background:

- **Chronicle name** — optional label for the campaign/setting
- **Time & place** — when and where the mortal was born / lives
- **Concept notes** — childhood, adulthood, personality, mannerisms (prompted by rules; all free text)

### 1.2 Traits (3 required)

- Each trait has: **name**, **+1 attribute**, **−1 attribute**
- Base value for every attribute: **2**
- After 3 traits: exactly **3 attributes at 3**, **3 at 2**, **3 at 1**
- **No attribute overlap:** each of the nine attributes may appear in at most one trait (as either +1 or −1)
- Attributes: Strength, Dexterity, Stamina, Charisma, Manipulation, Composure, Intelligence, Wits, Resolve

### 1.3 Skills (22 dots total)

Allocated in four labeled pools (player assigns which pool each dot came from):

| Pool | Dots | Prompt (from rules) |
|---|---:|---|
| Professional | 10 | What you spend most waking hours doing |
| Life Event | 5 | Major life events that shaped you |
| Leisure | 3 | Hobbies, pastimes, what you do for kicks |
| Natural | 4 | Innate talent; “life isn’t fair” |

- Dots may stack on the same skill across pools
- **Skill max at creation:** not specified in rules — default to **5** per skill (V5-adjacent); revisit if playtesting says otherwise
- **Standard skills:** 27 from rulebook (see §4.1)
- **Custom skills:** name + category (Physical / Social / Mental); rules warn they may be more limited in use

### 1.4 Languages

- **Count = final Intelligence rating** (after traits)
- Each entry: language name (free text or pick from suggestions later)

### 1.5 Specialties (2 required)

- **2 specialties**, each attached to a **different** skill
- Format: `Skill (specialty text)` — e.g. `Streetwise (drugs)`, `Larceny (cars)`

### 1.6 Beliefs & relations (free text)

- **Beliefs** — closely-held beliefs or general disposition
- **Relations & resources** — important people, assets, debts, etc.

### 1.7 Mortal milestone (wizard continues)

When all mortal steps validate, show *“You have now created a human!”* and enable **Next** into **step 12 (Embrace)**. This is a milestone within character creation, not the end of the wizard.

Export is available at any time via sidebar, but the primary path is completing the full creation flow through step 20.

---

## 2. User flow (wizard steps 1–11)

Linear wizard with sidebar progress; **Next** disabled until current step is valid. Steps 12–20 are vampire creation ([plan-vampire-creation.md](plan-vampire-creation.md)).

```
CHARACTER CREATION
├── 1–11  Mortal (this document)
│   1. Chronicle & Concept
│   2. Traits
│   3. Attributes (read-only summary)
│   4–7. Skills (Professional / Life Event / Leisure / Natural)
│   8. Languages
│   9. Specialties
│   10. Beliefs & Relations
│   11. Mortal milestone → “You have now created a human!”
├── 12–20 Vampire (see plan-vampire-creation.md)
└── 21+   Level-up (Level 3+)
```

**UX notes:**

- Step 3 shows computed attributes from traits (no manual attribute editing — traits are the only lever)
- Skill steps can show a **running total** per pool and **grand total** (must equal 22)
- **Load character** available from step 1 and via sidebar (restores `wizard_step` and all data)
- **Mid-wizard save** — download JSON at any step; resume via upload

---

## 3. Data model (JSON)

Single character file for the full lifecycle. See [plan-character-creation.md](plan-character-creation.md) for top-level shape.

```json
{
  "schema_version": 2,
  "wizard_step": 5,
  "character": { "name": "" },
  "chronicle": {
    "name": "",
    "time_and_place": ""
  },
  "concept": {
    "childhood": "",
    "adulthood": "",
    "personality": "",
    "mannerisms": ""
  },
  "mortal": {
    "traits": [
      { "name": "Shy", "plus": "Resolve", "minus": "Charisma" }
    ],
    "attributes": { "Strength": 2, "Dexterity": 2, "Stamina": 2, "Charisma": 2, "Manipulation": 2, "Composure": 2, "Intelligence": 2, "Wits": 2, "Resolve": 2 },
    "skills": {
      "Finance": { "dots": 3, "pools": { "professional": 3, "life_event": 0, "leisure": 0, "natural": 0 } }
    },
    "languages": ["English"],
    "specialties": [
      { "skill": "Streetwise", "text": "drugs" }
    ],
    "beliefs": "",
    "relations_and_resources": ""
  },
  "vampire": null,
  "meta": {
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601",
    "app_version": "0.1.0"
  }
}
```

- `wizard_step` — current position in unified wizard (1–20 creation; level-up uses separate sub-state)
- `vampire` — `null` until step 12 completes; then `{ "level": 0, ... }` growing through creation and level-ups
- `mortal.attributes` — **derived** from traits on save; recomputed on load if traits change
- `mortal.skills[].pools` — must sum to `dots`; pool totals across all skills must match budgets

---

## 4. Static game data (code/config)

### 4.1 Standard skills (from rulebook)

| Skill | Category |
|---|---|
| Academics | Mental |
| Animal Ken | Social |
| Athletics | Physical |
| Awareness | Mental |
| Brawl | Physical |
| Craft | Physical |
| Drive | Physical |
| Etiquette | Social |
| Finance | Mental |
| Firearms | Physical |
| Insight | Social |
| Intimidation | Social |
| Investigation | Mental |
| Larceny | Physical |
| Leadership | Social |
| Medicine | Mental |
| Melee | Physical |
| Occult | Mental |
| Performance | Social |
| Persuasion | Social |
| Politics | Mental |
| Science | Mental |
| Stealth | Physical |
| Streetwise | Social |
| Subterfuge | Social |
| Survival | Physical |
| Technology | Mental |

Store in `data/skills.json` (or Python constants in `pulse/data/skills.py`).

### 4.2 Attributes

Nine attributes with short descriptions (for tooltips/help panels) — from rulebook text.

### 4.3 Trait suggestions (placeholder list)

Curated suggestions only; player may ignore and type their own.

**File:** `data/trait_suggestions.json`

**Shape:**

```json
[
  {
    "name": "Shy",
    "plus": "Resolve",
    "minus": "Charisma",
    "blurb": "Withdrawn in social settings but steady under pressure."
  },
  {
    "name": "Confident",
    "plus": "Charisma",
    "minus": "Wits",
    "blurb": "Charismatic but sometimes slow to notice danger."
  },
  {
    "name": "Brawny",
    "plus": "Strength",
    "minus": "Dexterity",
    "blurb": "Powerfully built, but less capable of delicate or graceful movement."
  },
  {
    "name": "Nimble",
    "plus": "Dexterity",
    "minus": "Strength",
    "blurb": "Quick and precise, but lacks raw physical power."
  },
  {
    "name": "Hardy",
    "plus": "Stamina",
    "minus": "Charisma",
    "blurb": "Able to withstand hardship, though rough manners can put others off."
  },
  {
    "name": "Delicate",
    "plus": "Dexterity",
    "minus": "Stamina",
    "blurb": "Graceful and precise, but easily exhausted or physically overwhelmed."
  },
  {
    "name": "Imposing",
    "plus": "Strength",
    "minus": "Charisma",
    "blurb": "Physically commanding, but more intimidating than approachable."
  },
  {
    "name": "Restless",
    "plus": "Wits",
    "minus": "Resolve",
    "blurb": "Alert and quick to react, but struggles with prolonged, repetitive effort."
  },
  {
    "name": "Patient",
    "plus": "Resolve",
    "minus": "Wits",
    "blurb": "Persistent and methodical, but slow to respond to sudden changes."
  },
  {
    "name": "Studious",
    "plus": "Intelligence",
    "minus": "Charisma",
    "blurb": "Knowledgeable and analytical, but uncomfortable with casual social interaction."
  },
  {
    "name": "Absent-Minded",
    "plus": "Intelligence",
    "minus": "Wits",
    "blurb": "Capable of deep thought, but prone to missing what is happening nearby."
  },
  {
    "name": "Impulsive",
    "plus": "Wits",
    "minus": "Composure",
    "blurb": "Acts quickly and decisively, but has difficulty controlling immediate reactions."
  },
  {
    "name": "Stoic",
    "plus": "Composure",
    "minus": "Charisma",
    "blurb": "Calm and unreadable, but emotionally distant and difficult to warm to."
  },
  {
    "name": "Expressive",
    "plus": "Charisma",
    "minus": "Composure",
    "blurb": "Emotionally engaging and easy to read, but poor at concealing distress or uncertainty."
  },
  {
    "name": "Cunning",
    "plus": "Manipulation",
    "minus": "Charisma",
    "blurb": "Skilled at finding leverage, but rarely comes across as sincere."
  },
  {
    "name": "Guileless",
    "plus": "Charisma",
    "minus": "Manipulation",
    "blurb": "Open and naturally trustworthy, but poor at detecting or exploiting hidden motives."
  },
  {
    "name": "Suspicious",
    "plus": "Manipulation",
    "minus": "Composure",
    "blurb": "Quick to notice ulterior motives, but easily unsettled by ambiguous behavior."
  },
  {
    "name": "Unflappable",
    "plus": "Composure",
    "minus": "Wits",
    "blurb": "Remains calm in a crisis, but may react too slowly to rapidly developing threats."
  },
  {
    "name": "Driven",
    "plus": "Resolve",
    "minus": "Composure",
    "blurb": "Relentless in pursuit of a goal, but tense and easily frustrated by setbacks."
  },
  {
    "name": "Easygoing",
    "plus": "Composure",
    "minus": "Resolve",
    "blurb": "Relaxed under pressure, but struggles to sustain effort when motivation fades."
  },
  {
    "name": "Observant",
    "plus": "Wits",
    "minus": "Charisma",
    "blurb": "Notices subtle details, but spends more attention studying people than engaging them."
  },
  {
    "name": "Charming",
    "plus": "Charisma",
    "minus": "Resolve",
    "blurb": "Naturally wins people over, but relies on inspiration rather than persistence."
  },
  {
    "name": "Calculating",
    "plus": "Manipulation",
    "minus": "Composure",
    "blurb": "Carefully identifies pressure points, but becomes uneasy when events escape control."
  },
  {
    "name": "Disciplined",
    "plus": "Resolve",
    "minus": "Dexterity",
    "blurb": "Consistent and tireless, but rigid habits make spontaneous movement less fluid."
  },
  {
    "name": "Athletic",
    "plus": "Stamina",
    "minus": "Intelligence",
    "blurb": "Physically conditioned and energetic, but inclined toward action rather than reflection."
  },
  {
    "name": "Bookish",
    "plus": "Intelligence",
    "minus": "Strength",
    "blurb": "Well-read and mentally capable, but physically underdeveloped."
  },
  {
    "name": "Tough",
    "plus": "Stamina",
    "minus": "Composure",
    "blurb": "Endures pain and deprivation, but responds to stress with visible aggression."
  },
  {
    "name": "Precise",
    "plus": "Dexterity",
    "minus": "Wits",
    "blurb": "Excels when careful accuracy is possible, but hesitates when forced to improvise."
  },
  {
    "name": "Instinctive",
    "plus": "Wits",
    "minus": "Intelligence",
    "blurb": "Makes effective snap judgments, but rarely examines problems in depth."
  },
  {
    "name": "Methodical",
    "plus": "Intelligence",
    "minus": "Dexterity",
    "blurb": "Solves problems through careful analysis, but lacks fluidity and spontaneity."
  },
  {
    "name": "Commanding",
    "plus": "Charisma",
    "minus": "Composure",
    "blurb": "Naturally draws attention and obedience, but reacts poorly when openly challenged."
  },
  {
    "name": "Reserved",
    "plus": "Composure",
    "minus": "Manipulation",
    "blurb": "Keeps emotions firmly controlled, but has difficulty probing or influencing others."
  },
  {
    "name": "Tenacious",
    "plus": "Resolve",
    "minus": "Manipulation",
    "blurb": "Refuses to abandon a chosen course, but struggles to adapt through subtlety or compromise."
  },
  {
    "name": "Adaptable",
    "plus": "Wits",
    "minus": "Strength",
    "blurb": "Responds rapidly to changing circumstances, but lacks force when direct action is required."
  },
  {
    "name": "Forceful",
    "plus": "Strength",
    "minus": "Manipulation",
    "blurb": "Solves obstacles through direct pressure, but lacks subtlety in dealing with people."
  },
  {
    "name": "Silver-Tongued",
    "plus": "Manipulation",
    "minus": "Resolve",
    "blurb": "Skilled at steering others, but inclined to seek shortcuts instead of enduring hardship."
  }
]
```

**Initial seed (to expand later):** Shy, Confident, Athletic, Bookish, Hotheaded, Patient, Charming, Paranoid, Stoic, Impulsive — each with plausible +1/−1 pairs that respect no-overlap when combined (UI still validates the player’s final trio).

**UI:** “Pick a suggestion” dropdown or chips per trait slot; selecting one fills name + attributes; player can edit afterward.

### 4.4 Language suggestions (optional, v1)

Simple list in `data/language_suggestions.json` (English, Spanish, …) — not required for validation; Intelligence count still drives how many must be filled.

---

## 5. Validation (hard enforcement)

All checks run on **Next** and on **Review**. Display inline errors; block navigation when failing.

### 5.1 Chronicle & concept

| Field | Rule |
|---|---|
| Time & place | Non-empty (minimum bar for “appropriate to chronicle”) |
| Other concept fields | Optional but encouraged (show soft hint, don’t block) |

### 5.2 Traits

| Rule | Error message (example) |
|---|---|
| Exactly 3 traits | “Assign 3 traits.” |
| Each trait has name, +1, −1 | “Complete all trait fields.” |
| +1 ≠ −1 within a trait | “A trait cannot boost and penalize the same attribute.” |
| No attribute used twice across traits | “Each attribute can only appear in one trait.” |
| Final distribution 3×3, 3×2, 3×1 | “Attributes must be 3 at 3, 3 at 2, and 3 at 1.” |

### 5.3 Skills

| Rule | Error message (example) |
|---|---|
| Professional pool sums to 10 | “Professional: X/10 dots assigned.” |
| Life Event sums to 5 | “Life Event: X/5 dots assigned.” |
| Leisure sums to 3 | “Leisure: X/3 dots assigned.” |
| Natural sums to 4 | “Natural: X/4 dots assigned.” |
| Total = 22 | “Total skill dots: X/22.” |
| Per-skill dots ≥ 0, ≤ max (5) | “{skill} cannot exceed 5 dots.” |
| Custom skills have name + category | “Custom skills need a name and category.” |

### 5.4 Languages

| Rule | Error message |
|---|---|
| `len(languages) === Intelligence` | “Choose N languages (one per Intelligence dot).” |
| Each language non-empty | “Name every language.” |

### 5.5 Specialties

| Rule | Error message |
|---|---|
| Exactly 2 specialties | “Add 2 specialties.” |
| Two different skills | “Specialties must be on two different skills.” |
| Each has non-empty specialty text | “Describe each specialty.” |
| Skill must exist with ≥ 1 dot (recommended) | Soft warning if 0 dots; **hard block optional** — recommend require ≥ 1 dot on parent skill |

### 5.6 Beliefs & relations

Free text — no mechanical validation in v1.

---

## 6. Printable character sheet

### 6.1 Approach

- **Primary:** Streamlit `st.download_button` for HTML file styled for print (`@media print`)
- **In-app:** “Print preview” expander rendering the same template
- **Future:** PDF via `weasyprint` or browser Print → PDF (avoid extra deps in v1)

### 6.2 Sheet sections (order)

1. Header — character/chronicle name, time & place, date exported
2. Concept summary (condensed)
3. Attributes table — 9 attrs with values, grouped Physical / Social / Mental
4. Traits list — name (+1 / −1)
5. Skills table — skill, dots, pool breakdown (optional compact), category
6. Languages
7. Specialties
8. Beliefs
9. Relations & resources
10. Footer — “Mortal — Final Pulse” + schema version

### 6.3 Styling

- Clean, single-column, black-on-white, print-friendly
- No dependency on Streamlit theme for exported HTML

---

## 7. Save / load

| Action | Behavior |
|---|---|
| **Save JSON** | Download `{character_name_or_chronicle}_mortal.json` |
| **Load JSON** | File uploader; validate `schema_version`; hydrate `st.session_state` |
| **Autosave** | Optional v1.1 — `session_state` only; no server persistence |

**Load errors:** schema mismatch → clear message; partial/missing fields → defaults with warning.

---

## 8. Tech stack & project layout

```
Final_Pulse_App/
├── app.py                      # Streamlit entry
├── requirements.txt            # streamlit, (optional) python-docx for dev tools only
├── pulse/
│   ├── __init__.py
│   ├── models.py               # dataclasses / TypedDict for character
│   ├── validation.py           # all rules in §5
│   ├── attributes.py           # trait → attribute computation
│   ├── skills.py               # pool accounting helpers
│   ├── io.py                   # JSON save/load, schema version
│   ├── sheet.py                # HTML character sheet renderer
│   └── constants.py            # ATTRIBUTE_NAMES, POOL_BUDGETS, etc.
├── data/
│   ├── skills.json
│   ├── trait_suggestions.json  # expandable suggestion list
│   └── language_suggestions.json
├── docs/
│   └── plan-mortal-creation.md # this file
└── tests/
    ├── test_validation.py
    ├── test_attributes.py
    └── test_io.py
```

**Streamlit patterns:**

- `st.session_state.character` holds the live `Character` object
- `st.session_state.wizard_step` (int 1–11)
- Sidebar: step list, load JSON, reset character

---

## 9. Implementation phases

*Within the unified character creation app ([plan-character-creation.md](plan-character-creation.md)).*

### Phase A — Mortal steps (1–11)

1. Project scaffold + `requirements.txt`
2. `models.py` + `constants.py` + `data/skills.json`
3. `attributes.py` — trait computation + distribution check
4. `validation.py` — full rule set
5. Wizard steps 1–11 in `app.py`
6. JSON export/import
7. HTML character sheet

7. Mortal milestone step (11) → hand off to vampire steps

### Phase B — Vampire steps (12–20)

See [plan-vampire-creation.md](plan-vampire-creation.md) — not a separate product.

### Phase C — Deferred polish

1. Populate `trait_suggestions.json` (10–20 entries)
2. Tooltips with attribute/skill descriptions from rulebook
3. Skill step UX — filter by category, search, pool badges
4. Unit tests for validation edge cases

---

## 10. Open questions (non-blocking)

| # | Question | Proposed default |
|---|---|---|
| 1 | Max dots per skill at creation? | 5 |
| 2 | Require ≥ 1 skill dot for specialty parent skill? | Yes (hard block) |
| 3 | Character name field separate from chronicle? | Yes — `character.name` in JSON |
| 4 | Allow 0-dot skills on sheet? | Hide skills with 0 dots on sheet |
| 5 | Normalize “Animal ken” vs “Animal Ken”? | Display “Animal Ken”; accept either on load |

---

## 11. Test scenarios (acceptance)

1. **Valid minimal character** — 3 traits → correct 3/3/3 attr spread; 22 skills; languages = Int; 2 specialties; exports JSON and HTML
2. **Overlapping trait** — blocked with clear error
3. **Wrong attr distribution** — e.g. two +1 on same attr via overlapping traits — blocked
4. **Skill pool under/over** — cannot leave step until exact pool totals
5. **Load round-trip** — save JSON, load in fresh session, identical review output
6. **Custom skill** — e.g. Chess (Mental) counts toward pools and appears on sheet

---

## 12. Success criteria

- [ ] Player can complete mortal steps 1–11 and continue into Embrace without leaving the wizard
- [ ] Every point budget is enforced; no invalid state reachable via UI
- [ ] JSON round-trips reliably at any `wizard_step`
- [ ] Mortal sections appear correctly on sheet before and after vampire data exists
- [ ] Same `Character` model holds mortal + vampire data
