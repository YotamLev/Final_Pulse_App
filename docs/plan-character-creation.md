# Plan: Character Creation — Overview (Final Pulse)

**One app, one wizard, one JSON file.** Character creation is a single continuous flow:

```
Mortal (pp. 4–5)  →  Embrace & Level 0 (p. 6)  →  Level 1  →  Level 2  →  Level 3+ (level-up)
```

There is no separate “mortal app” or “vampire app”. Mortal creation is **the opening section** of character creation, not a prerequisite product.

## Unified wizard (steps 1–20)

| Steps | Section | Doc |
|---|---|---|
| 1–11 | **Mortal** — chronicle, traits, skills, languages, specialties, beliefs | [plan-mortal-creation.md](plan-mortal-creation.md) |
| — | *Milestone: “You have now created a human!”* — wizard continues | |
| 12 | Embrace — clan & bane | [plan-vampire-creation.md](plan-vampire-creation.md) |
| 13 | **Level 0** — 1st Discipline & power | |
| 14–16 | **Level 1** — +2 attrs, 2nd Discipline & power, predator type | |
| 17–19 | **Level 2** — −2 skills, +2 attrs, 3rd Discipline & power | |
| 20 | Review & export | |

## After step 20

**Level 3+** is the same character, same file — a repeatable **level-up** flow (not a new creation). Accessible when `vampire.level >= 2`.

## Save / resume

- **Mid-wizard save** at any step (1–20 or level-up)
- `wizard_step` (integer) drives resume position
- `vampire.level` is `null` until Embrace completes, then `0`, `1`, `2`, …

## Detail plans

| Document | Contents |
|---|---|
| [plan-mortal-creation.md](plan-mortal-creation.md) | Mortal rules, steps 1–11, validation |
| [plan-vampire-creation.md](plan-vampire-creation.md) | Embrace, levels 0–2, level 3+, caps, predator |
| [plan-discipline-powers.md](plan-discipline-powers.md) | `powers.json` schema, eligibility logic |

## JSON top-level shape

```json
{
  "schema_version": 2,
  "wizard_step": 7,
  "character": { "name": "" },
  "chronicle": { "name": "", "time_and_place": "" },
  "mortal": { "traits": [], "skills": {}, "languages": [], "specialties": [], "beliefs": "", "relations_and_resources": "" },
  "vampire": null,
  "meta": { "created_at": "", "updated_at": "" }
}
```

After Embrace, `vampire` is populated with `level: 0` and grows through creation and level-ups. Mortal fields remain immutable unless Storyteller edits (out of scope for v1).
