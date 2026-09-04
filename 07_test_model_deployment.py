"""
Script 7: Call the deployed CML Model Deployment endpoint directly and
print the full raw response, to see the actual error message behind a
generic success:false / 400 result.

The access key is read from the MODEL_ACCESS_KEY env var, or prompted for
interactively if not set — it is never hardcoded or committed to git.
The model service URL is read from MODEL_URL — copy it from the
Model Deployment's own page (Models -> your model -> the endpoint shown
under the Settings/Test tab), it is workspace- and model-specific.

Run from a CML session terminal:
    export MODEL_URL=https://modelservice.<your-workspace>/model
    export MODEL_ACCESS_KEY=<your model access key>
    python 07_test_model_deployment.py
"""

import getpass
import os

import requests

MODEL_URL = os.environ.get("MODEL_URL")
if not MODEL_URL:
    raise SystemExit(
        "ERROR: MODEL_URL not set. Export it from your Model Deployment's "
        "own page, e.g.:\n"
        "  export MODEL_URL=https://modelservice.<your-workspace>/model"
    )

access_key = os.environ.get("MODEL_ACCESS_KEY") or getpass.getpass("Model access key: ")

payload = {
    "accessKey": access_key,
    "request": {
        "loan_amount": 10000,
        "annual_income": 90000,
        "credit_score": 560,
        "employment_years": 10,
        "debt_to_income": 0.15,
        "num_credit_lines": 5,
        "num_delinquencies": 0,
        "loan_purpose": "home",
    },
}

r = requests.post(MODEL_URL, json=payload)
print(f"Status code: {r.status_code}")
print(f"Response body:\n{r.text}")
