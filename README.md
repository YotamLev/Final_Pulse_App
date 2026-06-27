# Final Pulse — Character Creation

Streamlit app for *Final Pulse* tabletop character creation.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Status

- **Steps 1–11:** Mortal creation (traits, skills, languages, specialties)
- **Steps 12–20:** Vampire creation (planned)
- **Level 3+:** Level-up mode (planned)

## Data

Game data lives in `data/` (`skills.json`, `powers.json`, `trait_suggestions.json`, etc.). Regenerate powers from the rulebook docx:

```bash
python scripts/extract_powers.py
```
