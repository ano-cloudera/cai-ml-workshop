# Credit Risk Model — Loan Default Prediction

An end-to-end machine learning project that predicts the probability of a borrower defaulting on a loan. Built with XGBoost and served as a REST API via Flask, designed to run on **Cloudera AI (CML) / AI Workbench**.

---

## Project Overview

Credit risk scoring is a core use case in financial services. This project demonstrates:

- Synthetic loan dataset generation with realistic risk factors
- Binary classification model training (default vs. no default) using XGBoost
- MLflow experiment tracking integrated with CML's native Experiments UI
- Model serialization and deployment as a REST API
- Automated CI/CD pipeline with KPI validation gates on every push

### Features used for prediction

| Feature | Description |
|---|---|
| `loan_amount` | Requested loan amount (USD) |
| `annual_income` | Applicant's annual income (USD) |
| `credit_score` | FICO-style credit score (300–850) |
| `employment_years` | Years in current employment |
| `debt_to_income` | Ratio of monthly debt payments to gross income |
| `num_credit_lines` | Number of open credit lines |
| `num_delinquencies` | Number of past delinquencies |
| `loan_purpose` | Purpose: home, auto, education, personal, business |

---

## Repository Structure

```
cai-ml-workshop/
├── requirements.txt                  # Python dependencies
├── cdsw-build.sh                     # CML/CDSW environment bootstrap script
├── 01_generate_data.py               # Generate synthetic loan dataset (loan_data.csv)
├── 02_train_model.py                 # Train XGBoost model, log to MLflow, save artifacts
├── 03_predict.py                     # Flask/Gunicorn REST API — session-based serving
├── 04_test_api.py                    # Test the running Flask API with sample requests
├── 05_validate_model.py              # KPI validation gate — used by CI/CD pipeline
├── 06_debug_predict.py               # Debug: call cml_model.predict() directly, print full traceback
├── 07_test_model_deployment.py       # Debug: call the deployed model's REST endpoint directly
├── 08_register_in_ai_registry.py     # Train, log to MLflow, and register model in Cloudera AI Registry
├── 09_test_registry_endpoint.py      # Test a Registry -> Model Endpoint (KServe V2) deployment
├── cml_model.py                      # CML Model Deployment entry point (production path)
├── monitoring/
│   └── 10_monitor_drift.py           # Data drift detection (PSI) — CML Job, run on a schedule
├── app/
│   └── app.py                        # Streamlit interactive prediction UI — CML Application
├── specs/                            # Spec-kit: spec.md / plan.md / tasks.md per feature
└── .github/workflows/retrain.yml     # GitHub Actions CI/CD workflow
```

<img width="735" height="367" alt="image" src="https://github.com/user-attachments/assets/d54f39f4-3ac7-4492-bea1-27eab6ee25e1" />

---

## MLflow Experiment Tracking

This project uses **MLflow** to log model parameters, KPIs, and artifacts. In Cloudera AI the `MLFLOW_TRACKING_URI` environment variable is automatically set in every session — no configuration needed. When running locally, runs are stored in `./mlruns`.

Each training run (`02_train_model.py`) records:

| What is logged | MLflow key |
|---|---|
| Hyperparameters | `n_estimators`, `max_depth`, `learning_rate`, `eval_metric` |
| Dataset stats | `train_samples`, `test_samples`, `default_rate` |
| **KPI / success metrics** | `roc_auc`, `accuracy` |
| Default class metrics | `precision_default`, `recall_default`, `f1_default` |
| No-default class metrics | `precision_no_default`, `recall_no_default`, `f1_no_default` |
| Model artifact | XGBoost model (with signature + input example) |
| Encoder artifact | `label_encoder.pkl` |

> MLflow is pre-installed in CML sessions via `mlflow-cml-plugin`. It is intentionally excluded from `requirements.txt` to avoid breaking CML's pinned version. When running outside CML (e.g. GitHub Actions), MLflow is skipped automatically.

**To view experiment results in CML:** navigate to **Experiments** in the left sidebar of your project.

---

## Using This Project in Cloudera AI (CML)

### Prerequisites

- Access to a Cloudera AI (CML) workspace
- AI Workbench enabled on your CML cluster
- Git credentials configured in your CML profile

---

### Step 1 — Create a New Project from Git

1. Log in to your **Cloudera AI** workspace.
2. Click **New Project** on the Projects page.
3. Choose **Git** as the project source.
4. Enter the repository URL:
   ```
   https://github.com/partomia/Cloudera-AI-MLOPs-Workshop
   ```
