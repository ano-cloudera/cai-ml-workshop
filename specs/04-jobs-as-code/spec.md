# Spec: Jobs as Code and Audience Disclaimer

## Problem

Internal review of the workshop (SE India, 2026-09-04) confirmed the six
core stages work end to end in a real CML session, but raised two related
gaps that both trace back to the same complaint: the workshop reads as a
single fixed script rather than a governed lifecycle a participant could
adapt or repeat on their own.

1. The Generate/Train/Validate/Monitor job chain is documented in README.md
   as manual click-through instructions ("go to Jobs, click New Job, fill
   in these fields"), not created automatically when the project is
   imported. A participant has to type the same field values four times
   from a table before the lifecycle is actually running as scheduled
   infrastructure rather than terminal commands.
2. The reviewer noted the workshop is well suited to a beginner audience
   but does not say so anywhere, so a participant expecting an advanced
   MLOps deep dive walks in with the wrong expectations.

## Acceptance Criteria

- A machine-readable job definition exists in the repo describing all four
  jobs (Generate Loan Data, Train Credit Risk Model, Validate Model KPIs,
  Monitor Data Drift) with their dependency chain, so the manual README
  table becomes a fallback path, not the only path.
- README.md states, near the top, who this workshop is for (beginner,
  self-contained synthetic-data lifecycle demo) and what it deliberately
  does not cover (feature engineering, a feature store, API-driven CI/CD),
  each with a pointer to the spec that will close that gap.
- The existing `monitoring/10_monitor_drift.py` module is referenced in the
  same jobs table as a first-class stage, not left implicit.

## Out of scope

- Actually calling the CML Jobs API to create these jobs programmatically
  from a script (that's closer to `05-cicd-api-trigger`, which already
  covers scripted interaction with the CML API). This spec only produces
  the job definition artifact and the disclaimer; wiring an import-time
  script that reads the definition and calls the API is a natural
  follow-up, not required to close this spec.
