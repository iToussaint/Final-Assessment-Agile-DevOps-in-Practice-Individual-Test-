# Sprint 2 – Retrospective

Format: **What went well / What didn't / Lessons learned / Improvements for the next sprint**,
plus a comparison with Sprint 1 to check that the Sprint 1 improvements actually helped.

## Did the Sprint 1 improvements work?

| Sprint 1 problem | Action taken | Outcome in Sprint 2 |
|---|---|---|
| P1 weak quality gate | A1 lint job, A2 coverage ≥ 90 %, A7 smoke test | **Worked.** The lint job caught 3 style issues in existing code; the coverage gate turned a branch red at 84 % when code was pushed without tests; the smoke test proves the real CLI and `/health` work on every build. |
| P2 single Python version | A3 matrix 3.10 / 3.12 / 3.13 | **Worked.** No version-specific failure, and we now *know* the README's "3.10+" claim is true. |
| P3 branches never built before merge | A4 push early, merge only when green | **Worked.** 17 branch builds; both red builds of the sprint were caught on a branch and never reached `main`. |
| P4 no logging | A5 logging first | **Worked.** Borrow/return/report code logged from its first commit; the log made the demo easy to verify (4 loan/return events recorded). |
| P5 encoding surprises | A6 `.editorconfig`, LF JSON | **Worked.** No encoding issues. |

## What went well
- **Velocity went up from 13 to 17 points** and the stretch story (US-06) was delivered. The
  Sprint 1 foundations (ABC, `to_dict`/`from_dict`, the `_kwargs_from_dict` hook) made e-books and
  audiobooks cheap: subclasses only add their own fields and call `super()`.
- **"Check every rule before changing state"** (from Sprint 1) was re-used in `borrow_book()` —
  a refused loan never leaves a book half-borrowed (`test_loan_limit_is_enforced_without_side_effects`).
- **Real continuous delivery:** every green `main` build now produces a versioned zip that is
  unpacked and health-checked in a clean folder before upload.
- **Monitoring is testable:** the HTTP health endpoint is tested against a real server on a free
  port, not mocked.

## What didn't go well

| # | Observation | Impact |
|---|---|---|
| P6 | **Code pushed before its tests** (logging module) → coverage gate failed the branch build. | One red build; the gate did its job, but the feedback came from CI instead of before the push. |
| P7 | **Invalid workflow file pushed** (`runner` context used in job-level `env`). GitHub rejected the whole run, so no job ran at all. | One red build and a fix commit; YAML errors are only found after pushing. |
| P8 | **The packaging (CD) job only runs on `main`/tags**, so it could not be verified on its branch before merging. | Risk of breaking `main` with an untested job (it passed first time, but by luck rather than by design). |
| P9 | **A scripted edit broke `main.py`** (an escaped `\n` became a real newline). Caught immediately by running the tests locally, but it shows edits can slip. | Minutes lost; would have been a red build if not checked locally. |
| P10 | **Estimates were pessimistic** for US-06 / US-07 (3 pts each, delivered faster than US-04 at 5). | Sprint commitment (14) was below real capacity (17). |
| P11 | `LibraryResource` base methods (`__repr__`/`__eq__` fallbacks) are only 78 % covered, because every subclass overrides them. | Small blind spot in the coverage report. |

## Lessons learned
1. **Quality gates only help if they can fail.** The coverage and lint gates paid for themselves
   in this sprint — keep the thresholds and treat a red build as useful feedback, not a nuisance.
2. **Shift checks left.** Two of the problems (P6, P9) could have been caught *before* the push by
   running the same checks locally; P7 by validating the workflow file before pushing.
3. **Build the right thing first.** Moving logging to the start of the sprint made every later
   story easier to debug and demonstrate — infrastructure stories are worth prioritising early.
4. **Re-estimate with real data.** Velocity is now 13 → 17; the next sprint can plan for ~15 points
   with confidence.

## Improvements for the next sprint (Sprint 3) — action items

| # | Action | Addresses |
|---|---|---|
| **B1** | Add **pre-commit hooks** (`ruff check`, `ruff format`, `pytest -q`) so the same gates run before each commit. | P6, P9 |
| **B2** | Add an **`actionlint` step** to validate workflow files in CI (and run it locally before pushing workflow changes). | P7 |
| **B3** | Run the **package job on every branch as a dry run** (build + verify), but upload the artifact only on `main`/tags. | P8 |
| **B4** | Write **tests in the same commit** as new behaviour (or first — TDD) for business rules. | P6 |
| **B5** | Re-baseline estimates with the reference story and plan Sprint 3 at **~15 points**. | P10 |
| **B6** | Add **direct tests for `LibraryResource`** via a minimal concrete test subclass. | P11 |
| **B7** | Move to **pull requests with branch protection** on `main` (required green CI check) instead of local `--no-ff` merges, so the "merge only when green" rule is enforced by GitHub, not by discipline. | P3 (hardening) |
| **B8** | For US-10 (due dates) introduce an **injectable clock** so date-dependent logic is testable without depending on the wall-clock. | upcoming work |

## Sprint comparison

| Metric | Sprint 1 | Sprint 2 |
|---|---|---|
| Velocity (points) | 13 | 17 |
| Stories delivered | 3 | 5 |
| Tests | 53 | 128 |
| Coverage | not measured (94 % when first measured) | 96.77 % (gate 90 %) |
| CI jobs per run | 1 | 6 (lint, 3× tests, smoke, package) |
| Python versions tested | 1 | 3 |
| Branch builds before merge | 0 | 17 |
| Red builds reaching `main` | 0 | 0 |
| Commits (excluding merges) | 21 | 36 |
