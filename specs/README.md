# Spec-Kit for This Workshop

Every non-trivial change to this project goes through a spec before code. This
follows the [GitHub spec-kit](https://github.com/github/spec-kit) convention:
spec → plan → tasks → implementation.

## Layout

```
specs/
  <NN>-<feature-slug>/
    spec.md    # what and why — problem statement, acceptance criteria
    plan.md    # how — technical approach, files touched, risks
    tasks.md   # checklist tracking implementation
```

Feature folders are numbered in the order they were introduced, not the order
they must ship — check each `spec.md` for actual dependencies between
features.

## Existing features

| Folder | Summary |
|---|---|
| [00-repo-hardening](00-repo-hardening/spec.md) | Secret removal, stray-file cleanup, hardcoded-value templating |
| [01-cicd-retrain-workflow](01-cicd-retrain-workflow/spec.md) | GitHub Actions workflow that retrains and gates on KPIs on every push |
| [02-model-monitoring](02-model-monitoring/spec.md) | Data drift detection module (PSI-based) runnable as a CML Job |
| [03-amp-prediction-app](03-amp-prediction-app/spec.md) | Streamlit prediction UI, deployable as a CML Application |

## Adding a new feature

1. Create `specs/<next-number>-<slug>/`.
2. Write `spec.md` first — the problem, who needs it, and acceptance criteria
   that don't presuppose an implementation.
3. Write `plan.md` — the technical approach, which existing files/patterns in
   this repo it builds on (reuse `FEATURE_ORDER`, the `_mlflow_available`
   guard pattern, etc. — don't reinvent them), and what's out of scope.
4. Write `tasks.md` as a checklist, then implement against it.
5. Update this table.

## Security note

Never hardcode access keys, tokens, or workspace-specific URLs into a
committed script. Follow the pattern already used in `07_test_model_deployment.py`
and `09_test_registry_endpoint.py`: read from an environment variable, with
`getpass` as an interactive fallback for secrets (never for URLs — those are
just config, not secret, so a hard failure with instructions is enough).
A hardcoded access key was found and removed from this repo during the
`00-repo-hardening` pass — see that spec for details.
