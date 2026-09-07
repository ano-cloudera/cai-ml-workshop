# Tasks: API-Triggered CI/CD (GitHub to CML)

- [ ] Add `10_trigger_cml_job.py` (env-var config, CML API v2 call, poll and gate on run status)
- [ ] Test locally: missing env vars fail loudly with setup instructions
- [ ] Add CML-trigger step/workflow gated on the KPI validation step
- [ ] Write `specs/05-cicd-api-trigger/setup.md` with the API key and GitHub Secret click-path
- [ ] Update README.md CI/CD section with the opt-in extended flow
- [ ] Verify an actual trigger run against a live CML workspace (user's environment, requires real API key)
