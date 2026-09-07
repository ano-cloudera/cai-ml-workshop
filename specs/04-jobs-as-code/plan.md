# Plan: Jobs as Code and Audience Disclaimer

## Approach

1. Add `jobs/pipeline.yaml`, a declarative description of the four jobs and
   their dependency chain. CML itself has no single native "jobs as code"
   import format as of this writing, so this file is written as a plain,
   documented YAML manifest that either a human follows step by step (same
   fields as today's README table, now centralized in one file instead of
   prose) or a future script (see `05-cicd-api-trigger`) can parse and feed
   directly into CML's Jobs API. Structure:
   ```yaml
   jobs:
     - name: Generate Loan Data
       script: 01_generate_data.py
       depends_on: null
       schedule: manual
     - name: Train Credit Risk Model
       script: 02_train_model.py
       depends_on: Generate Loan Data
       schedule: manual
     - name: Validate Model KPIs
       script: 05_validate_model.py
       depends_on: Train Credit Risk Model
       schedule: manual
     - name: Monitor Data Drift
       script: monitoring/10_monitor_drift.py
       depends_on: null
       schedule: cron  # recurring, independent of the training chain
   ```
2. Update README.md's existing Jobs table (in the CML Model Deployment
   section) to point at `jobs/pipeline.yaml` as the source of truth, and
   keep the manual click-through table as the "how to set this up by hand"
   fallback, since CML doesn't natively import a manifest yet.
3. Add an "Audience and Scope" callout near the top of README.md, right
   after the existing Project Overview section, stating:
   - This is a beginner-oriented, self-contained lifecycle demo (synthetic
     data, no external Data Lake dependency).
   - What it deliberately excludes today: feature engineering / feature
     store (`06-feature-engineering-store`), API-driven CI/CD
     (`05-cicd-api-trigger`) beyond the GitHub-runner-only workflow already
     in place.
4. Add a short "Monitoring" line item to the same disclaimer, pointing at
   the already-existing `monitoring/10_monitor_drift.py` and its README
   section, so it reads as a documented stage of the lifecycle rather than
   a file a participant has to notice on their own.

## Files touched

- Add: `jobs/pipeline.yaml`
- Edit: `README.md` (Audience and Scope callout, Jobs table pointer)

## Verification

- `python -c "import yaml; yaml.safe_load(open('jobs/pipeline.yaml'))"` to
  confirm valid YAML.
- Manual cross-check: every script path named in `jobs/pipeline.yaml`
  exists in the repo.
- Not verifiable from this environment: actually creating these four Jobs
  in a live CML workspace from the manifest (no automated importer exists
  yet, this spec ships the manifest and the manual fallback instructions
  only).
