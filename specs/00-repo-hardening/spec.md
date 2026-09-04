# Spec: Repo Hardening

## Problem

This project was handed over from another team for review before being
pushed to a shared GitHub remote. Review turned up:

1. `API_TEST_MODELDEP.py` — a committed script hardcoding a live-looking CML
   Model Deployment access key and a real workspace URL in plaintext. This
   is a credential leak: anyone with read access to the git history gets a
   working key, permanently, even if the file is later deleted (git retains
   history unless it's rewritten).
2. The README documents `.github/workflows/retrain.yml` as part of the
   project, but the file does not exist in the repo — the CI/CD section was
   aspirational or lost in transfer.
3. `Untitled.ipynb` — an empty scratch notebook (one cell contains a shell
   command typed into a Python kernel, producing a `SyntaxError`; the second
   cell is empty). No real content.
4. `07_test_model_deployment.py` and `09_test_registry_endpoint.py` hardcode
   one specific workspace's URLs and model/endpoint IDs, making them
   unusable as-is in any other workspace without manual editing (and prone
   to someone re-committing their own workspace's values later).
5. `README (1).md` — filename suggests a duplicate-download artifact rather
   than the intended canonical name.

## Acceptance Criteria

- No access keys, tokens, or other secrets exist anywhere in the working
  tree or in any git commit made from this point forward.
- The repo's file tree matches what the README documents (or the README is
  updated to match reality).
- Scripts that need a workspace-specific URL/ID fail loudly with setup
  instructions when the value isn't provided, rather than silently using
  someone else's workspace.
- No stray/empty files ship in the initial commit.

## Out of scope

- Rewriting git history (there is no prior history — this is the first
  commit, so the leaked key was never actually pushed anywhere; if this
  repo *had* prior history containing the key, that would need `git filter-repo`
  or BFG, and the leaked key would still need rotating in CML regardless of
  history rewriting).
- Rotating the leaked access key in the actual CML workspace — that's a
  credential-owner action the source team must take themselves, since the
  key material was for their environment, not something creatable/revocable
  from here. **Flag this to them explicitly when handing feedback back.**
