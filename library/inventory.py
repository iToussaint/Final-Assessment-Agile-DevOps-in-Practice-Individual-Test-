"""The Library inventory: in-memory collections and the core use-case functions."""

from __future__ import annotations

from library.author import Author
from library.book import Book
from library.borrower import Borrower
from library.exceptions import DuplicateError, NotFoundError
from library.utils import generate_id, normalise_isbn

SEARCH_FIELDS = ("all", "title", "author")


class Library:
    """Holds every book, author and borrower, keyed by id for O(1) lookup."""

    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.authors: dict[str, Author] = {}
        self.borrowers: dict[str, Borrower] = {}

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
