# Spec: Model Monitoring & Drift Detection

## Problem

The workshop currently covers training, deployment, and a one-time KPI
validation gate, but nothing about what happens after deployment: if the
population of loan applicants shifts over time (a common real-world MLOps
concern — the whole reason "MLOps" and not just "ML" exists), the deployed
model's predictions silently degrade with no signal to anyone. This is a
material gap for an MLOps workshop specifically.

## Acceptance Criteria

- A script exists that compares a "current" dataset against the original
  training distribution and reports, per numeric feature, whether it has
  drifted.
- The categorical feature (`loan_purpose`) is also checked for distribution
  shift.
- Uses a standard, explainable drift metric (Population Stability Index —
  PSI) with the conventional thresholds (< 0.1 no significant shift,
  0.1–0.2 moderate, > 0.2 significant) so workshop attendees learn a
  transferable technique, not a bespoke one.
- Exits non-zero when any feature exceeds the "significant drift" threshold,
  so it's usable as a CML Job gate (mirrors `05_validate_model.py`'s
  pass/fail contract).
- Logs results to MLflow (when available, via the same `_mlflow_available`
  guard pattern already used elsewhere in this repo) so drift history is
  visible in CML's Experiments tab over time, not just in job logs.
- Adds no new required dependency — computed with pandas/numpy only
  (already pinned in `requirements.txt`).

## Out of scope

- Automated retraining triggered by detected drift (a natural next step,
  but a separate feature — would need a CML Job/API call this workshop
  doesn't currently demonstrate).
- Concept drift / label drift (requires ground-truth outcomes arriving
  after the fact, which this synthetic-data workshop has no mechanism to
  simulate). This spec covers *data* (covariate) drift only.
- A dashboard/UI for drift — out of scope; results are logged to
  MLflow and printed, consistent with how `05_validate_model.py` reports.
