# Library Inventory Application

A command-line application for managing a small library's **books, authors and borrowers**,
built over two simulated sprints as the *Agile & DevOps in Practice* final assessment.

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
pytest
```

## Usage

Data is stored in `data/library.json` (override with `--data PATH` or the
`LIBRARY_DATA_FILE` environment variable).

```bash
# catalogue a book (repeat --author for co-authors)
python main.py add-book --title "Things Fall Apart" --author "Chinua Achebe" \
    --isbn 9780385474542 --genre Novel --year 1958

# search by title and/or author (case-insensitive, partial match)
python main.py search achebe
python main.py search "yellow sun" --field title

# list every book
python main.py list
```

## Monitoring & logging

```bash
# health check: prints a JSON status, exit code 0 (ok) or 1 (error)
python main.py health

# the same check over HTTP: GET http://127.0.0.1:8080/health -> 200 ok / 503 error
python main.py serve-health --port 8080

# show logs on the console as well (-v = INFO, -vv = DEBUG)
python main.py -v add-book ...
```

- Every state change (book added, library saved, …) is logged to `logs/library.log`
  (rotating, 1 MB × 3 backups; override with `--log-file` or `LIBRARY_LOG_FILE`).
- Expected errors (e.g. duplicate ISBN) are logged as `WARNING`; unexpected exceptions are
  logged with the full traceback while the user only sees a short message (exit code 2).

## Project structure

```
main.py                 # CLI entry point (argparse)
library/
├── resource.py         # LibraryResource abstract base class
├── author.py           # Author
├── book.py             # Book
├── borrower.py         # Borrower
├── inventory.py        # Library: add_book(), search_books(), ...
├── storage.py          # JSON load/save (atomic writes)
├── health.py           # health check + GET /health endpoint
├── logging_config.py   # console + rotating file logging
├── exceptions.py       # domain errors
└── utils.py            # id generation, validation helpers
data/library.json       # persisted inventory
tests/                  # pytest unit + integration tests
docs/                   # backlog, sprint plans, reviews, retrospectives
```

## Project documentation

| Phase | Documents |
|---|---|
| Sprint 0 – Planning | [Product vision & backlog](docs/sprint-0/product-backlog.md) · [Acceptance criteria](docs/sprint-0/acceptance-criteria.md) · [Definition of Done](docs/sprint-0/definition-of-done.md) · [Sprint 1 plan](docs/sprint-0/sprint-1-plan.md) |
| Sprint 1 | [Sprint review](docs/sprint-1/sprint-review.md) · [Retrospective](docs/sprint-1/retrospective.md) · [Test results](docs/sprint-1/evidence/test-results.txt) · [CLI demo](docs/sprint-1/evidence/cli-demo.txt) |
