# Plan: Character Creation — Vampire & Level-Up (Final Pulse)

**Part of:** unified character creation ([plan-character-creation.md](plan-character-creation.md)) — wizard steps **12–20** (Embrace through Level 2), then repeatable **level-up** for Level 3+.

**Follows:** mortal steps 1–11 ([plan-mortal-creation.md](plan-mortal-creation.md)) in the **same session and JSON file**.

**Source:** *Final Pulse text — Second Edition*, Character Creation pp. **6–7**; clan data pp. **8–9**; [`data/powers.json`](../data/powers.json).

**Flow:** `mortal (steps 1–11) → Embrace → Level 0 → Level 1 → Level 2 → Level 3+ (level-up)`. No skip past mortal.

**Decisions (locked):**

| Topic | Decision |
|---|---|
| Point budgets | Hard-enforced at every step |
| Output | Same JSON file extended + updated printable sheet |
| Chronicle | Already player-defined on mortal |
| Clan choice | After mortal creation, before Level 0 |
| Mortal first | **Required** — steps 1–11 in same wizard; no skip to Embrace |
| Mid-wizard save | **Allowed** at any step — `wizard_step` in JSON; resume via load |
| Sorcery paths | Allowed as L2 third Discipline |
| Amalgams | Offered on **L1+** power picks when character has **2+ Disciplines** and prereqs met |
| Predator types | Curated list + player-defined custom types |
| Attribute/skill caps | Default **5**; raised only by Discipline powers (see §1.8, [`data/cap_extensions.json`](../data/cap_extensions.json)) |
| Power suggestions | Filtered by `data/powers.json` + prerequisite logic ([plan-discipline-powers.md](plan-discipline-powers.md)) |

---

## 1. Rules summary

### 1.1 Overview (pp. 6–7)

After Embrace the player:

1. Chooses a **clan** → gains **clan Bane**
2. Advances through **Level 0 → 1 → 2** with fixed packages of choices
3. At **Level 3+**, gains **one pick per level** from four options

| Level | Package |
|---|---|
| **0** | 1 clan Discipline + 1st power; universal vampiric abilities |
| **1** | +2 attribute dots; 2nd clan Discipline; 2nd power; predator type (+ skills, specialty, predator power) |
| **2** | −2 skill dots; +2 attribute dots; 3rd Discipline (clan or any); 4th power |
| **3+** | Per level: **one** of — +1 attribute (per-attribute cap), +1 power, +2 skill dots, +3 specialties |

**End state at Level 2:** 3 Disciplines known, 4 powers (+ predator power may be from a 4th Discipline not counted among the 3 — see §1.6).

**Universal abilities (all vampires, from Level 0):** Blush of Life, Blood Surge, Vampiric healing (mechanics on p. 10 — display on sheet, no player choice).

---

### 1.2 Embrace — clan selection (p. 6, clan detail p. 8–9)

> *Choose a vampire clan from the Clan list chapter. You now get the clan Bane.*

**Core clans (v1):**

| Clan | Disciplines |
|---|---|
| Ventrue | Dominate, Presence, Fortitude |
| Veneris | Dominate, Protean, Potence |
| Toreador | Auspex, Presence, Celerity |
| Nosferatu | Nightmare, Obfuscate, Arrete, Potence, Animalism |
| Brujah | Presence, Potence, Celerity |
| Gangrel | Animalism, Protean, Fortitude |
| Malkavian | Auspex, Nightmare, Dominate, Arrete, Obfuscate |

**Store in:** `data/clans.json` (name, description, disciplines[], bane summary, bane player fields).

**Bane player input (mechanical fields for sheet):**

| Clan | Fields to capture |
|---|---|
| Ventrue | Feeding preference (ideals); feeding preference (shame) |
| Veneris | — (fully automatic bane) |
| Toreador | — |
| Nosferatu | Interaction penalty (−2 to −4, player picks) |
| Brujah | — |
| Gangrel | — |
| Malkavian | Mental illness/delusion (text); trigger 1; trigger 2 (emotional or situational) |

Bloodlines (p. 55+) deferred.

---

### 1.3 Level 0 Vampire

> *Choose one supernatural Discipline from the list in your Clan description. Choose your first power to receive from it.*

