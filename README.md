# Library Inventory Application

[![CI/CD](https://github.com/iToussaint/Final-Assessment-Agile-DevOps-in-Practice-Individual-Test-/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/iToussaint/Final-Assessment-Agile-DevOps-in-Practice-Individual-Test-/actions/workflows/ci.yml)

A command-line application for managing a small library's **books, e-books, audiobooks,
authors and borrowers**, built over two simulated sprints as the *Agile & DevOps in Practice*
final assessment.

> **Product vision:** For small community and school libraries that still track their stock on
> paper, Library Inventory is a lightweight command-line application that lets a librarian
> catalogue books, e-books and audiobooks, lend them to borrowers and instantly see what is
> available — with every record safely persisted to a JSON file.

## Getting started

Requires **Python 3.10+**. The application uses only the standard library.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt

pytest --cov=library --cov=main      # run the tests with coverage
ruff check . && ruff format --check . # lint
```

## Usage

Data is stored in `data/library.json` (override with `--data PATH` or the
`LIBRARY_DATA_FILE` environment variable). Run `python main.py --help` for every command.

```bash
# catalogue items (repeat --author for co-authors)
python main.py add-book --title "Things Fall Apart" --author "Chinua Achebe" \
    --isbn 9780385474542 --genre Novel --year 1958
python main.py add-book --type ebook --format EPUB --size-mb 2.4 --title "Americanah" \
    --author "Chimamanda Ngozi Adichie" --isbn 9780307455925 --genre Novel --year 2013
python main.py add-book --type audiobook --narrator "Peter Francis James" --duration 390 \
    --title "No Longer at Ease" --author "Chinua Achebe" --isbn 9780385474559 --genre Novel --year 1960

# search by title and/or author (case-insensitive, partial match) and list
python main.py search achebe
python main.py search "yellow sun" --field title
python main.py list

# borrowers and lending (max 3 books per borrower)
python main.py add-borrower --name "Ama Mensah" --email ama@example.com
python main.py borrowers
python main.py borrow B001 M001
python main.py return B001
python main.py history --borrower M001

# reports
python main.py report available     # | borrowed | by-author | by-genre | summary
```

## Monitoring & logging

```bash
# health check: prints a JSON status, exit code 0 (ok) or 1 (error)
python main.py health

# the same check over HTTP: GET http://127.0.0.1:8080/health -> 200 ok / 503 error
python main.py serve-health --port 8080

# show logs on the console as well (-v = INFO, -vv = DEBUG)
python main.py -v borrow B001 M001
```

- Every state change (book added, loan, return, save, report…) is logged to `logs/library.log`
  (rotating, 1 MB × 3 backups; override with `--log-file` or `LIBRARY_LOG_FILE`).
- Expected errors (e.g. duplicate ISBN) are logged as `WARNING`; unexpected exceptions are
  logged with the full traceback while the user only sees a short message (exit code 2).

## CI/CD pipeline

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull request:

```
lint ──▶ tests (Python 3.10 · 3.12 · 3.13, coverage ≥ 90 %) ──▶ smoke test + live /health ──▶ package (main & tags)
```

| Job | What it does |
|---|---|
| **Lint & format check** | `ruff check` + `ruff format --check` |
| **Tests** (matrix) | `pytest` with coverage gate `--cov-fail-under=90`; uploads JUnit + coverage XML |
| **CLI smoke test & health endpoint** | adds/lists/searches a book through the real CLI, runs `health`, starts `serve-health` and probes `GET /health` |
| **Package release artifact** | on `main` and `v*` tags: builds `library-inventory-<version>.zip`, verifies it runs from a clean folder, uploads it |

## Project documentation

| Phase | Documents |
|---|---|
| Sprint 0 – Planning | [Product vision & backlog](docs/sprint-0/product-backlog.md) · [Acceptance criteria](docs/sprint-0/acceptance-criteria.md) · [Definition of Done](docs/sprint-0/definition-of-done.md) · [Sprint 1 plan](docs/sprint-0/sprint-1-plan.md) |
| Sprint 1 | [Sprint review](docs/sprint-1/sprint-review.md) · [Retrospective](docs/sprint-1/retrospective.md) · [Test results](docs/sprint-1/evidence/test-results.txt) · [CLI demo](docs/sprint-1/evidence/cli-demo.txt) |
| Sprint 2 | [Sprint plan](docs/sprint-2/sprint-2-plan.md) · [Sprint review](docs/sprint-2/sprint-review.md) · [Retrospective](docs/sprint-2/retrospective.md) · [Test results](docs/sprint-2/evidence/test-results.txt) · [CLI demo](docs/sprint-2/evidence/cli-demo.txt) |
