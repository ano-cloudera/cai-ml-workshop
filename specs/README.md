# Spec-Kit for This Workshop

Every non-trivial change to this project goes through a spec before code. This
follows the [GitHub spec-kit](https://github.com/github/spec-kit) convention:
spec, then plan, then tasks, then implementation.

## Layout

```
specs/
  <NN>-<feature-slug>/
    spec.md    # what and why: problem statement, acceptance criteria
    plan.md    # how: technical approach, files touched, risks
    tasks.md   # checklist tracking implementation
```

Feature folders are numbered in the order they were introduced, not the order
they must ship. Check each `spec.md` for actual dependencies between
features.

## Existing features

| Folder | Summary | Status |
|---|---|---|
| [00-repo-hardening](00-repo-hardening/spec.md) | Secret removal, stray-file cleanup, hardcoded-value templating | Done |
| [01-cicd-retrain-workflow](01-cicd-retrain-workflow/spec.md) | GitHub Actions workflow that retrains and gates on KPIs on every push | Done |
| [02-model-monitoring](02-model-monitoring/spec.md) | Data drift detection module (PSI-based) runnable as a CML Job | Done |
| [03-amp-prediction-app](03-amp-prediction-app/spec.md) | Streamlit prediction UI, deployable as a CML Application | Done |
| [04-jobs-as-code](04-jobs-as-code/spec.md) | Job definition manifest for the four-job lifecycle chain, plus an audience/scope disclaimer in README | Planned |
| [05-cicd-api-trigger](05-cicd-api-trigger/spec.md) | GitHub Actions calls the CML API v2 to trigger a real Job in the workspace, not just a GitHub-runner smoke test | Planned |
| [06-feature-engineering-store](06-feature-engineering-store/spec.md) | Engineered features plus a lightweight, versioned feature store shared across every consumer script | Planned |

Features 04 through 06 were opened in response to internal review feedback
(SE India, 2026-09-04). Recommended build order: 04 first (cheapest, closes
the review's main overall comment), then 05 (highest effort, most visible
gap), then 06 (the reviewer's own bonus-tier item).

## Adding a new feature

1. Create `specs/<next-number>-<slug>/`.
2. Write `spec.md` first: the problem, who needs it, and acceptance criteria
   that don't presuppose an implementation.
3. Write `plan.md`: the technical approach, which existing files or patterns
   in this repo it builds on (reuse `FEATURE_ORDER`, the `_mlflow_available`
   guard pattern, and so on rather than reinventing them), and what's out
   of scope.
4. Write `tasks.md` as a checklist, then implement against it.
5. Update this table.

## Security note

Never hardcode access keys, tokens, or workspace-specific URLs into a
committed script. Follow the pattern already used in `07_test_model_deployment.py`
and `09_test_registry_endpoint.py`: read from an environment variable, with
`getpass` as an interactive fallback for secrets (never for URLs, since those
are just config, not secret, so a hard failure with instructions is enough).
A hardcoded access key was found and removed from this repo during the
`00-repo-hardening` pass. See that spec for details.
