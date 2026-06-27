# Discipline & Sorcery Powers Data

**File:** `data/powers.json`  
**Regenerate:** `python scripts/extract_powers.py` (requires `python-docx` and the source docx)

## Contents

| Category | Count | `source_type` | `source` field |
|---|---:|---|---|
| Disciplines | 149 | `discipline` | e.g. `Animalism`, `Dominate` |
| Amalgams | 26 | `amalgam` | `Amalgams` |
| Sorcery paths | 66 | `sorcery_path` | e.g. `Path of Blood` |
| **Total** | **241** | | |

92 powers have prerequisites.

## Power entry schema

```json
{
  "id": "animalism_pack_hunter",
  "name": "Pack Hunter",
  "source_type": "discipline",
  "source": "Animalism",
  "prerequisites": { ... },
  "summary": "First sentence of rule text (optional, for UI preview)"
}
```

- **`id`** — stable slug: `{source_slug}_{power_slug}`
- **`source_type`** — `discipline` | `amalgam` | `sorcery_path`
- **`prerequisites`** — `null` if none; otherwise structured object (see below)

## Prerequisite schema

Always includes **`raw`** (verbatim from rulebook). Parsed rules use **`all`** (every rule required) and/or **`any`** (pick one branch).

### Rule types

| `type` | Fields | Meaning |
|---|---|---|
| `power` | `power` | Must know this specific power |
| `any_powers` | `powers[]` | Must know at least one listed power |
| `disciplines` | `disciplines[]` | Must have both disciplines (amalgams) |
| `powers_from_source` | `source_type`, `source`, `min_count`, `exclude[]` | Must know N other powers from a discipline/path |
| `specialty` | `skill`, `specialty` | Must have a skill specialty (e.g. Performance: Dance) |

### Examples

**Single power:**
```json
{ "raw": "Mesmerize", "all": [{ "type": "power", "power": "Mesmerize" }] }
```

**N other powers from same discipline:**
```json
{
  "raw": "1 other Animalism power",
  "all": [{
    "type": "powers_from_source",
    "source_type": "discipline",
    "source": "Animalism",
    "min_count": 1,
    "exclude": ["Pack Hunter"]
  }]
}
```

**OR between powers:**
```json
{
  "raw": "Mesmerize or Draw on Instinct",
  "any": [
    { "type": "power", "power": "Mesmerize" },
    { "type": "power", "power": "Draw On Instinct" }
  ]
}
```

**Amalgam — discipline pair OR discipline pair:**
```json
{
  "raw": "Obfuscate & Potence or Obfuscate & Celerity",
  "any": [
    { "type": "disciplines", "disciplines": ["Obfuscate", "Potence"] },
    { "type": "disciplines", "disciplines": ["Obfuscate", "Celerity"] }
  ]
}
```

**Amalgam — disciplines + any power:**
```json
{
  "raw": "Arrete & Auspex, Mind Palace or Premonition",
  "all": [
    { "type": "disciplines", "disciplines": ["Arrete", "Auspex"] },
    { "type": "any_powers", "powers": ["Mind Palace", "Premonition"] }
  ]
}
```

## Planned eligibility logic (for UI)

When suggesting powers for a character:

1. **Filter by source** — only powers from disciplines/paths the character has (amalgams need both parent disciplines).
2. **Evaluate prerequisites** — recursively check `all` / `any` rules against `character.known_powers`.
3. **Exclude already known** — don’t suggest powers the character already has.
4. **Predator powers** — separate filter using predator-type relevance during step 16 and level-up power picks.

Helper function sketch:

```python
def is_power_available(power: dict, character) -> bool:
    if not has_required_source(power, character):
        return False
    prereq = power.get("prerequisites")
    if not prereq:
        return True
    if "all" in prereq:
        return all(evaluate_rule(r, character) for r in prereq["all"])
    if "any" in prereq:
        return any(evaluate_rule(r, character) for r in prereq["any"])
    return True
```

## Known source issues

`meta.unresolved_power_references` lists prerequisite power names that don’t match any extracted power heading:

- **Unrelenting** — referenced by amalgam **Momentum**; no power with this name exists in the docx (likely a typo).

Prerequisite text **Draw on Instinct** is normalized to power heading **Draw On Instinct**.