5. Set the project name and click **Create Project**.

---

### Step 2 — Open a Session and Install Dependencies

1. Inside the project, click **New Session**.
2. Select:
   - **Editor**: Workbench (or JupyterLab)
   - **Kernel**: Python 3
   - **Resource Profile**: At least 2 vCPU / 4 GB RAM
3. Click **Start Session**.
4. In the **Terminal** tab, run:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 3 — Generate the Dataset

```bash
python 01_generate_data.py
```

Generates `loan_data.csv` (10,000 synthetic loan records).

Expected output (indicative — the exact default rate depends on your
`numpy` version; `np.random.seed(42)` reproduces the same stream within a
numpy major version but not necessarily across one):
```
Dataset generated: 10000 rows, default rate: ~28-39%
```

---

### Step 4 — Train the Model

```bash
python 02_train_model.py
```

Trains an XGBoost classifier, logs the run to MLflow, and saves:
- `credit_risk_model.pkl` — trained model
- `label_encoder.pkl` — encoder for `loan_purpose`

Expected output:
```
              precision    recall  f1-score   support
           0       0.xx      0.xx      0.xx      xxxx
           1       0.xx      0.xx      0.xx      xxxx

ROC-AUC: 0.xxxx
MLflow run logged  — run_id: ...
Model saved to credit_risk_model.pkl
```

---

### Step 5 — Start the Prediction API

Run the API server from your **session terminal**:

```bash
python 03_predict.py
```

Gunicorn will start on port `5000`:

```
[INFO] Starting gunicorn 25.1.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Booting worker with pid: ...
```

Keep this terminal open — the server must stay running for Step 6.

---

### Step 6 — Test the API

```bash
python 04_test_api.py
```

Expected output:
```
Health check: {'status': 'ok'}

[Low-risk applicant]
  Default probability : 0.0312
  Prediction          : 0
  Risk label          : LOW

[High-risk applicant]
  Default probability : 0.8741
  Prediction          : 1
  Risk label          : HIGH
```

---

### API Reference

#### `POST /predict`

**Request body (JSON):**
```json
{
  "loan_amount": 10000,
  "annual_income": 90000,
  "credit_score": 780,
  "employment_years": 10,
  "debt_to_income": 0.15,
  "num_credit_lines": 5,
  "num_delinquencies": 0,
  "loan_purpose": "home"
}
```

**Response:**
```json
{
  "default_probability": 0.0312,
  "prediction": 0,
  "risk_label": "LOW"
}
```

#### `GET /health`

Returns `{"status": "ok"}` when the API is running.

---

## CML Model Deployment (Production Path)

CML Model Deployments provide a managed, authenticated REST endpoint that runs 24/7 without needing an open session.

> **PBJ runtimes require the `@cml_model` decorator, or every request silently fails.** CML's PBJ runtimes (`ml-runtime-pbj-*`) don't auto-discover the model function by name the way older engines did — `predict()` must be registered with `@cml.models_v1.cml_model`. Without it, the deployment builds and starts fine (`"Model ready"` appears in the log, status turns green), but **every single request fails** with `"failed to execute request"` in the runtime log and a bare `400`/`success: false` on the client side, with no exception or useful message anywhere — the request never actually reaches `predict()`. This was the root cause of a hard-to-diagnose 400 error on this project's `cml_model.py` deployment; the fix is the `@_cml_model` decorator (with a no-op fallback when `cml.models_v1` isn't importable, so direct/local calls to `predict()` — e.g. from `06_debug_predict.py` — still work unchanged) now applied in `cml_model.py`. If you ever see `"Model ready"` followed by requests failing with no other clue, check this first.

### Session API vs Model Deployment

| | Session API (`03_predict.py`) | Model Deployment (`cml_model.py`) |
|---|---|---|
| Lifecycle | Lives only while your session is open | Runs independently, always-on |
| Auth | None (open within session) | Access key required on every request |
| Scaling | Single process | Configurable replicas |
| Entry point | Flask route `POST /predict` | Plain Python function `predict(args)` |
| Port management | Manual (Gunicorn) | Handled entirely by CML |

### Step A — Create CML Jobs for the Pipeline

In CML → **Jobs → New Job**, create each job:

