"""Tests for EBook and AudioBook (US-06: AC6.1 - AC6.4)."""

import inspect

import pytest

from library import reports
from library.author import Author
from library.book import BOOK_TYPES, AudioBook, Book, EBook, book_from_dict
from library.storage import load_library, save_library
from main import main

AUTHOR = Author("A001", "Chinua Achebe")
COMMON = dict(
    title="Things Fall Apart", authors=[AUTHOR], isbn="9780385474542", genre="Novel", year=1958
)


def make_ebook(**overrides):
    return EBook(
        **{"book_id": "B001", **COMMON, "file_format": "epub", "size_mb": 2.5, **overrides}
    )


def make_audiobook(**overrides):
    fields = {"book_id": "B002", **COMMON, "narrator": "Peter Francis James"}
    return AudioBook(**{**fields, "duration_minutes": 390, **overrides})


@pytest.fixture
def mixed(library):
    library.add_book(
        "Purple Hibiscus", ["Chimamanda Ngozi Adichie"], "9780007189885", "Novel", 2003,
        kind="ebook", file_format="PDF", size_mb=3.1,
    )  # fmt: skip
    library.add_book(
        "No Longer at Ease", ["Chinua Achebe"], "9780385474559", "Novel", 1960,
        kind="audiobook", narrator="Peter Francis James", duration_minutes=245,
    )  # fmt: skip
    return library


# --- inheritance & super() (AC6.1) ----------------------------------------------------------


@pytest.mark.parametrize("cls", [EBook, AudioBook])
def test_subclasses_extend_book_and_call_super(cls):
    assert issubclass(cls, Book)
    assert "super().__init__" in inspect.getsource(cls.__init__)


def test_subclass_reuses_parent_validation():
    with pytest.raises(ValueError, match="Title"):
        make_ebook(title=" ")
    with pytest.raises(ValueError, match="Year"):
        make_audiobook(year=1300)


# --- specific fields are validated (AC6.2) -----------------------------------------------


def test_ebook_fields_are_normalised():
    ebook = make_ebook()
    assert ebook.file_format == "EPUB"
    assert ebook.size_mb == 2.5


@pytest.mark.parametrize(
    "overrides", [{"file_format": "DOCX"}, {"size_mb": 0}, {"size_mb": "big"}, {"file_format": ""}]
)
def test_ebook_rejects_invalid_fields(overrides):
    with pytest.raises(ValueError):
        make_ebook(**overrides)


@pytest.mark.parametrize(
    "overrides", [{"narrator": " "}, {"duration_minutes": -5}, {"duration_minutes": "long"}]
)
def test_audiobook_rejects_invalid_fields(overrides):
    with pytest.raises(ValueError):
        make_audiobook(**overrides)


# --- __repr__, describe and serialisation (AC6.3) -----------------------------------------


def test_repr_and_describe_extend_parent_output():
    ebook, audio = make_ebook(), make_audiobook()
    assert repr(ebook).startswith("EBook(id='B001', title='Things Fall Apart'")
    assert repr(ebook).endswith("file_format='EPUB', size_mb=2.5)")
    assert repr(audio).endswith("narrator='Peter Francis James', duration_minutes=390)")
    assert ebook.describe().endswith("- available | e-book EPUB, 2.5 MB")
    assert audio.describe().endswith("| audiobook read by Peter Francis James, 6h 30m")


def test_same_isbn_but_different_kind_is_not_equal():
    book = Book("B003", **COMMON)
    assert make_ebook() != book
    assert make_ebook() == make_ebook(book_id="B099")


@pytest.mark.parametrize("factory", [make_ebook, make_audiobook])
def test_round_trip_restores_the_correct_subclass(factory):
    item = factory()
    restored = book_from_dict(item.to_dict(), {AUTHOR.id: AUTHOR})
    assert type(restored) is type(item)
    assert restored.to_dict() == item.to_dict()


def test_unknown_type_is_rejected():
    data = make_ebook().to_dict() | {"type": "scroll"}
    with pytest.raises(ValueError, match="Unknown book type"):
        book_from_dict(data, {AUTHOR.id: AUTHOR})


def test_book_types_registry():
    assert {"book": Book, "ebook": EBook, "audiobook": AudioBook} == BOOK_TYPES


# --- behave like books everywhere (AC6.4) -----------------------------------------------------


def test_library_add_book_with_kind(mixed):
    assert isinstance(mixed.get_book("B005"), EBook)
    assert isinstance(mixed.get_book("B006"), AudioBook)
    with pytest.raises(ValueError):
        mixed.add_book("X", ["Y"], "9780000000002", "Novel", 2000, kind="scroll")


def test_mixed_library_search_borrow_report_and_persist(mixed, tmp_path):
    assert [type(b).__name__ for b in mixed.search_books("achebe", "author")] == [
        "Book",
        "AudioBook",
        "Book",
    ]
    ama = mixed.add_borrower("Ama Mensah", "ama@example.com")
    mixed.borrow_book("B005", ama.id)
    assert reports.books_by_type(mixed) == {"audiobook": 1, "book": 4, "ebook": 1}
    assert [b.title for b, _ in reports.borrowed_books(mixed)] == ["Purple Hibiscus"]

    path = tmp_path / "library.json"
    save_library(mixed, path)
    restored = load_library(path)
    assert isinstance(restored.get_book("B005"), EBook)
    assert not restored.get_book("B005").is_available
    assert restored.get_book("B006").duration_label == "4h 05m"


# --- CLI ---------------------------------------------------------------------------------------


def test_cli_adds_ebook_and_audiobook(tmp_path, capsys):
    data = ["--data", str(tmp_path / "library.json")]
    common = ["--author", "Chinua Achebe", "--genre", "Novel", "--year", "1958"]
    ebook = ["--type", "ebook", "--format", "pdf", "--size-mb", "1.2",
             "--title", "Things Fall Apart", "--isbn", "9780385474542"]  # fmt: skip
    audio = ["--type", "audiobook", "--narrator", "Peter Francis James", "--duration", "390",
             "--title", "Things Fall Apart (audio)", "--isbn", "9780739337639"]  # fmt: skip
    assert main([*data, "add-book", *ebook, *common]) == 0
    assert main([*data, "add-book", *audio, *common]) == 0
    out = capsys.readouterr().out
    assert "| e-book PDF, 1.2 MB" in out
    assert "| audiobook read by Peter Francis James, 6h 30m" in out


def test_cli_requires_kind_specific_options(tmp_path, capsys):
    argv = ["--data", str(tmp_path / "library.json"), "add-book", "--type", "ebook",
            "--title", "T", "--author", "A", "--isbn", "9780385474542",
            "--genre", "Novel", "--year", "1958"]  # fmt: skip
    assert main(argv) == 1
    assert "ebook needs --format and --size-mb" in capsys.readouterr().err
