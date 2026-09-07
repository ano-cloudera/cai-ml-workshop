# Tasks: Feature Engineering and Feature Store

- [ ] Implement `features/engineering.py` (three engineered features with documented rationale)
- [ ] Implement `features/store.py` (versioned Parquet feature table, `get_features()`)
- [ ] Add `pyarrow` to `requirements.txt`
- [ ] Update `02_train_model.py` to use the shared feature module
- [ ] Update `03_predict.py` to use the shared feature module
- [ ] Update `cml_model.py` to use the shared feature module
- [ ] Update `05_validate_model.py` to use the shared feature module
- [ ] Update `08_register_in_ai_registry.py` to use the shared feature module
- [ ] Update `app/app.py` to use the shared feature module
- [ ] Retrain and regenerate `credit_risk_model.pkl` / `label_encoder.pkl` against the new feature set
- [ ] Test full pipeline end to end locally (generate, train, validate, predict)
- [ ] Add README.md "Feature Engineering and Feature Store" section, marked optional/bonus
- [ ] Verify AI Registry and CML Application paths against the new feature set (user's environment)
