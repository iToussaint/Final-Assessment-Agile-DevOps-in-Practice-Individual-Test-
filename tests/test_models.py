"""Unit tests for the domain model (US-01: AC1.4, AC1.5, AC1.6)."""

import pytest

from library.author import Author
from library.book import Book
from library.borrower import Borrower
from library.resource import LibraryResource
from library.utils import current_year, generate_id, normalise_isbn


@pytest.fixture
def achebe() -> Author:
    return Author("A001", "Chinua Achebe")


def make_book(author: Author, **overrides) -> Book:
    fields = dict(
        book_id="B001",
        title="Things Fall Apart",
        authors=[author],
        isbn="978-0-385-47454-2",
        genre="novel",
        year=1958,
    )
    fields.update(overrides)
    return Book(**fields)


# --- LibraryResource (abstraction / inheritance) -------------------------------------


def test_library_resource_is_abstract():
    with pytest.raises(TypeError):
        LibraryResource("X001")


@pytest.mark.parametrize("cls", [Book, Author, Borrower])
def test_entities_inherit_from_library_resource(cls):
    assert issubclass(cls, LibraryResource)


def test_resource_id_must_not_be_blank():
    with pytest.raises(ValueError):
        Author("  ", "Someone")


# --- Author ----------------------------------------------------------------------------


def test_author_repr_and_whitespace_normalisation():
    author = Author("A001", "  Chinua   Achebe ")
    assert author.name == "Chinua Achebe"
    assert repr(author) == "Author(id='A001', name='Chinua Achebe')"


def test_authors_with_same_name_are_equal_case_insensitive():
    assert Author("A001", "Chinua Achebe") == Author("A002", "chinua achebe")
    assert len({Author("A001", "Chinua Achebe"), Author("A002", "CHINUA ACHEBE")}) == 1


def test_author_name_cannot_be_empty():
    with pytest.raises(ValueError):
        Author("A001", "")


# --- Book ------------------------------------------------------------------------------


def test_book_properties_are_normalised(achebe):
    book = make_book(achebe)
    assert book.isbn == "9780385474542"
    assert book.genre == "Novel"
    assert book.author_names == ["Chinua Achebe"]
    assert book.is_available


def test_book_attributes_are_private(achebe):
    book = make_book(achebe)
    assert "_Book__title" in vars(book)  # name-mangled private attribute
    assert "title" not in vars(book)  # only reachable through the property
    with pytest.raises(AttributeError):
        book.is_available = False  # read-only property


def test_book_setter_validates(achebe):
    book = make_book(achebe)
    with pytest.raises(ValueError):
        book.title = "   "
    assert book.title == "Things Fall Apart"


def test_authors_getter_returns_a_copy(achebe):
    book = make_book(achebe)
    book.authors.append(Author("A002", "Intruder"))
    assert book.author_names == ["Chinua Achebe"]


@pytest.mark.parametrize("year", [1200, current_year() + 1, "nineteen"])
def test_book_rejects_invalid_year(achebe, year):
    with pytest.raises(ValueError):
        make_book(achebe, year=year)


def test_book_requires_an_author():
    with pytest.raises(ValueError):
        make_book(None, authors=[])


def test_book_rejects_invalid_isbn(achebe):
    with pytest.raises(ValueError):
        make_book(achebe, isbn="12345")


def test_book_repr_is_readable(achebe):
    assert repr(make_book(achebe)) == (
        "Book(id='B001', title='Things Fall Apart', authors=['Chinua Achebe'], "
        "isbn='9780385474542', year=1958)"
    )


def test_books_with_same_isbn_are_equal(achebe):
    assert make_book(achebe) == make_book(achebe, book_id="B999", title="Different title")
    assert make_book(achebe) != make_book(achebe, isbn="9780385014809")


def test_book_round_trips_through_dict(achebe):
    book = make_book(achebe)
    restored = Book.from_dict(book.to_dict(), {achebe.id: achebe})
    assert restored == book
    assert restored.to_dict() == book.to_dict()


# --- Borrower ------------------------------------------------------------------------


def test_borrower_email_is_validated_and_lower_cased():
    borrower = Borrower("M001", "Ama Mensah", "Ama@Example.COM")
    assert borrower.email == "ama@example.com"
    with pytest.raises(ValueError):
        Borrower("M002", "Bad", "not-an-email")


def test_borrower_round_trips_through_dict():
    borrower = Borrower("M001", "Ama Mensah", "ama@example.com", ["B001"])
    restored = Borrower.from_dict(borrower.to_dict())
    assert restored == borrower
    assert restored.borrowed_book_ids == ("B001",)


# --- utils ------------------------------------------------------------------------------


def test_generate_id_uses_next_number_for_prefix():
    assert generate_id("B", []) == "B001"
    assert generate_id("B", ["B001", "B010", "A050"]) == "B011"


def test_normalise_isbn_accepts_isbn10_with_x():
    assert normalise_isbn("0-8044-2957-x") == "080442957X"
