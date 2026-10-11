# Sprint 2 – Sprint Plan

| | |
|---|---|
| **Sprint** | 2 (simulated, time-boxed to one working session) |
| **Dates** | Sun 11 Oct 2026 |
| **Team** | 1 developer — Product Owner, Scrum Master and Developer roles |
| **Previous velocity** | 13 pts |
| **Capacity** | ~14 pts committed + 3 pts stretch, plus the Sprint 1 retrospective actions |

## Sprint Goal

> *"A librarian can lend and receive books (including e-books and audiobooks), the manager can
> see stock and lending reports, and a maintainer can check health and read logs — with a
> stronger CI quality gate than Sprint 1."*

## Step 1 — apply the Sprint 1 retrospective actions first

| Action | Task | Branch |
|---|---|---|
| A6 | `.editorconfig` (UTF-8, LF); JSON written with `\n` newlines | `ci/sprint-1-retro-actions` |
| A1 | `ruff` lint + format-check job; test job `needs: lint` | `ci/sprint-1-retro-actions` |
| A2 | `pytest-cov` with `--cov-fail-under=90`; upload coverage + JUnit XML artifacts | `ci/sprint-1-retro-actions` |
| A3 | Python matrix 3.10 / 3.12 / 3.13 | `ci/sprint-1-retro-actions` |
| A4 | Push every branch on its first commit and before merging; merge only when its build is green | all branches |
| A5 | Build logging **first** (US-08) so later stories log from day one | `feature/US-08-health-logging` |
| A7 | CLI smoke-test step in CI (`add-book` → `list` → `health`) | `feature/US-08-health-logging` |

## Selected backlog items

| Order | ID | Story | Points | Commitment |
|---|---|---|---|---|
| 1 | US-08 | Health check & logging | 3 | Committed (moved first — retro A5) |
| 2 | US-04 | Register borrowers & borrow a book | 5 | Committed |
| 3 | US-05 | Return a book & borrowing history | 3 | Committed |
| 4 | US-07 | Reports (available, borrowed, by author, summary) | 3 | Committed |
| 5 | US-06 | E-books & audiobooks | 3 | **Stretch** |
| | | **Committed / with stretch** | **14 / 17** | |

US-09 (update/remove, *Could*) and US-10 (due dates, *Could*) stay in the product backlog.

## Task breakdown

### US-08 – Health check & logging
- [ ] `library/logging_config.py`: console handler (stderr, `-v` for INFO/DEBUG) + rotating file `logs/library.log`
- [ ] Log every state change in `Library`/`storage`; log unexpected exceptions with traceback in `main()`
- [ ] `library/health.py`: `check_health()` → data dir writable, data file valid, record counts
- [ ] `health` CLI command (JSON output, exit 0/1) and `serve-health` HTTP `GET /health` (200/503)
- [ ] Tests for logging, health check and the HTTP endpoint

### US-04 – Borrow
- [ ] `LoanRecord` (book id, borrower id, borrowed_at, returned_at)
- [ ] `Borrower` loan management with `MAX_LOANS = 3`
- [ ] `add_borrower()`, `borrow_book()` + CLI `add-borrower`, `borrowers`, `borrow`
- [ ] Persist borrowers and history; tests

### US-05 – Return & history
- [ ] `return_book()`, `get_history()` + CLI `return`, `history [--borrower]`; tests

### US-07 – Reports
- [ ] `library/reports.py` with list/dict comprehensions; CLI `report {available,borrowed,by-author,summary}`; tests

### US-06 – E-books & audiobooks (stretch)
- [ ] `EBook`, `AudioBook` extend `Book` using `super()`; polymorphic load from JSON
- [ ] CLI `add-book --type ebook|audiobook …`; tests

## Risks
- Borrowing touches both `Book` and `Borrower` state — must stay consistent if validation fails
  (re-use the "validate before storing" pattern from Sprint 1).
- Stricter CI (lint + coverage) may fail on existing code — fix immediately as part of the CI branch.
