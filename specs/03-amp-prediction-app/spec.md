# Spec: AMP-Style Interactive Prediction App

## Problem

The workshop currently only exposes the model via API (curl, `04_test_api.py`,
`07_test_model_deployment.py`). Workshop attendees who aren't comfortable
with curl/Python HTTP clients have no way to interactively explore the
model's behavior. Cloudera AI supports **CML Applications** (long-running,
always-on web apps launched from a project, similar in spirit to a
Cloudera AI Application Prototype/AMP demo UI) — this feature adds one for
this project.

## Acceptance Criteria

- A form-based UI where a user enters the 8 loan features and gets back
  `default_probability` / `prediction` / `risk_label`, matching the same
  contract as `03_predict.py`/`cml_model.py`.
- Loads the same `credit_risk_model.pkl`/`label_encoder.pkl` artifacts the
  rest of the workshop already uses — no separate model path.
- Runnable locally for development (`streamlit run app/app.py`).
- Documented as a CML Application (Applications → New Application → script
  `app/app.py`), following the same `CDSW_APP_PORT`/`CDSW_READONLY_PORT`
  port-binding awareness already established in `03_predict.py`.
- **Explicitly marked experimental / not yet validated inside a real CML
  workspace** — this environment cannot launch a CML Application, so only
  local Streamlit execution was verified. Consistent with how the existing
  README already flags the "second, unrated" Registry deployment path as
  experimental for the same reason (untested against real CML).

## Out of scope

- Authentication beyond whatever CML Applications provide natively.
- Batch/bulk prediction (CSV upload) — single-record form only, matching
  the existing single-record API contract this workshop already teaches.
