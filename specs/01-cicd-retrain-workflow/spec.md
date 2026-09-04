# Spec: CI/CD Retrain Workflow

## Problem

The README documents an automated pipeline: every push to `main` should
regenerate data, retrain the model, and gate the pipeline on KPI thresholds
via `05_validate_model.py`. The workflow file it names,
`.github/workflows/retrain.yml`, does not exist in the repo — the CI/CD
section of the README was describing something that was never committed.

## Acceptance Criteria

- `.github/workflows/retrain.yml` exists and triggers on push to `main`.
- It runs, in order: install `requirements.txt` → `01_generate_data.py` →
  `02_train_model.py` → `05_validate_model.py`.
- The job fails (red) if `05_validate_model.py` exits non-zero (KPI
  thresholds missed), matching the README's documented gate behavior.
- No secrets are required, matching the README's existing claim that "no
  secrets or external services required."
- MLflow logging is correctly skipped in this environment (it already is,
  via `02_train_model.py`'s `_mlflow_available` guard — no workflow-level
  change needed for that).

## Out of scope

- Auto-deploying to CML from the workflow (would require CML API
  credentials as GitHub Secrets — a separate, larger feature the README
  doesn't currently describe or need).
- Caching pip dependencies for speed — nice-to-have, not required for
  correctness; can be added later without changing the spec.
