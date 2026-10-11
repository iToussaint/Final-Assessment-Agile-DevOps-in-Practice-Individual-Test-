"""The Library inventory: in-memory collections and the core use-case functions."""

from __future__ import annotations

import logging

from library.author import Author
from library.book import Book
from library.borrower import Borrower
from library.exceptions import DuplicateError, LoanError, NotFoundError
from library.loan import LoanRecord
from library.utils import generate_id, normalise_isbn, now_iso

SEARCH_FIELDS = ("all", "title", "author")

logger = logging.getLogger(__name__)


class Library:
    """Holds every book, author and borrower, keyed by id for O(1) lookup."""

    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.authors: dict[str, Author] = {}
        self.borrowers: dict[str, Borrower] = {}
        self.history: list[LoanRecord] = []

    # --- authors ---------------------------------------------------------------------

    def find_author(self, name: str) -> Author | None:
        """Return the author with this name (case-insensitive), if any."""
        wanted = " ".join(name.split()).casefold()
        matches = [a for a in self.authors.values() if a.name.casefold() == wanted]
        return matches[0] if matches else None

    def _resolve_authors(self, author_names: list[str]) -> tuple[list[Author], list[Author]]:
        """Map names to Author objects, re-using existing ones.

        Returns ``(authors, new_authors)``; new authors are *not* registered yet so
        nothing is stored if the book later fails validation.
        """
        authors: list[Author] = []
        new_authors: list[Author] = []
        taken_ids = list(self.authors)
        for name in author_names:
            author = self.find_author(name)
            if author is None:
                author = Author(generate_id("A", taken_ids), name)
                taken_ids.append(author.id)
                new_authors.append(author)
            if author not in authors:
                authors.append(author)
        return authors, new_authors

    # --- books -----------------------------------------------------------------------

    def add_book(
        self,
        title: str,
        author_names: list[str],
        isbn: str,
        genre: str,
        year: int,
    ) -> Book:
        """Validate and catalogue a new book, returning it."""
        clean_isbn = normalise_isbn(isbn)
        if any(book.isbn == clean_isbn for book in self.books.values()):
            raise DuplicateError(f"A book with ISBN {clean_isbn} is already catalogued")

        authors, new_authors = self._resolve_authors(author_names)
        book = Book(
            book_id=generate_id("B", self.books),
            title=title,
            authors=authors,
            isbn=clean_isbn,
            genre=genre,
            year=year,
        )
        self.authors.update({author.id: author for author in new_authors})
        self.books[book.id] = book
        for author in new_authors:
            logger.info("Registered author %s (%s)", author.id, author.name)
        logger.info("Added book %s %r (ISBN %s)", book.id, book.title, book.isbn)
        return book

    def get_book(self, book_id: str) -> Book:
        try:
            return self.books[book_id]
        except KeyError:
            raise NotFoundError(f"No book with id {book_id!r}") from None

    def search_books(self, term: str, field: str = "all") -> list[Book]:
        """Case-insensitive partial-match search on ``title``, ``author`` or ``all``."""
        if field not in SEARCH_FIELDS:
            raise ValueError(f"field must be one of {', '.join(SEARCH_FIELDS)}")
        needle = term.strip().casefold()
        if not needle:
            return []
        logger.debug("Searching %s for %r", field, needle)

        def matches_title(book: Book) -> bool:
            return needle in book.title.casefold()

        def matches_author(book: Book) -> bool:
            return any(needle in name.casefold() for name in book.author_names)

        checks = {
            "title": [matches_title],
            "author": [matches_author],
            "all": [matches_title, matches_author],
        }[field]
        return [book for book in self.list_books() if any(check(book) for check in checks)]

    def list_books(self) -> list[Book]:
        """All books sorted by title."""
        return sorted(self.books.values(), key=lambda book: book.title.casefold())

    # --- borrowers ---------------------------------------------------------------------

    def add_borrower(self, name: str, email: str) -> Borrower:
        """Register a new borrower; e-mail addresses must be unique."""
        borrower = Borrower(generate_id("M", self.borrowers), name, email)
        if borrower in self.borrowers.values():
            raise DuplicateError(f"A borrower with e-mail {borrower.email} is already registered")
        self.borrowers[borrower.id] = borrower
        logger.info("Registered borrower %s (%s)", borrower.id, borrower.email)
        return borrower

    def get_borrower(self, borrower_id: str) -> Borrower:
        try:
            return self.borrowers[borrower_id]
        except KeyError:
            raise NotFoundError(f"No borrower with id {borrower_id!r}") from None

    def list_borrowers(self) -> list[Borrower]:
        return sorted(self.borrowers.values(), key=lambda borrower: borrower.name.casefold())

    # --- lending -----------------------------------------------------------------------

    def borrow_book(self, book_id: str, borrower_id: str) -> LoanRecord:
        """Lend an available book to a borrower and record it in the history."""
        book = self.get_book(book_id)
        borrower = self.get_borrower(borrower_id)
        # check every rule before changing any state, so a refusal leaves nothing half-done
        if not book.is_available:
            holder = self.borrower_of(book.id)
            who = f" by {holder.name}" if holder else ""
            raise LoanError(f"{book.title!r} ({book.id}) is already on loan{who}")
        if not borrower.can_borrow:
            raise LoanError(f"{borrower.name} has reached the loan limit")

        book.mark_borrowed()
        borrower.add_loan(book.id)
        record = LoanRecord(book_id=book.id, borrower_id=borrower.id, borrowed_at=now_iso())
        self.history.append(record)
        logger.info("Book %s lent to borrower %s", book.id, borrower.id)
        return record

    def return_book(self, book_id: str) -> LoanRecord:
        """Receive a borrowed book back and close its loan record."""
        book = self.get_book(book_id)
        open_records = [r for r in self.active_loans() if r.book_id == book.id]
        if book.is_available or not open_records:
            raise LoanError(f"{book.title!r} ({book.id}) is not on loan")
        record = open_records[0]
        borrower = self.get_borrower(record.borrower_id)

        borrower.remove_loan(book.id)
        book.mark_returned()
        record.returned_at = now_iso()
        logger.info("Book %s returned by borrower %s", book.id, borrower.id)
        return record

    def get_history(self, borrower_id: str | None = None) -> list[LoanRecord]:
        """Borrowing history, oldest first, optionally for one borrower."""
        if borrower_id is not None:
            self.get_borrower(borrower_id)  # raises NotFoundError for unknown ids
        return [
            record
            for record in self.history
            if borrower_id is None or record.borrower_id == borrower_id
        ]

    def active_loans(self) -> list[LoanRecord]:
        return [record for record in self.history if record.is_active]

    def borrower_of(self, book_id: str) -> Borrower | None:
        """The borrower currently holding ``book_id``, if it is on loan."""
        holders = [
            self.borrowers.get(record.borrower_id)
            for record in self.active_loans()
            if record.book_id == book_id
        ]
        return holders[0] if holders else None
