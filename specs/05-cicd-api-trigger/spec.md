# Spec: API-Triggered CI/CD (GitHub to CML)

## Problem

The existing `.github/workflows/retrain.yml` proves the KPI gate logic on
every push to `main`, but it runs entirely inside GitHub's own runner. It
never touches the real CML workspace: no CML Job runs, no new build is
created, no deployment is promoted. The internal review explicitly asked
for the missing half of this loop: a push to GitHub should be able to
trigger the actual CML lifecycle, not just a parallel copy of it on
GitHub's infrastructure. The demo runbook already names this exact gap in
Section 9.3 (Cloudera AI API v2, described there as "the natural follow-up
conversation" and intentionally left unbuilt in the base demo).

## Acceptance Criteria

- Documentation exists explaining, step by step, how to obtain a CML API v2
  key and store it as a GitHub Secret, matching CML's own auth model (this
  cannot be hardcoded or guessed, it is workspace- and user-specific, same
  discipline already applied to `MODEL_ACCESS_KEY` elsewhere in this repo).
- A script or workflow step exists that, after `05_validate_model.py`
  passes inside the GitHub Actions run, calls the CML Jobs API to trigger a
  retrain Job in the real CML workspace (not a duplicate of the GitHub-side
  training, an actual call into CML).
- The workflow fails loudly and specifically if the CML API call fails
  (wrong key, wrong workspace URL, Job not found), rather than silently
  succeeding on the GitHub-only steps and leaving the CML side stale with
  no signal.
- Documented as experimental / not yet validated against a live workspace
  from this environment, consistent with how `03-amp-prediction-app` and
  the AI Registry path are already flagged in this repo when something
  cannot be exercised outside a real CML session.

## Out of scope

- Automatically promoting a Model Deployment build from the same pipeline
  run (build promotion is a separate CML API call with its own risk, since
  it affects a production-serving endpoint; land the Job trigger first,
  treat deployment promotion as a follow-up once the trigger path is
  proven).
- Any GitOps-style rollback automation. This spec only closes the forward
  path (push triggers CML), not a rollback path.
