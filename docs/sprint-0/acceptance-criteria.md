# Sprint 0 – Acceptance Criteria

Acceptance criteria (AC) are written in *Given / When / Then* form. A story is accepted only
when **every** AC passes **and** the [Definition of Done](definition-of-done.md) is met.

---

## US-01 – Add a book (Must · 5 pts)

- **AC1.1** Given valid details (title, author name(s), ISBN, genre, year), when I add a book,
  then it is stored in the inventory with a unique ID and is *available*.
- **AC1.2** Given an author name that already exists, when I add another book by that author,
  then the existing `Author` is re-used (no duplicate author records).
- **AC1.3** Given a book with an ISBN that is already catalogued, when I add it,
  then the operation is rejected with a clear error message.
- **AC1.4** Given an empty title or an invalid year (in the future or < 1450), when I add a book,
  then a validation error is raised and nothing is stored.
- **AC1.5** Book data is encapsulated: attributes are private and exposed through
  properties (getters/setters with validation).
- **AC1.6** `Book`, `Author` and `Borrower` inherit from the abstract base class
  `LibraryResource`, which cannot be instantiated directly.

## US-02 – Search books (Must · 3 pts)

- **AC2.1** Given a search term, when I search by **title**, then all books whose title contains
  the term are returned (case-insensitive, partial match).
- **AC2.2** Given a search term, when I search by **author**, then all books by any author whose
  name contains the term are returned.
- **AC2.3** Given no field, when I search, then both title and author are searched.
- **AC2.4** Given a term that matches nothing, then an empty result is returned and the CLI shows
  "No books found".
- **AC2.5** Searching is implemented with list comprehensions.

## US-03 – Persist inventory to JSON (Must · 5 pts)

- **AC3.1** Given books in the inventory, when the application saves, then
  `data/library.json` contains every book and author.
- **AC3.2** Given an existing `library.json`, when the application starts, then all records
  are loaded back as objects equal (`__eq__`) to the ones saved.
- **AC3.3** Given the data file does not exist, when the application starts, then it starts
  with an empty inventory and creates the file on first save.
- **AC3.4** Given a corrupted JSON file, when the application starts, then a clear error is
  reported instead of a raw traceback.
- **AC3.5** Writes are atomic (write to a temp file, then replace) so a crash cannot leave a
  half-written file.

## US-04 – Register borrowers & borrow a book (Must · 5 pts)

- **AC4.1** Given a name and e-mail, when I register a borrower, then a borrower with a unique
  ID is stored; a duplicate e-mail is rejected.
- **AC4.2** Given an available book and a registered borrower, when I borrow the book, then the
  book becomes *borrowed*, it appears in the borrower's current loans, and a history entry
  with the date is recorded.
- **AC4.3** Given a book that is already borrowed, when someone tries to borrow it, then the
  operation is rejected.
- **AC4.4** Given a borrower who already holds the maximum of **3** books, when they try to
  borrow another, then the operation is rejected.
- **AC4.5** Unknown book or borrower IDs produce a clear "not found" error.

## US-05 – Return a book & borrowing history (Must · 3 pts)

- **AC5.1** Given a borrowed book, when it is returned, then it becomes *available* and is
  removed from the borrower's current loans.
- **AC5.2** The history entry for that loan gets a return date.
- **AC5.3** Returning a book that is not borrowed is rejected with a clear error.
- **AC5.4** The full borrowing history is persisted to `library.json` and can be listed,
  optionally filtered by borrower.

## US-06 – E-books & audiobooks (Should · 3 pts)

- **AC6.1** `EBook` and `AudioBook` extend `Book` and call `super().__init__()`.
- **AC6.2** An `EBook` adds file format (PDF/EPUB/MOBI) and size in MB; an `AudioBook` adds
  narrator and duration in minutes — both validated.
- **AC6.3** Both subclasses override `__repr__`/`describe()` and serialise their extra fields;
  loading from JSON restores the correct subclass.
- **AC6.4** E-books and audiobooks can be searched, borrowed and reported exactly like books.

## US-07 – Reports (Should · 3 pts)

- **AC7.1** "Available books" report lists every book not currently on loan.
- **AC7.2** "Borrowed books" report lists every book on loan together with its borrower.
- **AC7.3** "Books by author" report groups titles under each author (dict comprehension).
- **AC7.4** A summary report shows totals (books, available, borrowed, borrowers, by type).
- **AC7.5** Reports are generated with list/dict comprehensions.

## US-08 – Health check & logging (Should · 3 pts)

- **AC8.1** `python main.py health` checks the data file is readable, valid JSON and writable,
  prints a JSON status (`"status": "ok"` or `"error"` with details) and exits `0`/`1`.
- **AC8.2** `python main.py serve-health` exposes the same check over HTTP at `GET /health`
  (200 when healthy, 503 otherwise).
- **AC8.3** Every state-changing action (add, borrow, return, save) is logged with timestamp,
  level and module.
- **AC8.4** Logs go to the console and to a rotating file `logs/library.log`; unexpected errors
  are logged with a full traceback (error tracking) while the user sees a friendly message.

## US-09 – Update / remove a book (Could · 2 pts)

- **AC9.1** A book's title, genre or year can be updated with the same validation as US-01.
- **AC9.2** A book can be removed only if it is not currently borrowed.

## US-10 – Due dates & overdue items (Could · 5 pts)

- **AC10.1** Each loan gets a due date (default 14 days).
- **AC10.2** An "overdue" report lists loans past their due date.