| Choice | Constraint |
|---|---|
| 1st Discipline | Must be from **clan Discipline list** |
| 1st power | Must be from that Discipline; **prerequisites** enforced via `powers.json` |

**No attribute or skill changes at Level 0.**

Set `vampire.level = 0` on completion.

---

### 1.4 Level 1 Vampire

> *Add 2 dots to base attributes … choose a second Discipline from your Clan Discipline list … choose a second power, either from your first Discipline or the one you chose now … choose a predator type.*

| Step | Constraint |
|---|---|
| +2 attribute dots | Any attributes; **per-attribute cap** (default 5, extendable — §1.8) |
| 2nd Discipline | Must be from **clan list**; must differ from 1st |
| 2nd power | From Discipline 1 **or** Discipline 2; prerequisites enforced |
| Predator type | One of 15 types (§1.5) |
| Predator package | +2 skill dots, +1 specialty, +1 predator power (3rd power overall) |

**Skill/specialty from predator:** player picks from **curated options** per predator type (rulebook gives OR-examples, not exhaustive lists).

**Predator power:** from *any Discipline relevant to predator type*; must meet prerequisites; prefer powers with predator bonus text when suggesting (§1.5).

Set `vampire.level = 1` on completion.

---

### 1.5 Predator types (p. 6–7)

**All types:**

| ID | Name | Description (from rulebook) |
|---|---|---|
| `alleycat` | Alleycat | Blood by force or threat |
| `hyena` | Hyena | Blood from fresh corpses |
| `leech` | Leech | Feed from other vampires |
| `flea` | Flea | Covertly from mortal family or friends |
| `honeysucker` | Honeysucker | Blood with consent |
| `farmer` | Farmer | Feed from animals |
| `shepard` | Shepard | Feed from cult, church, or fans |
| `sandman` | Sandman | Sleeping victims, often breaking in |
| `scene_queen` | Scene queen | Subculture / exclusive group with high status |
| `siren` | Siren | Seduction under guise of sex |
| `trapdoor` | Trapdoor | Lure victims in |
| `entrepreneur` | Entrepreneur | Exchange goods & services |
| `stalker` | Stalker | Study routine & habits of a target |
| `psychopomp` | Psychopomp | Victims on edge of natural death |
| `bedlamite` | Bedlamite | Feed on the insane |

**Rulebook examples (fully specified):**

| Type | Skill options (pick one branch) | Specialty examples | Example power |
|---|---|---|---|
| Sandman | Stealth **or** Larceny (+2 dots) | homes | Lullaby |
| Alleycat | Brawl **or** Intimidation (+2 dots) | streetfights / mugging | Unholy Fist * |
| Farmer | Animal Ken **or** Survival (+2 dots) | urban / hunting | Borrowed Knowledge |
| Shepard | Etiquette **or** Occult (+2 dots) | subculture / mortal cult | Awe |

\* Rulebook says “Unholy Fists”; power heading is **Unholy Fist**.

**Leech special rule:** may take **2 powers from one Discipline** as predator package (instead of 1), but feeding restriction like Ventrue bane (vampires only).

**Predator bonus:** only powers whose description includes *“if chosen as predator power”* grant a mechanical bonus; others are legal but offer no extra benefit.

**Data gap:** 11 predator types lack full skill/power mappings → `data/predator_types.json` with `status: "example" | "curated" | "tbd"`.

**Custom predator types:** Player may **add a custom predator type** (name + description + free-form skill/specialty/power choices). Stored with `source: "custom"` in JSON. Curated types remain the default UX.

---

### 1.6 Level 2 Vampire

> *Lose 2 skill dots you forgot. Add 2 Attribute dots. Choose a third Discipline, either from your Clan Discipline list or not. Choose a fourth power.*

| Step | Constraint |
|---|---|
| −2 skill dots | Player removes 2 dots from existing skills (cannot go below 0) |
| +2 attribute dots | Any attributes; respect per-attribute cap (§1.8) |
| 3rd Discipline | **Clan list OR any Discipline or Sorcery path** (paths count as Disciplines per p. 15 intro) |
| 4th power | From any **owned** Discipline/path; prerequisites enforced |

