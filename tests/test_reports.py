"""Tests for inventory reports (US-07: AC7.1 - AC7.5)."""

import pytest

from library import reports
from library.inventory import Library
from library.storage import save_library
from main import main


@pytest.fixture
def lending(library):
    ama = library.add_borrower("Ama Mensah", "ama@example.com")
    library.borrow_book("B001", ama.id)  # Things Fall Apart
    library.borrow_book("B004", ama.id)  # Good Omens
    return library


def test_available_books_excludes_loans(lending):
    assert [b.title for b in reports.available_books(lending)] == [
        "Arrow of God",
        "Half of a Yellow Sun",
    ]


def test_borrowed_books_are_paired_with_their_borrower(lending):
    pairs = reports.borrowed_books(lending)
    assert [(book.id, holder.name) for book, holder in pairs] == [
        ("B004", "Ama Mensah"),
        ("B001", "Ama Mensah"),
    ]


def test_books_by_author_groups_titles_including_co_authors(library):
    assert reports.books_by_author(library) == {
        "Chimamanda Ngozi Adichie": ["Half of a Yellow Sun"],
        "Chinua Achebe": ["Arrow of God", "Things Fall Apart"],
        "Neil Gaiman": ["Good Omens"],
        "Terry Pratchett": ["Good Omens"],
    }


def test_books_by_genre_and_type(library):
    assert reports.books_by_genre(library) == {
        "Fantasy": 1,
        "Historical Fiction": 1,
        "Novel": 2,
    }
    assert reports.books_by_type(library) == {"book": 4}


def test_summary_totals(lending):
    lending.return_book("B004")
    assert reports.summary(lending) == {
        "books": 4,
        "available": 3,
        "borrowed": 1,
        "authors": 4,
        "borrowers": 1,
        "active_loans": 1,
        "total_loans": 2,
        "by_type": {"book": 4},
    }


def test_reports_on_empty_library():
    empty = Library()
    assert reports.available_books(empty) == []
    assert reports.books_by_author(empty) == {}
    assert reports.render_report("summary", empty)[-1] == "By type: -"


def test_render_report_rejects_unknown_name(library):
    with pytest.raises(ValueError):
        reports.render_report("nope", library)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("available", "Available books (2)"),
        ("borrowed", "[B001] Things Fall Apart -> Ama Mensah (M001)"),
        ("by-author", "  - Things Fall Apart"),
        ("by-genre", "Novel: 2"),
        ("summary", "Active loans: 2"),
    ],
)
def test_cli_report_commands(lending, tmp_path, capsys, name, expected):
    data = tmp_path / "library.json"
    save_library(lending, data)
    assert main(["--data", str(data), "report", name]) == 0
    assert expected in capsys.readouterr().out.splitlines()


def test_report_generation_is_logged(lending, tmp_path, isolated_log_file):
    data = tmp_path / "library.json"
    save_library(lending, data)
    main(["--data", str(data), "report", "summary"])
    assert "library.reports | Generating summary report" in isolated_log_file.read_text(
        encoding="utf-8"
    )
