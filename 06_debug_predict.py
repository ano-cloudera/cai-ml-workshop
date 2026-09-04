"""
Script 6: Debug the CML Model Deployment predict() function locally.

Calls cml_model.predict() directly with the same payload used in the
failed Model Deployment test, so the full traceback (if any) prints to
this terminal instead of being swallowed by the deployment wrapper.

Run from the project root in a CML session (after the .pkl artifacts exist):
    python 06_debug_predict.py
"""

import traceback

payload = {
    "loan_amount": 10000,
    "annual_income": 90000,
    "credit_score": 560,
    "employment_years": 10,
    "debt_to_income": 0.15,
    "num_credit_lines": 5,
    "num_delinquencies": 0,
    "loan_purpose": "home",
}

print(f"Testing predict() with payload:\n{payload}\n")

try:
    from cml_model import predict
    result = predict(payload)
    print(f"Result: {result}")
except Exception:
    print("predict() raised an exception:\n")
    traceback.print_exc()