**Note:** General rules (p. 15) state vampires have **3 Disciplines known**, with predator power sometimes from a Discipline outside those 3. Track separately:

- `disciplines[]` — the 3 “known” slots (filled by L0, L1, L2 choices)
- `powers[]` — all powers including predator power (may reference a 4th source)

Set `vampire.level = 2` on completion → mortal+vampire creation **complete** for initial play.

---

### 1.7 Levels 3 and beyond

> *Each level, you can choose to add one of these: 1 attribute dot (maximum 5) … 1 Discipline power from a Discipline you have … 2 skill dots … 3 Specialties.*

| Option | ID | Constraint |
|---|---|---|
| Attribute | `attr` | +1 dot to one attribute; must not exceed **effective cap** for that attribute |
| Power | `power` | +1 power from a Discipline/path the character **already has**; prerequisites enforced; **amalgams** eligible if character has both parent Disciplines and meets prereqs |
| Skills | `skills` | +2 dots (any skills, respect per-skill max) |
| Specialties | `specialties` | +3 specialties (any skills) |

**Flow:** open-ended level-up wizard — pick level target → pick one option → apply → repeat. No limit on level in app (Storyteller sets chronicle pace).

Increment `vampire.level` after each successful level-up.

---

### 1.8 Attribute & skill caps (default 5, Discipline extensions)

**Base rule (p. 5):** *Attributes can't be raised above 5, unless with a Discipline.*

**App defaults:** attribute max = **5**, skill max = **5** for dot allocation and validation.

**Effective cap** = default + sum of permanent extensions from known powers + Masterwork choices.

#### Permanent attribute max +1 (one power per attribute)

| Power | Discipline | Attribute raised |
|---|---|---|
| Alert | Auspex | Wits |
| Quick | Celerity | Dexterity |
| Hardy | Fortitude | Stamina |
| Manipulator | Nightmare | Manipulation |
| Powerhouse | Potence | Strength |
| Charming | Presence | Charisma |
| Calculating | Arrete | Intelligence |

**No cap-raising power found** for **Resolve** or **Composure** in the current rulebook.

#### Permanent skill max

| Power | Discipline | Effect |
|---|---|---|
| Masterwork | Arrete | +1 max on **2 chosen skills**, **or** +2 max on **1 skill** (player choice recorded at acquisition) |

#### Not permanent caps (track on sheet as notes, not dot limits)

| Power | Effect |
|---|---|
| **Back to Basics** (Protean) | In animal form only: +2 Attributes (can exceed max) and skill bonuses |
| **Prowess From Pain** (Fortitude) | Temporary Physical Attribute bonus while healing; cap 5 (10 if upgraded) |
| **Fortitude Mastery** (Fortitude) | Upgrades Prowess From Pain temp cap to 10 — not a permanent dot cap |
| **Shift balance** (Protean) | Redistributes Physical attribute dots; does not raise cap |

**Data file:** [`data/cap_extensions.json`](../data/cap_extensions.json) — used by `pulse/caps.py` to compute `effective_attribute_max(attr)` and `effective_skill_max(skill)` from known powers.

**Masterwork UX:** When player acquires Masterwork (L3+ power pick), sub-wizard captures skill choice(s) before confirming.

---

## 2. Cumulative state at each level

Assuming mortal creation per existing plan:

| Stat | Mortal end | After L0 | After L1 | After L2 | Per L3+ pick |
|---|---:|---:|---:|---:|---|
| Attribute dots (above mortal base) | 0 | 0 | +2 | +4 | +1 if attr pick |
| Skill dots (above mortal 22) | 22 | 22 | 24 | 22 | +2 if skills pick |
| Specialties | 2 | 2 | 3 | 3 | +3 if specialties pick |
| Disciplines | 0 | 1 | 2 | 3 | — |
| Powers | 0 | 1 | 3 | 4 | +1 if power pick |

**Leech exception:** may have **4 powers at end of L1** (2 predator powers) if player uses Leech rule.

---

## 3. User flow (wizard steps 12–20, then level-up)

Same wizard as mortal steps ([plan-character-creation.md](plan-character-creation.md)). Step 11 ends with *“You have now created a human!”* — step 12 begins Embrace.

