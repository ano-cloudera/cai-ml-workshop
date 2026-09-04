# Plan: CI/CD Retrain Workflow

## Approach

Add `.github/workflows/retrain.yml`:

- Trigger: `push` to `main` (matches README).
- Runner: `ubuntu-latest`.
- Steps: `actions/checkout@v4` → `actions/setup-python@v5` (Python 3.10, to
  match CML's default session Python and the notebook kernel metadata seen
  elsewhere in the repo) → `pip install -r requirements.txt` →
  `python 01_generate_data.py` → `python 02_train_model.py` →
  `python 05_validate_model.py`.
- No `env:` secrets block — nothing in this chain needs one (mlflow import
  fails gracefully and is skipped per the existing guard in
  `02_train_model.py`).
- Exit code of the last step (`05_validate_model.py`) determines job
  success/failure natively — no extra `if: failure()` handling needed.

## Files touched

- Add: `.github/workflows/retrain.yml`

## Verification

- `python -c "import yaml; yaml.safe_load(open('.github/workflows/retrain.yml'))"`
  to confirm valid YAML.
- Manually trace the step sequence against a local run of the same three
  commands (already verified working in this session).
- Actual GitHub Actions execution requires a push to a real GitHub repo —
  not verifiable from this environment. Recommend the user trigger a test
  push (or `workflow_dispatch`, if added later) once the remote is wired up.
