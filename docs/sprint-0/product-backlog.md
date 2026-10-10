# Sprint 0 – Product Vision & Product Backlog

## Product Vision

> For small community and school libraries that still track their stock on paper,
> **Library Inventory** is a lightweight command-line application that lets a librarian
> catalogue books, e-books and audiobooks, lend them to borrowers and instantly see what is
> available — with every record safely persisted to a JSON file.

## Users / Personas

| Persona | Need |
|---|---|
| **Librarian** (primary user) | Catalogue items, lend and receive them back, answer "do we have…?" questions quickly |
| **Library manager** | Get simple reports on stock and lending activity |
| **Maintainer (developer/ops)** | Know the application is healthy and diagnose problems from logs |

## Product Backlog (prioritised & estimated)

**Prioritisation:** MoSCoW (Must / Should / Could), then ordered by business value and
technical dependency (e.g. persistence and the book model unblock everything else).

**Estimation:** relative sizing with Fibonacci story points (1, 2, 3, 5, 8), using
US-02 *Search books* (3 pts) as the reference story. Points reflect complexity, effort and
uncertainty — not hours.

| Rank | ID | User Story | Priority | Points |
|---|---|---|---|---|
| 1 | US-01 | As a **librarian**, I want to add a book with its author(s), ISBN, genre and year so that the item is catalogued in the inventory. | Must | 5 |
| 2 | US-03 | As a **librarian**, I want the inventory to be saved to and loaded from a JSON file so that no data is lost when the application is closed. | Must | 5 |
| 3 | US-02 | As a **librarian**, I want to search books by title or author so that I can quickly tell a visitor whether we hold a book. | Must | 3 |
| 4 | US-04 | As a **librarian**, I want to register borrowers and lend an available book to them so that I know who has which item. | Must | 5 |
| 5 | US-05 | As a **librarian**, I want to record the return of a borrowed book and keep a borrowing history so that items become available again and past loans can be audited. | Must | 3 |
| 6 | US-08 | As a **maintainer**, I want a health check and application logs so that I can verify the system is working and troubleshoot errors. | Should | 3 |
| 7 | US-07 | As a **library manager**, I want reports of available books, borrowed books and books grouped by author so that I can understand the state of the collection. | Should | 3 |
| 8 | US-06 | As a **librarian**, I want to catalogue e-books and audiobooks with their specific details (file format/size, narrator/duration) so that digital items are managed alongside print books. | Should | 3 |
| 9 | US-09 | As a **librarian**, I want to update or remove a book record so that the catalogue stays accurate. | Could | 2 |
| 10 | US-10 | As a **librarian**, I want loans to have a due date and see overdue items so that I can chase late returns. | Could | 5 |

**Total backlog:** 37 points · **Must:** 21 pts · **Should:** 9 pts · **Could:** 7 pts

### Technical enablers (not user-facing, tracked as sprint tasks)

| ID | Enabler | Sprint |
|---|---|---|
| T-01 | Project skeleton (package layout, `pyproject.toml`, dev requirements) | 1 |
| T-02 | CI pipeline on GitHub Actions running the test-suite on every push / PR | 1 |
| T-03 | Branching workflow: `main` + short-lived `feature/*`, `docs/*`, `ci/*` branches merged with `--no-ff` | 0 |