### Steps 12–20 — Embrace through Level 2

```
11. Mortal milestone (from plan-mortal-creation.md)
12. Embrace — Clan & Bane
13. Level 0 — 1st Discipline & Power
14. Level 1 — Attributes (+2)
15. Level 1 — 2nd Discipline & 2nd Power
16. Level 1 — Predator Type (skills, specialty, predator power)
17. Level 2 — Remove 2 Skill Dots
18. Level 2 — Attributes (+2)
19. Level 2 — 3rd Discipline & 4th Power
20. Character Review & Export
```

Set `vampire.level` to `0`, `1`, or `2` as each level’s steps complete. After step 20, initial character creation is **complete** (`wizard_step: 20`).

### Level 3+ — level-up (same character, same app)

Not a new wizard — a repeatable mode when `vampire.level >= 2`:

```
Level-Up
  1. Confirm current level → target level (level + 1)
  2. Choose one advancement option (attr / power / skills / specialties)
  3. Apply choice (sub-wizard per option)
  4. Review delta → confirm → increment level
  5. Repeat or export
```

**Navigation:** sidebar shows full steps 1–20; completed sections collapsed; **Level Up** entry when `vampire.level >= 2`.

---

## 4. Power selection UI (shared across levels)

Reuse eligibility engine from [plan-discipline-powers.md](plan-discipline-powers.md):

1. **Pool** — powers whose `source` is in character’s eligible Discipline list for this step
2. **Exclude known** — powers already on character
3. **Prerequisites** — `is_power_available(power, character)`
4. **Predator step** — widen pool to disciplines tagged relevant for chosen predator type (or all disciplines if custom type); badge powers that have predator bonuses
5. **Amalgams (L1+ power picks)** — once character has **2+ Disciplines**, include amalgams where parent `disciplines[]` ⊆ known Disciplines and prerequisites pass (applies to L1 2nd power, predator power, L2 4th power, L3+ power picks)

**Display per power:** name, source, summary, prerequisite chain, predator-bonus indicator.

**Sorcery paths at L2:** when picking 3rd Discipline, offer full `sorcery_paths` list from `powers.json` in addition to clan list and other disciplines.

---

## 5. Data model (JSON — `vampire` block)

Extends unified character schema v2 ([plan-character-creation.md](plan-character-creation.md)). Mortal data lives under `mortal`; vampire data under `vampire` (populated from step 12 onward).

```json
{
  "schema_version": 2,
  "wizard_step": 16,
  "character": { "name": "Jordy" },
  "mortal": { },
  "vampire": {
    "level": 1,
    "clan": "Gangrel",
    "bane": {
      "summary": "Gluttonous — ...",
      "fields": {}
    },
    "predator": {
      "type": "farmer",
      "source": "curated",
      "custom": null,
      "skill_choice": { "skill": "Animal Ken", "dots": 2 },
      "specialty": { "skill": "Animal Ken", "text": "urban" },
      "powers": ["arrete_borrowed_knowledge"]
    },
    "disciplines": [
      { "name": "Animalism", "source": "clan", "acquired_at_level": 0 },
      { "name": "Protean", "source": "clan", "acquired_at_level": 1 },
      { "name": "Path of Blood", "source": "other", "acquired_at_level": 2 }
    ],
    "powers": [
      { "id": "animalism_feral_whispers", "name": "Feral Whispers", "source": "Animalism", "acquired_at_level": 0, "is_predator_power": false },
      { "id": "protean_animorph", "name": "Animorph", "source": "Protean", "acquired_at_level": 1, "is_predator_power": false },
      { "id": "arrete_borrowed_knowledge", "name": "Borrowed Knowledge", "source": "Arrete", "acquired_at_level": 1, "is_predator_power": true }
    ],
    "attribute_adjustments": [
      { "level": 1, "changes": { "Strength": 1, "Stamina": 1 } },
      { "level": 2, "changes": { "Resolve": 2 } }
    ],
    "skill_adjustments": [
      { "level": 1, "predator": { "Animal Ken": 2 } },
      { "level": 2, "removed": { "Athletics": 1, "Drive": 1 } }
    ],
    "specialty_adjustments": [
      { "level": 1, "predator": { "skill": "Animal Ken", "text": "urban" } }
    ],
    "level_ups": [
      { "to_level": 3, "choice": "skills", "details": { "Science": 1, "Medicine": 1 } },
      { "to_level": 4, "choice": "power", "details": { "id": "animalism_pack_hunter" } }
    ],
    "cap_choices": {
      "masterwork": { "mode": "one_skill_plus_two", "skills": ["Science"] }
    }
  },
  "meta": { "updated_at": "ISO-8601" }
}
```

