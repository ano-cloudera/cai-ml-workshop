# Plan: Feature Engineering and Feature Store

## Approach

1. **Engineered features** (added in a new shared module,
   `features/engineering.py`, so every consumer imports the same logic
   instead of re-deriving it):
   - `loan_to_income_ratio` = `loan_amount / annual_income`. Rationale: a
     borrower requesting a large loan relative to income is a materially
     different risk profile than the same `loan_amount` for a
     high-income applicant, a signal the raw columns don't expose
     directly.
   - `credit_utilization_proxy` = `num_credit_lines / (employment_years + 1)`.
     Rationale: many credit lines opened over a short employment history
     reads differently than the same count built up over decades; the
     raw columns don't capture that relationship.
   - `delinquency_rate` = `num_delinquencies / (num_credit_lines + 1)`.
     Rationale: five delinquencies out of twenty credit lines is a
     different risk signal than five out of two; this normalizes
     delinquency count against exposure instead of treating it as an
     absolute count.
   - All three are pure functions of existing raw columns, computed
     deterministically, no new data source needed.
2. **Feature store (lightweight, in-repo)**:
   - `features/store.py`: a small module wrapping a versioned feature
     table. On write, computes the engineered features for a given
     `loan_data.csv`, and saves the result to
     `features/feature_table_v{N}.parquet` (Parquet chosen over CSV here
     specifically because the feature table carries dtypes that matter,
     unlike the human-readable raw CSV), alongside a
     `features/feature_table_latest.parquet` symlink-equivalent (a small
     JSON pointer file, since actual symlinks don't survive Git cleanly).
   - Exposes `get_features(df)` (compute engineered features + join to
     raw), used by every consumer instead of each file redefining
     `FEATURE_ORDER` and the engineered-feature formulas independently.
   - This is intentionally not a client-server feature store. It is the
     smallest thing that (a) versions feature definitions and outputs,
     (b) centralizes the computation, (c) needs no new pinned dependency
     beyond `pyarrow` for Parquet support (added to `requirements.txt`).
3. **Update every `FEATURE_ORDER` consumer** to import from
   `features/engineering.py` rather than hardcoding the raw eight-feature
   list: `02_train_model.py`, `03_predict.py`, `cml_model.py`,
   `05_validate_model.py`, `08_register_in_ai_registry.py`, `app/app.py`.
   This is the highest-risk part of the change (most files touched), and
   is the reason this spec is scoped after `04` and `05`, not before:
   it touches the serving path (`cml_model.py`) that the repo's own
   documented gotchas warn is the easiest place to silently break
   inference.
4. **README update**: new "Feature Engineering and Feature Store" section,
   explicitly marked optional/bonus per the reviewer's own framing, with
   the three features' business rationale and the store's file layout.

## Files touched

- Add: `features/engineering.py`, `features/store.py`,
  `features/feature_table_v1.parquet` (generated, not hand-written)
- Edit: `02_train_model.py`, `03_predict.py`, `cml_model.py`,
  `05_validate_model.py`, `08_register_in_ai_registry.py`, `app/app.py`,
  `requirements.txt` (+pyarrow), `README.md`

## Risks

- Changing `FEATURE_ORDER` changes the model's input shape, so
  `credit_risk_model.pkl` must be retrained after this change; the old
  `.pkl` will not be compatible with the new feature set. This must ship
  together with a retrain, not as a silent contract change against the
  existing artifact.
- The AI Registry path (`08_register_in_ai_registry.py`) has its own
  documented TensorSpec shape (`(-1, len(FEATURE_ORDER))`); the shape
  changes automatically since it derives from `FEATURE_ORDER`'s length,
  but any registered model version from before this change becomes
  incompatible with the new caller contract. Document this clearly as a
  breaking change for existing registered versions.

## Verification

- Local: run the full pipeline end to end (generate, build feature table,
  train, validate, predict via `06_debug_predict.py`) after the change,
  confirm the KPI gate still passes with the enlarged feature set.
- Confirm every one of the six consumer files produces identical
  `FEATURE_ORDER` content by importing from the shared module (no
  hand-copied list left behind anywhere).
- AI Registry and CML Application paths remain static-review-only from
  this environment, consistent with the rest of this repo's verification
  notes.
