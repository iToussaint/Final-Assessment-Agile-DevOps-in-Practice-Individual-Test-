# Sprint 1 – Sprint Review

| | |
|---|---|
| **Sprint goal** | *A librarian can catalogue books with their authors, find them by title or author, and the catalogue survives an application restart — all verified automatically by CI.* |
| **Goal met?** | ✅ **Yes** |
| **Committed / delivered** | 13 / 13 story points (3 / 3 stories) |
| **Velocity** | **13 points** |
| **Release tag** | `v0.1.0` |

## Delivered backlog items

| ID | Story | Pts | Status | Branch |
|---|---|---|---|---|
| US-01 | Add a book | 5 | ✅ Done | `feature/US-01-add-book` |
| US-02 | Search books by title / author | 3 | ✅ Done | `feature/US-02-search-books` |
| US-03 | Persist inventory to JSON | 5 | ✅ Done | `feature/US-03-json-persistence` |
| T-01 | Project skeleton | – | ✅ Done | `chore/project-setup` |
| T-02 | CI pipeline (GitHub Actions) | – | ✅ Done | `chore/project-setup` |

## Acceptance criteria check

| AC | Evidence | Result |
|---|---|---|
| AC1.1 add book with id, available | `test_add_book_assigns_id_and_is_available`, CLI demo | ✅ |
| AC1.2 author re-used | `test_add_book_reuses_existing_author`, `…_case_insensitive` | ✅ |
| AC1.3 duplicate ISBN rejected | `test_add_book_rejects_duplicate_isbn`, CLI demo (exit code 1) | ✅ |
| AC1.4 validation, nothing stored | `test_invalid_book_is_not_stored_and_creates_no_author`, `test_book_rejects_invalid_year` | ✅ |
| AC1.5 private attrs + properties | `test_book_attributes_are_private`, `test_book_setter_validates` | ✅ |
| AC1.6 ABC `LibraryResource` | `test_library_resource_is_abstract`, `test_entities_inherit_from_library_resource` | ✅ |
| AC2.1 – AC2.4 search title / author / all / none | `tests/test_search.py` (7 tests), CLI demo | ✅ |
| AC2.5 list comprehensions | `Library.search_books()` in `library/inventory.py` | ✅ |
| AC3.1 / AC3.2 save + load equal objects | `test_save_writes_all_books_and_authors`, `test_round_trip_restores_equal_objects` | ✅ |
| AC3.3 missing file → empty, created on save | `test_missing_file_gives_empty_library_and_save_creates_it` | ✅ |
| AC3.4 corrupted file → clear error | `test_corrupted_json_raises_storage_error`, `test_corrupted_data_file_reports_friendly_error` | ✅ |
| AC3.5 atomic write | `test_save_is_atomic_and_leaves_no_temp_file` | ✅ |

## Demo

A full transcript of the demo is in [evidence/cli-demo.txt](evidence/cli-demo.txt). Highlights:

```text
$ python main.py add-book --title "Good Omens" --author "Terry Pratchett" --author "Neil Gaiman" \
      --isbn 9780060853983 --genre Fantasy --year 1990
Added [B002] Good Omens by Terry Pratchett, Neil Gaiman (1990, Fantasy) ISBN 9780060853983 - available

$ python main.py add-book --title "Things Fall Apart" ... --isbn 978-0-385-47454-2 ...
Error: A book with ISBN 9780385474542 is already catalogued      (exit code 1)

$ python main.py search gaiman --field author
[B002] Good Omens by Terry Pratchett, Neil Gaiman (1990, Fantasy) ISBN 9780060853983 - available
```

## Testing evidence

- **53 tests, 53 passed** — full output in [evidence/test-results.txt](evidence/test-results.txt).
- Unit tests: `test_models.py`, `test_inventory.py`, `test_search.py`.
- Integration tests: `test_storage.py` (real files in `tmp_path`), `test_cli.py` (end-to-end through `main()`).

## CI evidence

- Workflow: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — runs on every push and on PRs to `main`.
- Runs: see the **Actions** tab of the repository → workflow **CI**. The `main` build for the
  merge of US-03 is green (53 passed on Python 3.12).

## Definition of Done check

| DoD item | Status |
|---|---|
| All AC met | ✅ |
| Unit + integration tests, suite green locally | ✅ |
| Short-lived branch per story, merged with `--no-ff` | ✅ |
| CI green on `main` | ✅ |
| README updated (usage, structure) | ✅ |

## Product backlog after Sprint 1

Remaining: US-04 (5), US-05 (3), US-08 (3), US-07 (3), US-06 (3), US-09 (2), US-10 (5) = **24 points**.
No new stories were added; Product Owner confirmed the order is unchanged.
