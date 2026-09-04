# Plan: AMP-Style Interactive Prediction App

## Approach

Add `app/app.py` — Streamlit chosen over Flask+HTML because it needs zero
frontend code to get a real form UI, matches what CML Applications commonly
host, and is a light dependency (pure Python, no build step) appropriate
for a workshop.

1. Load `credit_risk_model.pkl` / `label_encoder.pkl` at module level
   (Streamlit re-runs the script top-to-bottom on every interaction, so
   wrap the load in `st.cache_resource` to avoid re-loading the model on
   every keystroke).
2. Render a form for the 8 `FEATURE_ORDER` fields (numeric inputs with
   sane min/max/step matching `01_generate_data.py`'s generation ranges;
   `loan_purpose` as a `st.selectbox` populated from `le.classes_` so it's
   always in sync with the actual encoder, not a hardcoded list).
3. On submit, run the exact same inference logic as `cml_model.py`/`03_predict.py`
   (`model.predict_proba`, `nthread=1` set once at load, same
   `default_probability`/`prediction`/`risk_label` output), displayed with
   `st.metric`/color-coded risk label.
4. Add a `--` bootstrap note (not code — Streamlit apps are launched via the
   `streamlit run` CLI, not `python app.py`) documenting the CML Application
   launch command:
   `streamlit run app/app.py --server.port $CDSW_APP_PORT --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false`
   — CML's reverse proxy requires disabling Streamlit's default CORS/XSRF
   checks (Streamlit's own docs recommend this for iframed/proxied
   deployments, which is exactly what a CML Application is).
5. Add `streamlit` to `requirements.txt`.
6. Add a README section: "Interactive Prediction App (CML Application)"
   with the launch steps and the experimental-status caveat.

## Files touched

- Add: `app/app.py`
- Edit: `requirements.txt` (+streamlit), `README.md` (+section)

## Verification

- `pip install streamlit`, `streamlit run app/app.py` locally on the
  Python 3.11 venv already set up; submit a low-risk and high-risk input,
  confirm the displayed prediction matches what `04_test_api.py` /
  `06_debug_predict.py` produce for equivalent payloads.
- CML Application launch itself (port binding under `CDSW_APP_PORT`,
  reverse proxy behavior) is **not verifiable from this environment** —
  flagged in spec.md and to the user directly.
