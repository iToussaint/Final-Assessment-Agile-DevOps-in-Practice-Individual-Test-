# Sprint 1 – Sprint Plan

| | |
|---|---|
| **Sprint** | 1 (simulated, time-boxed to one working session) |
| **Dates** | Sat 10 Oct 2026 |
| **Team** | 1 developer (me) — Product Owner, Scrum Master and Developer roles |
| **Capacity** | ~13 story points + technical enablers T-01, T-02 |

## Sprint Goal

> *"A librarian can catalogue books with their authors, find them by title or author, and
> the catalogue survives an application restart — all verified automatically by CI."*

## Selected backlog items

| ID | Story | Points |
|---|---|---|
| US-01 | Add a book (with authors, OOP model, validation) | 5 |
| US-03 | Persist inventory to JSON | 5 |
| US-02 | Search books by title / author | 3 |
| | **Committed total** | **13** |

Why these three: they are the top-ranked *Must* stories and every later story (borrowing,
reports, sub-types) depends on the book model, the inventory and persistence.

## Task breakdown

### T-01 / T-02 – Enablers
- [ ] Create package skeleton (`library/`, `tests/`, `data/`), `pyproject.toml`, `requirements-dev.txt`
- [ ] GitHub Actions workflow: checkout → set up Python → install deps → `pytest`

### US-01 – Add a book
- [ ] `LibraryResource` ABC with abstract `to_dict()` / `describe()` and a shared `id`
- [ ] `Author` class (private attrs, properties, `__repr__`, `__eq__`)
- [ ] `Book` class (validation in setters, author list, availability flag)
- [ ] `Library` inventory with dict `id → object` and `add_book()` (author re-use, duplicate ISBN check)
- [ ] Unit tests for models and `add_book()`

### US-02 – Search books
- [ ] `search_books(term, field)` using list comprehensions, case-insensitive
- [ ] Unit tests (title, author, both, no match)

### US-03 – Persistence
- [ ] `to_dict()` / `from_dict()` on every model
- [ ] `storage.py`: `load_library()` / `save_library()` with atomic write and corrupted-file error
- [ ] `main.py` CLI: `add-book`, `search`, `list`
- [ ] Integration tests: save → load round-trip; CLI end-to-end against a temp data file

## Risks
- First time wiring CI for this repo — keep the workflow minimal and extend in Sprint 2.
- Persistence format will need to grow (borrowers, history) — design `to_dict()` to be extensible.
