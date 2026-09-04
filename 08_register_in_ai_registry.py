"""
Script 8: Train, log to MLflow, and register the credit risk model in the
Cloudera AI Registry.

WHY mlflow.xgboost.log_model() AND AN EXPLICIT float32 TensorSpec SIGNATURE
------------------------------------------------------------------------------
Three separate bugs had to be fixed here, found the hard way against a real
CML Registry -> Endpoint deployment:

1. An earlier version wrapped the classifier in a custom
   mlflow.pyfunc.PythonModel subclass, so loan_purpose encoding and
   FEATURE_ORDER enforcement would travel inside one registry artifact.
   Triton's generated model.py calls `self.model.predict(x)` directly at
   serve time, and CML's conversion silently produces a None model object
   for a custom PythonModel class — every inference call then fails with
   "'NoneType' object has no attribute 'predict'" no matter what package
   versions are installed. Native flavors (mlflow.xgboost.log_model, same
   as 02_train_model.py) load correctly; custom pyfunc classes don't.

2. mlflow.models.infer_signature(X_test, y_prob), inferred from a pandas
   DataFrame, produces a ColSpec signature (named columns, no shape).
   CML's conversion runs the SAME shape-extracting converter for every
   MLflow flavor — xgboost included — and fails at conversion time with
   "No shape found in MLflow input" on any ColSpec signature, regardless
   of flavor. It needs an explicit TensorSpec (a single homogeneous-dtype
   tensor with a shape) instead.

3. Even with a TensorSpec, a float64 dtype fails at inference time:
   "dtype of input float32 does not match expected dtype float64". Triton's
   own tensor config for the endpoint is fixed at FP32 regardless of what's
   declared in the signature (confirmed via the endpoint's /metadata
   response showing "datatype": "FP32"), and mlflow's schema enforcement
   inside model.py rejects a mismatched dtype before the data ever reaches
   predict(). The signature must declare float32 to match.

All three fixes are required together. The tradeoff of neither being a
ColSpec/pyfunc-wrapper: loan_purpose must be pre-encoded by the caller
(same numeric-FEATURE_ORDER contract cml_model.py already uses) — the
loan_purpose -> int mapping is printed at the end of this script's output.

WHY xgboost==3.1.3 / scikit-learn==1.7.2, NOT THE PROJECT'S PINNED VERSIONS
------------------------------------------------------------------------------
requirements.txt pins xgboost==1.7.6 / scikit-learn==1.3.0 for cml_model.py's
Model Deployment path, which builds its own container from requirements.txt.
The AI Registry -> Endpoint path is different: it serves the model from a
FIXED Triton base image that (as of this writing) ships Python 3.12.3,
xgboost 3.1.3, and scikit-learn 1.8.0 — not configurable via this script's
pip_requirements, which only documents the training environment, it does
not get installed into the serving container. A CML session's Python 3.10
can't install scikit-learn 1.8.0 (requires Python >=3.11), so an exact
match isn't achievable here — xgboost 3.1.3 is the critical one to match
(its booster serialization changed significantly across the 1.x -> 3.x
jump), while scikit-learn 1.7.2 (newest available under Python 3.10) is a
same-major-version best effort against the container's 1.8.0.

Before running this script, install those versions in the session (leave
mlflow itself untouched — it's pinned by mlflow-cml-plugin and upgrading it
can break experiment tracking auth):

    pip install --user "xgboost==3.1.3" "scikit-learn==1.7.2"

Downgrade back to the pinned versions afterward if you plan to re-run
02_train_model.py / 05_validate_model.py / rebuild cml_model.py's Model
Deployment in the same session — those expect xgboost==1.7.6 /
scikit-learn==1.3.0 per requirements.txt, and a pkl produced under 3.1.3
may not load correctly in that container:

    pip install --user "xgboost==1.7.6" "scikit-learn==1.3.0"

Run this from a Cloudera AI session in the project (after 01_generate_data.py
has produced loan_data.csv). It trains a fresh model, logs an experiment run,
and registers it in the AI Registry.
"""

import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd
from mlflow.models.signature import ModelSignature
from mlflow.types import Schema, TensorSpec
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

