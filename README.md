# FailSafe AI — Student Success Intelligence Platform

A redesigned version of your original Streamlit app: same ML model, same
Student/Faculty modes, same risk math — new visual layer on top.

## What changed (UI only)

- **`app.py`** — same logic, reorganized into cards/sections with the new
  components. Prediction now passes a `DataFrame` to the model (removes the
  sklearn "missing feature names" warning) instead of a raw list — output is
  identical.
- **`components.py`** *(new)* — small helper functions for cards, pills,
  metric tiles, and the custom SVG risk gauge. No model or business logic
  lives here.
- **`style.css`** *(new)* — the design system: dark "control room" theme,
  Space Grotesk / Inter / JetBrains Mono type, amber/teal/rose risk colors.
- **Risk score is now clamped to 0–100** for display. The original formula
  could exceed 100 in extreme cases (e.g. 0% attendance, 0% marks, 0 GPA);
  the underlying math is unchanged, only the displayed number is capped —
  matching what `st.progress()` already did in the original app.
- **Analysis results persist** across reruns via `st.session_state`, so
  changing a slider after clicking "Analyze" doesn't immediately wipe the
  results out from under you (it now waits for another click).

## What did NOT change

- The trained model (`model.pkl`) — untouched, loaded as-is.
- `train_model.py` / `test_model.py` — untouched, included for reference.
- Feature set fed to the model: `G1, G2, absences, studytime, failures`.
- The weighted risk-score formula.
- Every original feature: AI Risk Prediction, Risk Analysis, Student Persona,
  Academic Insight Breakdown, Failure Timeline, Recovery Plan, What-If
  Simulator, Resume Booster, Semester Intelligence Engine, Career Guidance
  Hub, and the Faculty quick-screen flow.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

```
app.py              — main Streamlit app
components.py        — UI helper functions (cards, gauge, pills)
style.css             — design system / theme
model.pkl             — your trained RandomForestClassifier (unchanged)
train_model.py        — training script (unchanged)
test_model.py         — quick model smoke test (unchanged)
student-mat.csv        — Math course dataset
student-por.csv         — Portuguese course dataset
requirements.txt
```

## Note on `test_model.py`

It calls `model.predict([[12, 13, 2]])` with only 3 features, but the model
was trained on 5 (`G1, G2, absences, studytime, failures`). That script will
raise a shape-mismatch error if run as-is — it predates the 5-feature
version of the model. Not changed here since you didn't ask for it, but
worth knowing if you run it.
