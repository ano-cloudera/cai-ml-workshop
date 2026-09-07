# Plan: API-Triggered CI/CD (GitHub to CML)

## Approach

1. Add `10_trigger_cml_job.py` (repo root, numbered to sit alongside the
   existing pipeline scripts since it is invoked the same way, from a
   workflow step calling `python 10_trigger_cml_job.py`):
   - Reads `CML_API_URL`, `CML_API_KEY`, `CML_PROJECT_ID`, and
     `CML_JOB_ID` from environment variables (same env-var-first pattern
     already used in `07_test_model_deployment.py` and
     `09_test_registry_endpoint.py`), failing loudly with setup
     instructions if any are missing.
   - Calls CML's public API v2 (`POST /api/v2/projects/{project_id}/jobs/{job_id}/runs`,
     the job-run-trigger endpoint) using `requests` (already a pinned
     dependency, no new package needed).
   - Polls the run status until it finishes or a timeout is hit, and exits
     non-zero if the triggered CML Job itself fails, so a downstream CI
     step can gate on it exactly like `05_validate_model.py`'s exit code.
2. Add a new job to `.github/workflows/retrain.yml` (or a second workflow
   file, `cml-trigger.yml`, kept separate so the GitHub-only smoke test
   still runs even if CML credentials are not configured for a given
   fork), gated on `05_validate_model.py`'s success, that runs
   `10_trigger_cml_job.py` with the three secrets pulled from
   `${{ secrets.CML_API_KEY }}` etc.
3. Write `specs/05-cicd-api-trigger/setup.md` (a companion doc, not just
   the spec/plan/tasks triad) with the concrete click-path for getting a
   CML API v2 key (User Settings > API Keys, per the runbook's own
   Section 4.1 table) and adding it as a GitHub repository secret, since
   this is the one step no script can do for the user.
4. Update README.md's CI/CD Pipeline section with a subsection describing
   this extended flow, clearly marked as opt-in and requiring the three
   secrets, distinct from the base GitHub-only workflow which needs none.

## Files touched

- Add: `10_trigger_cml_job.py`, `specs/05-cicd-api-trigger/setup.md`
- Edit: `.github/workflows/retrain.yml` (or add `cml-trigger.yml`),
  `README.md`

## Verification

- Local dry run of `10_trigger_cml_job.py`'s argument parsing and
  fail-loudly behavior when env vars are unset (does not require a real
  CML API key to verify this part).
- Actual end-to-end trigger against a live CML workspace's API v2 requires
  a real API key and Job ID, which only the user's own environment has.
  This cannot be verified from this environment. The script and workflow
  are marked experimental in the spec until the user confirms a real
  trigger run succeeds.