- `wizard_step` — resume position (1–20 during creation; level-up may set `wizard_step: 21` or use `vampire.level_up_in_progress`)
- `vampire` — `null` until Embrace (step 12); `level` tracks 0, 1, 2, … through creation and level-ups
- `vampire.level_ups[]` — audit log for Level 3+ choices

**Derived on load/save:**

- `attributes` — mortal base + trait adjustments + vampire `attribute_adjustments` + level-ups
- `skills` — mortal pools + predator + removals + level-ups
- `specialties` — mortal + predator + level-ups

---

## 6. Static game data (new files)

| File | Purpose |
|---|---|
| `data/clans.json` | 7 clans: disciplines, bane text, input fields |
| `data/predator_types.json` | 15 types, skill branches, specialty hints, power hints, special rules |
| `data/powers.json` | *(exists)* — power list + prerequisites |
| `data/cap_extensions.json` | Permanent cap-raising powers (§1.8) |
| `pulse/caps.py` | `effective_attribute_max()`, `effective_skill_max()` |

### 6.1 `predator_types.json` shape

```json
{
  "id": "sandman",
  "name": "Sandman",
  "description": "You feed from sleeping victims, often breaking into homes.",
  "status": "example",
  "skill_branches": [
    {
      "skills": ["Stealth"],
      "specialty_examples": ["homes"]
    },
    {
      "skills": ["Larceny"],
      "specialty_examples": ["homes"]
    }
  ],
  "suggested_powers": ["Lullaby"],
  "relevant_disciplines": ["Nightmare", "Obfuscate"],
  "special_rules": null
}
```

```json
{
  "id": "leech",
  "name": "Leech",
  "status": "example",
  "special_rules": {
    "predator_power_count": 2,
    "same_discipline": true,
    "feeding_restriction": "vampires_only"
  }
}
```

Types without rulebook examples: `status: "tbd"`, empty `skill_branches` — UI allows free-form until curated.

### 6.2 Enhance `powers.json` (Phase B)

Add optional fields to power entries (extract script update):

- `predator_bonus: true | false` — parsed from *“if chosen as predator power”* in full text
- `predator_bonus_text` — the bonus sentence(s)

---

## 7. Validation (hard enforcement)

### 7.1 Clan & Bane

| Rule | Block if |
|---|---|
| Clan selected | missing |
| Required bane fields | empty (Ventrue ×2 preferences, Malkavian illness + 2 triggers, Nosferatu penalty) |

### 7.2 Level 0

| Rule | Block if |
|---|---|
| Discipline | not on clan list |
| Power | not from chosen Discipline; prereqs fail; already known |

### 7.3 Level 1 — attributes

| Rule | Block if |
|---|---|
| Dot budget | ≠ exactly 2 dots allocated |
| Per-attribute max | any attribute > **effective cap** for that attribute |

### 7.4 Level 1 — disciplines & powers

| Rule | Block if |
|---|---|
| 2nd Discipline | not on clan list; same as 1st |
| 2nd power | not from Discipline 1 or 2; prereqs fail |

### 7.5 Level 1 — predator

| Rule | Block if |
|---|---|
| Type | not selected |
| Skills | ≠ 2 dots in one curated branch (or free-form if TBD type) |
| Specialty | missing; must attach to chosen predator skill |
| Predator power(s) | wrong count (1, or 2 for Leech); prereqs fail; not from relevant discipline |
| Leech | 2 powers not from same Discipline when using special rule |

### 7.6 Level 2 — skills

| Rule | Block if |
|---|---|
| Removal | ≠ exactly 2 dots removed from skills with sufficient dots |