EXPERIMENT_NAME = "credit-risk-model"
REGISTERED_MODEL_NAME = "credit_risk_model"
CSV = "loan_data.csv"

FEATURE_ORDER = [
    "loan_amount",
    "annual_income",
    "credit_score",
    "employment_years",
    "debt_to_income",
    "num_credit_lines",
    "num_delinquencies",
    "loan_purpose",
]

PARAMS = {
    "n_estimators": 100,
    "max_depth": 4,
    "learning_rate": 0.1,
    "eval_metric": "logloss",
    "random_state": 42,
}


def main():
    try:
        df = pd.read_csv(CSV)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: {CSV} not found. Run 01_generate_data.py first.")

    le = LabelEncoder()
    df_encoded = df.copy()
    df_encoded["loan_purpose"] = le.fit_transform(df_encoded["loan_purpose"])

    X = df_encoded[FEATURE_ORDER]
    y = df_encoded["default"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = XGBClassifier(**PARAMS)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    report = classification_report(y_test, y_pred, output_dict=True)
    roc_auc = roc_auc_score(y_test, y_prob)

    metrics = {
        "roc_auc": round(roc_auc, 4),
        "accuracy": round(report["accuracy"], 4),
        "precision_default": round(report["1"]["precision"], 4),
        "recall_default": round(report["1"]["recall"], 4),
        "f1_default": round(report["1"]["f1-score"], 4),
        "precision_no_default": round(report["0"]["precision"], 4),
        "recall_no_default": round(report["0"]["recall"], 4),
        "f1_no_default": round(report["0"]["f1-score"], 4),
    }

    # A shaped TensorSpec, not mlflow.models.infer_signature(X_test, y_prob)
    # (which infers ColSpec — named columns, no shape — from a DataFrame).
    # CML's Registry -> Endpoint conversion runs the same shape-extracting
    # converter for every MLflow flavor, xgboost included, and fails with
    # "No shape found in MLflow input" on a ColSpec signature regardless of
    # flavor. See module docstring.
    # float32, not float64: Triton's own tensor config for this endpoint is
    # fixed at FP32 regardless of what's declared here (confirmed via the
    # endpoint's /metadata response). mlflow's schema enforcement inside
    # model.py checks incoming data against this signature's dtype, so a
    # float64 signature rejects Triton's FP32 payload with "dtype of input
    # float32 does not match expected dtype float64".
    input_example = X_test.head(3).to_numpy(dtype=np.float32)
    signature = ModelSignature(
        inputs=Schema([TensorSpec(np.dtype(np.float32), (-1, len(FEATURE_ORDER)))]),
        outputs=Schema([TensorSpec(np.dtype(np.float32), (-1,))]),
    )

    mlflow.set_experiment(EXPERIMENT_NAME)
    with mlflow.start_run(run_name="xgboost-native") as run:
        mlflow.log_params(PARAMS)
        mlflow.log_params({
            "test_size": 0.2,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "default_rate": round(float(y.mean()), 4),
        })
        mlflow.log_metrics(metrics)

        # MLflow 2.x uses artifact_path; 3.x renamed it to name. Cloudera AI
        # runtimes ship 2.x, so artifact_path is the correct argument here
        # (matches the mlflow.xgboost.log_model call in 02_train_model.py).
        mlflow.xgboost.log_model(
            clf,
            artifact_path="model",
            input_example=input_example,
            signature=signature,
            pip_requirements=["xgboost==3.1.3", "scikit-learn==1.7.2", "pandas", "numpy"],
        )

        print(f"run_id: {run.info.run_id}")
        for k, v in metrics.items():
            print(f"  {k:20s} {v}")

        # Register. On Cloudera AI this lands in the AI Registry; you can also
        # do it from Experiments -> run -> Register Model in the UI.
        model_uri = f"runs:/{run.info.run_id}/model"
        result = mlflow.register_model(model_uri, REGISTERED_MODEL_NAME)
        print(f"\nregistered '{result.name}' version {result.version}")

        print("\nloan_purpose encoding (pass the int, in FEATURE_ORDER position 8):")
        for cls, code in zip(le.classes_, le.transform(le.classes_)):
            print(f"  {cls:12s} -> {code}")


if __name__ == "__main__":
    main()
