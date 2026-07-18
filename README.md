# Final Pulse

Streamlit app for *Final Pulse* tabletop character creation.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Status

App and data are being overhauled. The Masquerade-inspired theme and Streamlit shell are preserved.

## Regenerating the rules doc

`Instructions/Final Pulse 2E - Character Building Rules.html` is generated from
`pulse/data/{traits,skill_trees,disciplines,clans}.py`. After editing any of those,
regenerate it with:

```bash
python scripts/generate_rules_doc.py
```
