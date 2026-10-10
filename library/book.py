"""The Book entity."""

from __future__ import annotations

from typing import Any

from library.author import Author
from library.resource import LibraryResource
from library.utils import current_year, normalise_isbn, require_text

MIN_YEAR = 1450  # the printing press - nothing older can be a printed book


class Book(LibraryResource):
    """A catalogued title written by one or more authors."""

    resource_type = "book"

    def __init__(
        self,
        book_id: str,
        title: str,
        authors: list[Author],
        isbn: str,
        genre: str,
        year: int,
        available: bool = True,
    ) -> None:
        super().__init__(book_id)
        self.title = title
        self.authors = authors
        self.isbn = isbn
        self.genre = genre
        self.year = year
        self.__available = bool(available)

    # --- encapsulated attributes -------------------------------------------------

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        self.__title = require_text(value, "Title")

    @property
    def authors(self) -> list[Author]:
        """A copy of the author list, so callers cannot mutate the book's state."""
        return list(self.__authors)

    @authors.setter
    def authors(self, value: list[Author]) -> None:
        authors = list(value or [])
        if not authors:
            raise ValueError("A book needs at least one author")
        if not all(isinstance(author, Author) for author in authors):
            raise TypeError("authors must be Author instances")
        self.__authors = authors

    @property
    def author_names(self) -> list[str]:
        return [author.name for author in self.__authors]

    @property
    def isbn(self) -> str:
        return self.__isbn

    @isbn.setter
    def isbn(self, value: str) -> None:
        self.__isbn = normalise_isbn(value)

    @property
    def genre(self) -> str:
        return self.__genre

    @genre.setter
    def genre(self, value: str) -> None:
        self.__genre = require_text(value, "Genre").title()

    @property
    def year(self) -> int:
        return self.__year

    @year.setter
    def year(self, value: int) -> None:
        try:
            year = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Year must be a whole number, got {value!r}") from None
        if not MIN_YEAR <= year <= current_year():
            raise ValueError(f"Year must be between {MIN_YEAR} and {current_year()}, got {year}")
        self.__year = year

    @property
    def is_available(self) -> bool:
        return self.__available

    # --- LibraryResource interface ----------------------------------------------

    def describe(self) -> str:
        status = "available" if self.is_available else "borrowed"
        return (
            f"[{self.id}] {self.title} by {', '.join(self.author_names)} "
            f"({self.year}, {self.genre}) ISBN {self.isbn} - {status}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.resource_type,
            "title": self.title,
            "author_ids": [author.id for author in self.__authors],
            "isbn": self.isbn,
            "genre": self.genre,
            "year": self.year,
            "available": self.is_available,
        }

    @classmethod
    def _kwargs_from_dict(
        cls, data: dict[str, Any], authors_by_id: dict[str, Author]
    ) -> dict[str, Any]:
        """Constructor arguments rebuilt from ``to_dict()`` output (extended by subclasses)."""
        return {
            "book_id": data["id"],
            "title": data["title"],
            "authors": [authors_by_id[author_id] for author_id in data["author_ids"]],
            "isbn": data["isbn"],
            "genre": data["genre"],
            "year": data["year"],
            "available": data.get("available", True),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], authors_by_id: dict[str, Author]) -> Book:
        return cls(**cls._kwargs_from_dict(data, authors_by_id))

    # --- special methods -------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(id={self.id!r}, title={self.title!r}, "
            f"authors={self.author_names!r}, isbn={self.isbn!r}, year={self.year})"
        )

    def __eq__(self, other: object) -> bool:
        """Books are equal when they are the same kind of item with the same ISBN."""
        if not isinstance(other, Book):
            return NotImplemented
        return type(self) is type(other) and self.isbn == other.isbn

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.isbn))
