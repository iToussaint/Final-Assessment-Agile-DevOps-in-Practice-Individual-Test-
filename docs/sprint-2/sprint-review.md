# Sprint 2 – Sprint Review

| | |
|---|---|
| **Sprint goal** | *A librarian can lend and receive books (including e-books and audiobooks), the manager can see stock and lending reports, and a maintainer can check health and read logs — with a stronger CI quality gate than Sprint 1.* |
| **Goal met?** | ✅ **Yes** |
| **Committed / delivered** | 14 committed + 3 stretch → **17 / 17 points delivered** (5 / 5 stories) |
| **Velocity** | **17 points** (Sprint 1: 13) |
| **Release** | `v0.2.0` — packaged automatically as `library-inventory-0.2.0.zip` by the CD job |

## Delivered backlog items

| ID | Story | Pts | Status | Branch |
|---|---|---|---|---|
| US-08 | Health check & logging | 3 | ✅ Done | `feature/US-08-health-logging` |
| US-04 | Register borrowers & borrow a book | 5 | ✅ Done | `feature/US-04-borrow-book` |
| US-05 | Return a book & borrowing history | 3 | ✅ Done | `feature/US-05-return-book` |
| US-07 | Reports | 3 | ✅ Done | `feature/US-07-reports` |
| US-06 | E-books & audiobooks (stretch) | 3 | ✅ Done | `feature/US-06-ebook-audiobook` |
| – | Sprint 1 retro actions A1, A2, A3, A6 | – | ✅ Done | `ci/sprint-1-retro-actions` |
| – | Continuous delivery: release zip artifact | – | ✅ Done | `ci/release-artifact` |

## Sprint 1 retrospective actions — applied

| Action | Result | Evidence |
|---|---|---|
| **A1** ruff lint + format job gating tests | ✅ Immediately found 1 long line and 2 unformatted files in Sprint 1 code — fixed in `style(retro-A1)` commit | `lint` job in [ci.yml](../../.github/workflows/ci.yml); [lint-results.txt](evidence/lint-results.txt) |
| **A2** coverage ≥ 90 % + reports as artifacts | ✅ The gate **failed a real build**: logging code was pushed before its tests (coverage 84.18 %) and the branch went red until the tests were committed | `--cov-fail-under=90`; artifacts `test-reports-py3.x` on every run |
| **A3** Python 3.10 / 3.12 / 3.13 matrix | ✅ All three green on every run | `Tests (Python 3.x)` jobs |
| **A4** push each branch early, merge only when green | ✅ Every Sprint 2 branch has its own CI runs (17 branch runs) before its merge | Actions tab, filter by branch |
| **A5** logging first | ✅ US-08 moved to the top; US-04/05/07 log from their first commit | `library.inventory`/`library.reports` log lines |
| **A6** `.editorconfig`, LF JSON | ✅ No encoding issues this sprint | `.editorconfig`, `storage.py` |
| **A7** CLI smoke test in CI | ✅ Smoke job drives the real CLI and probes a live `GET /health` | `CLI smoke test & health endpoint` job |

## Acceptance criteria check

