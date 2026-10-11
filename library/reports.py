"""Inventory reports built with list and dict comprehensions."""

from __future__ import annotations

import logging
from typing import Any

from library.book import Book
from library.borrower import Borrower
from library.inventory import Library

logger = logging.getLogger(__name__)

REPORTS = ("available", "borrowed", "by-author", "by-genre", "summary")


def available_books(library: Library) -> list[Book]:
    return [book for book in library.list_books() if book.is_available]


def borrowed_books(library: Library) -> list[tuple[Book, Borrower | None]]:
    """Every book on loan, paired with the borrower who holds it."""
    return [
        (book, library.borrower_of(book.id))
        for book in library.list_books()
        if not book.is_available
    ]


def books_by_author(library: Library) -> dict[str, list[str]]:
    """Author name -> sorted titles (co-written books appear under each author)."""
    authors = sorted(library.authors.values(), key=lambda author: author.name.casefold())
    return {
        author.name: sorted(book.title for book in library.books.values() if author in book.authors)
        for author in authors
    }


def books_by_genre(library: Library) -> dict[str, int]:
    genres = sorted({book.genre for book in library.books.values()})
    return {
        genre: sum(1 for book in library.books.values() if book.genre == genre) for genre in genres
    }


def books_by_type(library: Library) -> dict[str, int]:
    types = sorted({book.resource_type for book in library.books.values()})
    return {
        kind: len([book for book in library.books.values() if book.resource_type == kind])
        for kind in types
    }


def summary(library: Library) -> dict[str, Any]:
    available = available_books(library)
    return {
        "books": len(library.books),
        "available": len(available),
        "borrowed": len(library.books) - len(available),
        "authors": len(library.authors),
        "borrowers": len(library.borrowers),
        "active_loans": len(library.active_loans()),
        "total_loans": len(library.history),
        "by_type": books_by_type(library),
    }


def render_report(name: str, library: Library) -> list[str]:
    """Return the named report as printable lines."""
    logger.info("Generating %s report", name)
    if name == "available":
        books = available_books(library)
        return [f"Available books ({len(books)})", *(book.describe() for book in books)]
    if name == "borrowed":
        loans = borrowed_books(library)
        return [
            f"Borrowed books ({len(loans)})",
            *(
                f"[{book.id}] {book.title} -> "
                + (f"{holder.name} ({holder.id})" if holder else "unknown borrower")
                for book, holder in loans
            ),
        ]
    if name == "by-author":
        lines = ["Books by author"]
        for author, titles in books_by_author(library).items():
            lines.append(f"{author} ({len(titles)})")
            lines.extend(f"  - {title}" for title in titles)
        return lines
    if name == "by-genre":
        return ["Books by genre", *(f"{g}: {n}" for g, n in books_by_genre(library).items())]
    if name == "summary":
        stats = summary(library)
        by_type = ", ".join(f"{kind}: {count}" for kind, count in stats.pop("by_type").items())
        return [
            "Library summary",
            *(f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in stats.items()),
            f"By type: {by_type or '-'}",
        ]
    raise ValueError(f"Unknown report {name!r}; choose from {', '.join(REPORTS)}")
