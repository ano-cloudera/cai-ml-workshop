# Spec: Feature Engineering and Feature Store

## Problem

`01_generate_data.py` produces eight raw loan features and hands them
directly to the model with no transformation beyond the existing
`loan_purpose` label encoding. There is no derived signal (ratios,
interactions, binning) and no mechanism to compute, version, or reuse
features outside a single training run. The internal review asked for
feature engineering as the primary ask, with a feature store named
explicitly as a bonus, lower-priority addition.

## Acceptance Criteria

- At least two or three engineered features are added, each with a stated
  business rationale (not engineering for its own sake), computed
  deterministically from the existing raw columns so the pipeline stays
  self-contained and reproducible.
- The engineered features are used consistently across every script that
  currently duplicates `FEATURE_ORDER`
  (`02_train_model.py`, `03_predict.py`, `cml_model.py`,
  `05_validate_model.py`, `08_register_in_ai_registry.py`, `app/app.py`),
  not just added to training and forgotten elsewhere, since this repo's
  existing gotcha list already documents how easily these constants drift
  out of sync.
- A minimal feature store exists: a versioned, queryable store of computed
  feature values, separate from the model artifact itself, so the same
  feature computation logic is not re-implemented in six different files.
  Given no new heavy service dependency is wanted (matches this project's
  existing bias toward pinned, lightweight `requirements.txt` deps), this
  is implemented as a shared Python module plus a versioned Parquet/CSV
  feature table, not a standalone feature-store service.
- Documented as a bonus/optional module in README.md, consistent with how
  the reviewer scoped it, not folded into the beginner core lifecycle.

## Out of scope

- A production feature-store service (Feast, Cloudera's own feature store
  tooling, or similar). This spec produces a lightweight, in-repo
  equivalent sufficient for a workshop, not a deployable service. Adopting
  a real feature-store product is a natural extension to name in the
  README but not to build here.
- Real-time/streaming feature computation. This dataset and workshop are
  batch-oriented throughout; introducing streaming would contradict the
  project's own stated scope note about staying self-contained and fast.
