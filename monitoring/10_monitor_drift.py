"""
Script 10: Detect data (covariate) drift between the reference training
distribution and a current dataset, using the Population Stability Index
(PSI).

Usage:
    python monitoring/10_monitor_drift.py [--reference loan_data.csv] [--current loan_data.csv]

With no arguments, compares loan_data.csv against itself (a trivial
near-zero-drift self-check useful for verifying the script runs cleanly).
Point --current at a newer dataset to detect real drift.

PSI thresholds (standard convention):
    < 0.1   no significant population shift
    0.1-0.2 moderate shift, worth investigating
    > 0.2   significant shift, model likely needs retraining

Exit codes (CML Job-compatible, same contract as 05_validate_model.py):
    0 — no feature exceeds the SIGNIFICANT threshold
    1 — one or more features have drifted significantly
"""

import argparse
import sys

import numpy as np
import pandas as pd

try:
    import mlflow
    _mlflow_available = True
except ImportError:
    _mlflow_available = False
    print("mlflow not available — skipping experiment tracking", flush=True)

NUMERIC_FEATURES = [
    "loan_amount",
    "annual_income",
    "credit_score",
    "employment_years",
    "debt_to_income",
    "num_credit_lines",
    "num_delinquencies",
]
CATEGORICAL_FEATURES = ["loan_purpose"]

PSI_MODERATE = 0.1
PSI_SIGNIFICANT = 0.2
N_BUCKETS = 10
EPS = 1e-6


def _psi(reference: pd.Series, current: pd.Series) -> float:
    """PSI = sum((cur_pct - ref_pct) * ln(cur_pct / ref_pct)) over buckets."""
    ref_pct = reference.value_counts(normalize=True).sort_index()
    cur_pct = current.value_counts(normalize=True).sort_index()
    all_buckets = ref_pct.index.union(cur_pct.index)
    ref_pct = ref_pct.reindex(all_buckets, fill_value=0.0) + EPS
    cur_pct = cur_pct.reindex(all_buckets, fill_value=0.0) + EPS
    return float(((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)).sum())


def numeric_psi(reference: pd.Series, current: pd.Series) -> float:
    # Quantile bucket edges from the reference distribution, applied to both.
    edges = pd.qcut(reference, q=N_BUCKETS, duplicates="drop", retbins=True)[1]
    edges[0], edges[-1] = -np.inf, np.inf
    ref_binned = pd.cut(reference, bins=edges)
    cur_binned = pd.cut(current, bins=edges)
    return _psi(ref_binned, cur_binned)


def categorical_psi(reference: pd.Series, current: pd.Series) -> float:
    return _psi(reference, current)


def label(psi: float) -> str:
    if psi >= PSI_SIGNIFICANT:
        return "SIGNIFICANT"
    if psi >= PSI_MODERATE:
        return "MODERATE"
    return "PASS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", default="loan_data.csv")
    parser.add_argument("--current", default="loan_data.csv")
    args = parser.parse_args()

    try:
        ref_df = pd.read_csv(args.reference)
        cur_df = pd.read_csv(args.current)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    results = {}
    for feature in NUMERIC_FEATURES:
        results[feature] = numeric_psi(ref_df[feature], cur_df[feature])
    for feature in CATEGORICAL_FEATURES:
        results[feature] = categorical_psi(ref_df[feature], cur_df[feature])

    print(f"{'Feature':<20} {'PSI':>8}   Status")
    print("-" * 44)
    for feature, psi in results.items():
        print(f"{feature:<20} {psi:>8.4f}   {label(psi)}")

    max_psi = max(results.values())
    drifted = [f for f, psi in results.items() if psi >= PSI_SIGNIFICANT]
    print()
    print(f"Max PSI            : {max_psi:.4f}")
    print(f"Features drifted   : {len(drifted)} ({', '.join(drifted) if drifted else 'none'})")

    if _mlflow_available:
        mlflow.set_experiment("credit-risk-model-monitoring")
        with mlflow.start_run():
            mlflow.log_params({
                "reference_file": args.reference,
                "current_file": args.current,
                "psi_moderate_threshold": PSI_MODERATE,
                "psi_significant_threshold": PSI_SIGNIFICANT,
            })
            mlflow.log_metrics({f"psi_{f}": psi for f, psi in results.items()})
            mlflow.log_metrics({
                "max_psi": max_psi,
                "features_drifted": len(drifted),
            })
            print(f"\nMLflow run logged  — experiment: credit-risk-model-monitoring")

    if max_psi >= PSI_SIGNIFICANT:
        print("\nDRIFT CHECK FAILED: one or more features drifted significantly.")
        sys.exit(1)

    print("\nDRIFT CHECK PASSED — no significant drift detected.")


if __name__ == "__main__":
    main()
