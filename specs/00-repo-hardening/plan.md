# Plan: Repo Hardening

## Approach

1. **Delete `API_TEST_MODELDEP.py`.** It duplicates `07_test_model_deployment.py`,
   which does the same job (call the deployed Model's `/model` endpoint)
   safely via `MODEL_ACCESS_KEY` env var + `getpass` fallback. No
   replacement needed beyond that existing script.
2. **Delete `Untitled.ipynb`.** No real content to preserve.
3. **Rename `README (1).md` → `README.md`.**
4. **Templatize `07_test_model_deployment.py`**: replace the hardcoded
   `MODEL_URL` with `os.environ.get("MODEL_URL")`, raising `SystemExit`
   with setup instructions if unset. Mirrors the existing
   `MODEL_ACCESS_KEY` pattern already in that file.
5. **Templatize `09_test_registry_endpoint.py`**: same treatment for
   `BASE_URL` → `REGISTRY_ENDPOINT_URL` and `MODEL_NAME` → `REGISTRY_MODEL_NAME`.
6. **Add `.gitignore`**: `__pycache__/`, `*.pyc`, `.venv*/`, `mlruns/`,
   `.ipynb_checkpoints/`, `.DS_Store`. Deliberately does *not* try to
   pattern-match secret-shaped filenames — hiding them from git status is
   worse than catching them via review/grep, since an ignored secret file
   still exists on disk and can leak by other means (zip, screen share).
7. **Update `README.md`** file tree to match the actual repo (drop the two
   deleted files, add `.github/workflows/retrain.yml`, `monitoring/`,
   `app/`, `specs/`), and soften the data-gen "Expected output" default
   rate to note it's numpy-version-sensitive rather than an exact figure
   (observed 39% locally against 28.34% documented, same seed=42 — numpy's
   `RandomState` stream is stable across versions for a given numpy major
   version but the repo doesn't pin an exact numpy patch version).
8. **Do not touch the committed `.pkl`/`.csv` artifacts.** They were
   verified to load and predict correctly locally (`06_debug_predict.py`);
   regenerating them under a different local numpy/xgboost build than the
   source team used would replace a known-good, presumably-tested model
   with an unvalidated one.

## Files touched

- Delete: `API_TEST_MODELDEP.py`, `Untitled.ipynb`
- Rename: `README (1).md` → `README.md`
- Edit: `07_test_model_deployment.py`, `09_test_registry_endpoint.py`, `README.md`
- Add: `.gitignore`

## Risks

- Renaming the README changes its path; no other file references it by
  name, so this is safe.
- Env-var-only config on 07/09 means a first-time user must read the
  docstring before running — acceptable, since these are debug/test
  scripts run manually from a session terminal, not automated jobs.
