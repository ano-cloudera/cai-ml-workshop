"""
Interactive credit risk prediction UI (Streamlit).

Local dev:
    streamlit run app/app.py

CML Application (Applications -> New Application):
    Script  : app/app.py
    Command : streamlit run app/app.py --server.port $CDSW_APP_PORT \\
              --server.address 0.0.0.0 --server.enableCORS false \\
              --server.enableXsrfProtection false
    (CORS/XSRF protection must be disabled because CML serves Applications
    through a reverse proxy — same reasoning Streamlit's own docs give for
    any iframed/proxied deployment.)

NOT YET VALIDATED as a live CML Application (this environment cannot launch
one) — only local `streamlit run` was verified. See
specs/03-amp-prediction-app/spec.md.
"""

import os

import joblib
import numpy as np
import streamlit as st

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


@st.cache_resource
def load_artifacts():
    project_dir = os.environ.get("CDSW_PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model = joblib.load(os.path.join(project_dir, "credit_risk_model.pkl"))
    le = joblib.load(os.path.join(project_dir, "label_encoder.pkl"))
    model.set_params(nthread=1)
    return model, le


st.set_page_config(page_title="Credit Risk Predictor", page_icon="\U0001F3E6")
st.title("Credit Risk Predictor")
st.caption("XGBoost loan default classifier — Cloudera AI MLOps Workshop")

model, le = load_artifacts()

with st.form("predict_form"):
    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input("Loan amount ($)", 1000, 50000, 10000, step=500)
        annual_income = st.number_input("Annual income ($)", 20000, 150000, 60000, step=1000)
        credit_score = st.number_input("Credit score", 300, 850, 700, step=10)
        employment_years = st.number_input("Employment years", 0, 30, 5, step=1)
    with col2:
        debt_to_income = st.slider("Debt-to-income ratio", 0.05, 0.75, 0.30, step=0.01)
        num_credit_lines = st.number_input("Number of credit lines", 1, 20, 5, step=1)
        num_delinquencies = st.number_input("Number of delinquencies", 0, 10, 0, step=1)
        loan_purpose = st.selectbox("Loan purpose", list(le.classes_))

    submitted = st.form_submit_button("Predict")

if submitted:
    loan_purpose_encoded = le.transform([loan_purpose])[0]
    values = [
        loan_amount, annual_income, credit_score, employment_years,
        debt_to_income, num_credit_lines, num_delinquencies, loan_purpose_encoded,
    ]
    prob = model.predict_proba(np.array([values], dtype=np.float64))[0][1]
    prediction = int(prob >= 0.5)
    risk_label = "HIGH" if prediction == 1 else "LOW"

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Default probability", f"{prob:.2%}")
    c2.metric("Prediction", "Default" if prediction else "No default")
    c3.metric("Risk label", risk_label, delta=None,
              delta_color="inverse" if risk_label == "HIGH" else "normal")
    if risk_label == "HIGH":
        st.error("High risk of default.")
    else:
        st.success("Low risk of default.")