| Story | AC | Evidence (tests) | Result |
|---|---|---|---|
| US-08 | AC8.1 `health` JSON + exit code | `test_health_command_prints_json_and_exit_code`, demo | ✅ |
| | AC8.2 `GET /health` 200 / 503 | `test_http_health_returns_200_when_healthy`, `…_503_when_unhealthy`, `…_404` | ✅ |
| | AC8.3 state changes logged | `test_state_changes_are_logged_to_file`, `test_report_generation_is_logged` | ✅ |
| | AC8.4 console + rotating file, tracebacks for unexpected errors | `test_unexpected_error_is_tracked_with_traceback`, `test_console_is_quiet_by_default_and_verbose_with_v` | ✅ |
| US-04 | AC4.1 register, duplicate e-mail rejected | `test_add_borrower_assigns_member_id`, `test_duplicate_email_is_rejected` | ✅ |
| | AC4.2 borrow updates book, borrower, history | `test_borrow_updates_book_borrower_and_history` | ✅ |
| | AC4.3 already on loan rejected | `test_cannot_borrow_a_book_already_on_loan` | ✅ |
| | AC4.4 max 3 loans | `test_loan_limit_is_enforced_without_side_effects` | ✅ |
| | AC4.5 unknown ids → not found | `test_unknown_ids_raise_not_found` | ✅ |
| US-05 | AC5.1 / AC5.2 return closes loan with date | `test_return_makes_book_available_and_frees_borrower_slot` | ✅ |
| | AC5.3 return of book not on loan rejected | `test_returning_a_book_not_on_loan_is_rejected` | ✅ |
| | AC5.4 history persisted & filterable | `test_history_can_be_filtered_by_borrower`, `test_history_with_return_dates_is_persisted` | ✅ |
| US-07 | AC7.1 – AC7.5 reports via comprehensions | `tests/test_reports.py` (13 tests) | ✅ |
| US-06 | AC6.1 subclasses use `super()` | `test_subclasses_extend_book_and_call_super`, `test_subclass_reuses_parent_validation` | ✅ |
| | AC6.2 extra fields validated | `test_ebook_rejects_invalid_fields`, `test_audiobook_rejects_invalid_fields` | ✅ |
| | AC6.3 `__repr__`/`describe`/serialisation, correct subclass on load | `test_repr_and_describe_extend_parent_output`, `test_round_trip_restores_the_correct_subclass` | ✅ |
| | AC6.4 behave like books (search, borrow, report) | `test_mixed_library_search_borrow_report_and_persist` | ✅ |

## Demo

Full transcript: [evidence/cli-demo.txt](evidence/cli-demo.txt). Highlights:

```text
$ python main.py borrow B002 M001
Error: Ama Mensah has reached the loan limit                       (exit code 1)

$ python main.py report borrowed
Borrowed books (3)
[B008] Americanah -> Ama Mensah (M001)
[B009] No Longer at Ease -> Ama Mensah (M001)
[B001] Things Fall Apart -> Ama Mensah (M001)

$ python main.py list
[B008] Americanah by Chimamanda Ngozi Adichie (2013, Novel) ISBN 9780307455925 - available | e-book EPUB, 2.4 MB
[B009] No Longer at Ease by Chinua Achebe (1960, Novel) ... | audiobook read by Peter Francis James, 6h 30m

$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/health
200
```

## Testing evidence

- **128 tests, 128 passed, coverage 96.77 %** (gate: 90 %) — [evidence/test-results.txt](evidence/test-results.txt)
- Lint: `ruff check` and `ruff format --check` clean — [evidence/lint-results.txt](evidence/lint-results.txt)
- New test modules: `test_logging.py`, `test_health.py` (incl. a real HTTP server on a free port),
  `test_borrowing.py`, `test_returns.py`, `test_reports.py`, `test_book_types.py`.

## CI/CD evidence

Pipeline ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)) on `main` after the last merge:

| Job | Result |
|---|---|
| Lint & format check | ✅ |
| Tests (Python 3.10) | ✅ |
| Tests (Python 3.12) | ✅ |
| Tests (Python 3.13) | ✅ |
| CLI smoke test & health endpoint | ✅ |
| Package release artifact | ✅ `library-inventory-0.2.0` |

Two **red builds** happened during the sprint and are kept visible in the Actions history:

1. `feature/US-08-health-logging` @ `c4c691f` — coverage gate failed at 84.18 % (logging module
   pushed before its tests). Fixed by `d102c28` (tests).
2. `feature/US-08-health-logging` @ `a042fca` — workflow file invalid (`runner` context is not
   allowed in job-level `env`). Fixed by `4d2c410`.

Neither reached `main`, which is exactly what the branch-first workflow (A4) is for.

## Definition of Done check

| DoD item | Status |
|---|---|
| All AC met | ✅ |
| Unit + integration tests; suite green locally and in CI | ✅ |
| Lint clean, coverage ≥ 90 % | ✅ (new in Sprint 2) |
| One branch per story, merged with `--no-ff` after a green branch build | ✅ |
| README updated (usage, monitoring, CI/CD, design) | ✅ |

## Product backlog after Sprint 2

| ID | Story | Pts | Status |
|---|---|---|---|
| US-01 … US-08 | | 30 | ✅ Done |
| US-09 | Update / remove a book | 2 | Backlog (Could) |
| US-10 | Due dates & overdue report | 5 | Backlog (Could) |

**Burn-up:** 0 → 13 (Sprint 1) → 30 (Sprint 2) of 37 points. All *Must* and *Should* stories are done.
