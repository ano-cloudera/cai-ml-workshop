# Plan: Model Monitoring & Drift Detection

## Approach

Add `monitoring/10_monitor_drift.py` (numbered to continue the pipeline's
existing script-numbering convention, in its own subfolder since it's a
distinct operational concern from the core train/deploy pipeline):

1. **Reference distribution**: load `loan_data.csv` (the same file
   `01_generate_data.py`/`02_train_model.py` produce/consume) as the
   baseline. In a real deployment this would be the training-time snapshot;
   for this workshop, the same file doubles as both, with a `--current`
   CLI arg (default: same file, so running with no args is a trivial
   zero-drift self-check) to point at a different "current production
   traffic" CSV for the drift-detected demo path.
2. **PSI computation** (numeric features: `loan_amount`, `annual_income`,
   `credit_score`, `employment_years`, `debt_to_income`, `num_credit_lines`,
   `num_delinquencies`):
   - Bin the reference feature into 10 quantile buckets (`pandas.qcut` on
     the reference data, reused to bin the current data).
   - PSI = `sum((current_pct - ref_pct) * ln(current_pct / ref_pct))` per
     bucket, summed. Standard formula, implemented directly with
     numpy/pandas — no new dependency.
   - Guard against zero-percent buckets (add a small epsilon) to avoid
     `log(0)`.
3. **Categorical check** (`loan_purpose`): same PSI formula applied to
   category proportions instead of quantile buckets.
4. **Reporting**: print a per-feature PSI table with a
   PASS/MODERATE/SIGNIFICANT label using the standard thresholds (0.1, 0.2).
5. **MLflow**: reuse the `_mlflow_available` try/except import guard
   pattern from `02_train_model.py`. When available, log each feature's
   PSI as a metric under experiment `credit-risk-model-monitoring`, plus a
   summary `max_psi` and `features_drifted` count.
6. **Exit code**: 0 if `max_psi < 0.2`, else 1 — CML Job-compatible gate,
   matching `05_validate_model.py`'s contract exactly (0 = green, 1 = red).
7. **README update**: add a `Monitor Data Drift` row to the existing CML
   Jobs table (Step A of the Model Deployment section), noting it has no
   upstream dependency and is intended to run on a recurring schedule
   (CML Jobs support cron-style scheduling in the UI) rather than
   triggered by the training job.

## Files touched

- Add: `monitoring/10_monitor_drift.py`
- Edit: `README.md` (Jobs table + a short new "Monitoring" section)

## Risks

- PSI on a *self-comparison* (default invocation) is not exactly zero due
  to quantile-boundary ties/duplicate values in synthetic data — verify
  it's negligibly small (well under 0.1), not exactly 0, when testing.
- Thresholds (0.1 / 0.2) are industry-standard but arbitrary for this
  synthetic dataset; the script documents them as configurable constants
  at the top, same style as `05_validate_model.py`'s `ROC_AUC_MIN`.