### 7.7 Level 2 — attributes & discipline

| Rule | Block if |
|---|---|
| Dot budget | ≠ 2 attribute dots |
| Per-attribute max | any attribute > **effective cap** for that attribute |
| 3rd Discipline | duplicate of existing |
| 4th power | not from owned Discipline; prereqs fail |

### 7.8 Level 3+

| Rule | Block if |
|---|---|
| Choice | none selected |
| Attribute | +1 would exceed **effective cap** |
| Power | not from owned Discipline/path or amalgam rules; prereqs fail |
| Skills | ≠ 2 dots allocated; any skill > **effective skill max** |
| Specialties | ≠ 3 new specialties specified |

---

## 8. Printable character sheet (vampire sections)

Add to existing HTML sheet after mortal sections:

1. **Clan & Bane** — clan name, bane text, player bane fields
2. **Predator type** — name, feeding style, predator skills/specialty
3. **Level** — current vampire level
4. **Disciplines** — list with acquisition level
5. **Powers** — table: name, source, predator flag, acquisition level
6. **Attributes / Skills / Specialties** — show mortal + vampire deltas inline or as adjusted totals
7. **Innate abilities** — Blush of Life, Blood Surge, Vampiric healing (static text)

---

## 9. Project layout (additions)

```
pulse/
  clans.py              # load clans.json
  predator.py           # load predator_types.json, Leech rules
  powers.py             # eligibility + suggestion helpers
  vampire_validation.py # rules in §7
  vampire_models.py     # VampireState dataclass (or extend models.py)
app/
  steps_vampire.py      # wizard steps 12–20
  steps_levelup.py      # level 3+ flow
data/
  clans.json
  predator_types.json
docs/
  plan-vampire-creation.md   # this file
```

---

## 10. Implementation phases

### Phase A — Data & logic

1. `data/clans.json` from pp. 8–9
2. `data/predator_types.json` — 4 example types + 11 TBD stubs
3. `pulse/powers.py` — eligibility engine
4. Extend `extract_powers.py` — `predator_bonus` flag
5. JSON schema v2 + migration from v1 mortal-only saves

### Phase B — Creation wizard (L0–L2)

1. Steps 12–20 in Streamlit
2. `vampire_validation.py`
3. Attribute/skill delta UIs (reuse mortal skill widgets)
4. Power picker component (shared)
5. Vampire review + sheet sections

### Phase C — Level 3+

1. Level-up entry point from review screen
2. Four-option picker + sub-flows
3. Level history in `vampire.level_ups[]`
4. Masterwork / cap choice sub-wizard

### Phase D — Polish

1. Curate remaining 11 predator types (playtest with Storyteller)
2. Tooltips linking to power summaries
3. Tests for cumulative stat math and prereq chains

---

## 11. Open questions

_All previously open items are now locked (see decisions table at top). Remaining design notes:_

| # | Note |
|---|---|
| 1 | **Resolve / Composure** — no cap-raising power in rulebook; cap stays 5 unless future errata |
| 2 | **Masterwork** — single power acquisition; choice stored in `cap_choices.masterwork` |
| 3 | **Custom predator** — Storyteller approval flag optional (off by default) |

---

## 12. Acceptance scenarios

1. **Gangrel Farmer L0–L2** — Animalism + Protean + third pick; 4 powers; predator Borrowed Knowledge; skills 22→24→22; attributes +4 total
2. **Leech** — 2 predator powers same Discipline at L1; feeding restriction on sheet
3. **Malkavian** — bane triggers required before L0
4. **Prereq blocked** — cannot take Pack Hunter without another Animalism power
5. **L3 power pick** — only powers from owned Disciplines; amalgam appears when eligible
6. **JSON round-trip** — mortal → full L2 vampire → L5 with mixed level-ups → reload identical

---

## 13. Success criteria

- [ ] Player can Embrace and reach Level 2 without reading pp. 6–7
- [ ] Clan banes with player fields are captured on sheet
- [ ] Every dot budget and discipline constraint is enforced
- [ ] Power picker respects prerequisites from `powers.json`
- [ ] Level 3+ loop is repeatable and logged in JSON
- [ ] Single character file spans mortal + vampire lifecycle
