# Tasks: Model Monitoring & Drift Detection

- [x] Implement `monitoring/10_monitor_drift.py` (PSI numeric + categorical, MLflow guard, exit code gate)
- [x] Test: self-comparison (`loan_data.csv` vs itself) — expect near-zero PSI, exit 0
- [x] Test: synthetically shifted copy — expect elevated PSI, exit 1
- [x] Update `README.md` Jobs table + add Monitoring section
- [ ] Verify MLflow logging renders correctly in CML's Experiments tab (user's environment)