| Job name | Script | Dependency |
|---|---|---|
| `Generate Loan Data` | `01_generate_data.py` | — |
| `Train Credit Risk Model` | `02_train_model.py` | Generate Loan Data |
| `Validate Model KPIs` | `05_validate_model.py` | Train Credit Risk Model |
| `Monitor Data Drift` | `monitoring/10_monitor_drift.py` | — (run on a recurring schedule, not chained to the training jobs) |

Run **Job 1** then **Job 2** in order. This produces `credit_risk_model.pkl` and `label_encoder.pkl` in the project filesystem and logs the run to the **Experiments** tab.

`Monitor Data Drift` is independent of the training chain — schedule it (CML Jobs support cron-style recurrence in the UI) to periodically compare current production data against the reference `loan_data.csv` and catch population shift before it silently degrades predictions. See [Model Monitoring & Drift Detection](#model-monitoring--drift-detection) below.

> The `.pkl` files must exist in the project before deploying the model.

### Step B — Deploy the Model

1. Go to **Models** → **New Model**
2. Fill in the configuration:

   | Field | Value |
   |---|---|
   | Name | `credit-risk-model` |
   | Description | XGBoost loan default predictor |
   | File | `cml_model.py` |
   | Function | `predict` |
   | Kernel | Python 3 |
   | CPU | 1 |
   | Memory | 2 GB |
   | Replicas | 1 |

3. Under **Example Input**, paste:
   ```json
   {
     "loan_amount": 10000,
     "annual_income": 90000,
     "credit_score": 780,
     "employment_years": 10,
     "debt_to_income": 0.15,
     "num_credit_lines": 5,
     "num_delinquencies": 0,
     "loan_purpose": "home"
   }
   ```
4. Click **Deploy Model** and wait for the status badge to turn **green (Running)**.

### Step C — Test the Deployed Model

#### From the CML UI

Model → **Test** tab → example input is pre-filled → click **Run**.

#### Via curl

```bash
curl -X POST https://<your-cml-workspace>/api/v1/projects/<username>/<project>/models/<model-id>/predict \
  -H "Content-Type: application/json" \
  -d '{
    "accessKey": "<your-model-access-key>",
    "request": {
      "loan_amount": 10000,
      "annual_income": 90000,
      "credit_score": 780,
      "employment_years": 10,
      "debt_to_income": 0.15,
      "num_credit_lines": 5,
      "num_delinquencies": 0,
      "loan_purpose": "home"
    }
  }'
```

Response:
```json
{
  "success": true,
  "response": {
    "default_probability": 0.0312,
    "prediction": 0,
    "risk_label": "LOW"
  }
}
```

### Retraining and Redeployment

1. Re-run **Job 2** (Train Credit Risk Model) — new `.pkl` files are written and a new MLflow run is logged
2. Deployed model → **Builds** → **Rebuild** — CML picks up the new `.pkl` files and redeploys with zero downtime

---

## Cloudera AI Registry (Alternative Deployment Path)

`cml_model.py` requires two separate artifacts at load time — `credit_risk_model.pkl` and `label_encoder.pkl`. The **AI Registry** path instead logs the classifier as a single versioned MLflow artifact via `mlflow.xgboost.log_model()` and serves it through CML's **Model Endpoints** (KServe/Triton), independent of `cml_model.py`.

> **Numeric input only, and use the native flavor.** `08_register_in_ai_registry.py` originally wrapped the classifier in a custom `mlflow.pyfunc.PythonModel` so callers could send `loan_purpose="home"` as a raw string. That broke in production: CML's Registry → **Endpoint** path converts models to Triton, and Triton has full native support for well-known MLflow flavors (`mlflow.xgboost.log_model`) but not arbitrary custom `PythonModel` classes — the conversion silently produces a model object that's `None` at serve time, and every inference call fails with `'NoneType' object has no attribute 'predict'` no matter what package versions are installed. The script now logs via the native `xgboost` flavor (same as `02_train_model.py`), which CML's conversion demonstrably supports. The tradeoff: the caller must pre-encode `loan_purpose` to its `LabelEncoder` class index, same numeric contract `cml_model.py`'s classifier already expects — the script prints that mapping at the end of its run.

> **Package versions must match the serving container, not `requirements.txt`.** The Triton image serving Registry endpoints is fixed and (as of this writing) ships `xgboost==3.1.3` / `scikit-learn==1.8.0` / Python 3.12 — unrelated to `cml_model.py`'s pinned `xgboost==1.7.6` / `scikit-learn==1.3.0`, and not configurable via this script's `pip_requirements` (that only documents the training environment; it isn't installed into the serving container). Training under the project's pinned versions produced a pickle the serving image's `xgboost` couldn't load. Before running this script:
> ```bash
> pip install --user "xgboost==3.1.3" "scikit-learn==1.7.2"   # 1.7.2: newest sklearn a Python 3.10 session can install; 1.8.0 needs Python >=3.11
> ```
> Downgrade back (`pip install --user "xgboost==1.7.6" "scikit-learn==1.3.0"`) before touching `02_train_model.py`, `05_validate_model.py`, or rebuilding `cml_model.py`'s Model Deployment in the same session.

> **Signature dtype must be `float32`, not `float64`.** Triton's own tensor config for the endpoint is fixed at `FP32` regardless of what the MLflow signature declares (visible in the endpoint's `/metadata` response). A `float64` signature fails at inference time with `dtype of input float32 does not match expected dtype float64` — mlflow's schema enforcement inside CML's generated `model.py` rejects the mismatch before `predict()` ever runs. `08_register_in_ai_registry.py` declares the signature as `float32` to match.

### Step A — Register a Model Version

```bash
python 08_register_in_ai_registry.py
```

This script:
1. Trains a fresh `XGBClassifier` using the same `FEATURE_ORDER` and hyperparameters as `02_train_model.py`.
2. Logs it via `mlflow.xgboost.log_model()` to the `credit-risk-model` MLflow experiment.
3. Registers the artifact as model name `credit_risk_model` in the Cloudera AI Registry, creating a new version each run.
4. Prints the `loan_purpose` → int mapping callers must pre-encode.

Expected output:
```
run_id: <run-id>
  roc_auc              0.7419
  accuracy             0.665
  ...

registered 'credit_risk_model' version 5

loan_purpose encoding (pass the int, in FEATURE_ORDER position 8):
  auto         -> 0
  business     -> 1
  education    -> 2
  home         -> 3
  personal     -> 4
```

### Step B — Create a Model Endpoint from the Registry

1. In CML, navigate to **Registered Models**, open `credit_risk_model`, and pick the version you just registered.
2. Create/point a **Model Endpoint** at that version (Deployments → Model Endpoints). This is a KServe V2 (Open Inference Protocol) endpoint — a different calling convention than `cml_model.py`'s accessKey-based predict API.

### Step C — Test a Registry-Deployed Model

Use `09_test_registry_endpoint.py`: it authenticates with the session's JWT (`/tmp/jwt`), reads the input tensor's name/shape/datatype from the endpoint's own metadata (no need to guess — CML assigns names like `INPUT__0`), and sends a request built from that. Update `BASE_URL`/`MODEL_NAME` at the top of the script to match your endpoint (from the endpoint's own page — Endpoint Base URL / Model ID), and pre-encode `loan_purpose` in `FEATURES` per the mapping Step A printed:

