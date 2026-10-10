"""Unit tests for the Library inventory (US-01: AC1.1 - AC1.4)."""

import pytest

from library.exceptions import DuplicateError, NotFoundError
from library.inventory import Library


def test_add_book_assigns_id_and_is_available():
    lib = Library()
    book = lib.add_book("Things Fall Apart", ["Chinua Achebe"], "9780385474542", "Novel", 1958)
    assert book.id == "B001"
    assert book.is_available
    assert lib.get_book("B001") is book


def test_add_book_reuses_existing_author(library):
    achebe_books = [b for b in library.books.values() if "Chinua Achebe" in b.author_names]
    assert len(achebe_books) == 2
    assert achebe_books[0].authors[0] is achebe_books[1].authors[0]
    assert len(library.authors) == 4  # Achebe, Adichie, Pratchett, Gaiman


def test_add_book_author_match_is_case_insensitive(library):
    book = library.add_book("No Longer at Ease", ["chinua  ACHEBE"], "9780385474559", "Novel", 1960)
    assert book.authors[0].id == library.find_author("Chinua Achebe").id
    assert len(library.authors) == 4


def test_add_book_rejects_duplicate_isbn(library):
    with pytest.raises(DuplicateError):
        library.add_book("Copy", ["Someone"], "978-0-385-47454-2", "Novel", 1958)


def test_invalid_book_is_not_stored_and_creates_no_author():
    lib = Library()
    with pytest.raises(ValueError):
        lib.add_book("", ["New Author"], "9780385474542", "Novel", 1958)
    assert lib.books == {}
    assert lib.authors == {}


def test_get_book_unknown_id_raises_not_found(library):
    with pytest.raises(NotFoundError):
        library.get_book("B999")


def test_list_books_is_sorted_by_title(library):
    assert [b.title for b in library.list_books()] == [
        "Arrow of God",
        "Good Omens",
        "Half of a Yellow Sun",
        "Things Fall Apart",
    ]