```bash
pip install open-inference-openapi
python 09_test_registry_endpoint.py
```

Expected response:
```json
{
  "model_name": "<model-id>",
  "model_version": "8",
  "outputs": [
    {
      "name": "OUTPUT__0",
      "shape": [1],
      "datatype": "FP32",
      "data": [0.0]
    }
  ]
}
```

### A Second, Different Way to Deploy a Registered Model

CML has a **second, unrelated** path to serving a Registry model, easy to confuse with Step B above since both start from the same registered `credit_risk_model`:

| | Step B above | This second path |
|---|---|---|
| Where | Workspace-level **Registered Models** → **Model Endpoints** | Inside the **project** → **Model Deployments** → **New Model** → template **"Deploy registered model"** |
| Serving stack | KServe / Triton | Same classic accessKey-based Model API family as `cml_model.py` (same `ml-runtime-pbj-jupyterlab-python*-cuda` base image) |
| Entry point | Auto-converted Triton `model.py` | CML auto-generates its own `predict.py` / `predict_with_metrics` from the registered artifact — not a file in this repo |
| Request format | KServe V2 tensor protocol (`09_test_registry_endpoint.py`) | Presumed accessKey/`request` JSON like `cml_model.py`, unconfirmed — not yet tested end-to-end |

This second path is **not yet validated** in this project — the build completes (same install of `xgboost==3.1.3`/`scikit-learn==1.7.2`/`mlflow==2.19.0` from the registered artifact's `pip_requirements`), but the actual runtime request/response contract of CML's auto-generated `predict_with_metrics` hasn't been confirmed working yet. Treat it as experimental until tested; Step B's KServe Endpoint path above is the confirmed-working route to serve `credit_risk_model` from the Registry.

Note the output is the **predicted class** (`0.0` = no default, `1.0` = default) via the native `xgboost` flavor's default `predict()` — not the richer `{default_probability, prediction, risk_label}` shape `cml_model.py` returns. That convenience lived in the custom pyfunc wrapper, which had to be dropped (see the note above) since custom `PythonModel` classes don't load correctly through CML's Registry → Endpoint conversion.

### Registering a New Version

Re-run `python 08_register_in_ai_registry.py` any time after retraining — it always creates a **new version** under the same `credit_risk_model` name rather than overwriting version 1, so previous versions stay available for rollback in the Registry UI.

---

## Model Monitoring & Drift Detection

A deployed model's predictions silently degrade if the population of loan
applicants shifts over time — the whole reason production ML needs
ongoing monitoring, not just a one-time validation gate. `monitoring/10_monitor_drift.py`
compares a "current" dataset against the reference training distribution
using the **Population Stability Index (PSI)**, a standard, explainable
drift metric:

| PSI | Interpretation |
|---|---|
| < 0.1 | No significant population shift |
| 0.1 – 0.2 | Moderate shift, worth investigating |
| > 0.2 | Significant shift — model likely needs retraining |

```bash
python monitoring/10_monitor_drift.py --reference loan_data.csv --current <new_data>.csv
```

With no arguments it compares `loan_data.csv` against itself (near-zero
PSI, exit 0) — useful as a smoke test. It checks every numeric feature plus
`loan_purpose` (categorical PSI), logs results to MLflow under the
`credit-risk-model-monitoring` experiment when MLflow is available (same
skip-if-absent pattern as `02_train_model.py`), and exits non-zero if any
feature crosses the significant-drift threshold — making it usable as a
CML Job gate, scheduled independently of the training chain (see the Jobs
table above).

> Covers **data (covariate) drift** only. Concept/label drift would need
> ground-truth outcomes arriving after the fact, which this synthetic
> workshop dataset has no mechanism to simulate.

---

## Interactive Prediction App (CML Application)

`app/app.py` is a small Streamlit form UI for attendees who'd rather click
through a form than use curl/Python to hit the API — same inference
contract as `03_predict.py`/`cml_model.py`.

**Local dev:**
```bash
streamlit run app/app.py
```

**As a CML Application:** Applications → New Application →
- Script: `app/app.py`
- Command:
  ```bash
  streamlit run app/app.py --server.port $CDSW_APP_PORT --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false
  ```
  (CORS/XSRF checks must be disabled because CML serves Applications through
  a reverse proxy.)

> **Experimental — not yet validated as a live CML Application.** Local
> `streamlit run` was verified; launching it as an actual CML Application
> (port binding under `CDSW_APP_PORT`, the reverse proxy path) has not been
> tested against a real workspace. Treat it the same way this README
> already treats the untested second Registry deployment path above.

---

## CI/CD Pipeline (GitHub Actions)

Every push to `main` automatically retrains and validates the model.

```
Push to main
     ↓
GitHub Actions fires (.github/workflows/retrain.yml)
     ↓
Step 1: pip install -r requirements.txt
     ↓
Step 2: python 01_generate_data.py   → loan_data.csv
     ↓
Step 3: python 02_train_model.py     → credit_risk_model.pkl
     ↓
Step 4: python 05_validate_model.py
     ↓
✅ ROC-AUC ≥ 0.75 AND F1 ≥ 0.60 → pipeline green
❌ Either threshold missed        → pipeline red
```

No secrets or external services required — the pipeline runs entirely within GitHub Actions.

### KPI thresholds

Defined at the top of `05_validate_model.py`:

```python
ROC_AUC_MIN    = 0.72
F1_DEFAULT_MIN = 0.50
```

These are calibrated to realistic performance on the synthetic dataset. Raise them when switching to real loan data.

---

## Dependencies

| Package | Purpose |
|---|---|
| `pandas` | Data manipulation |
| `numpy<2.0` | Numerical operations (pinned for scikit-learn 1.3.0 compatibility) |
| `scikit-learn==1.3.0` | Preprocessing, metrics |
| `xgboost==1.7.6` | Gradient boosted classifier |
| `flask` | REST API framework (session path only) |
| `joblib==1.3.2` | Model serialization |
| `gunicorn` | WSGI server for session-based serving |
| `requests` | HTTP client for test script |
| `mlflow` | Experiment tracking — pre-installed by CML via `mlflow-cml-plugin`, do not add to `requirements.txt` |
