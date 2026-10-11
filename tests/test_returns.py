"""Tests for returning books and the borrowing history (US-05: AC5.1 - AC5.4)."""

import pytest

from library.exceptions import LoanError, NotFoundError
from library.storage import load_library, save_library
from main import main


@pytest.fixture
def lending(library):
    """Library where Ama has borrowed B001 and B002, and Kofi has borrowed B003."""
    ama = library.add_borrower("Ama Mensah", "ama@example.com")
    kofi = library.add_borrower("Kofi Boateng", "kofi@example.com")
    library.borrow_book("B001", ama.id)
    library.borrow_book("B002", ama.id)
    library.borrow_book("B003", kofi.id)
    return library


def test_return_makes_book_available_and_frees_borrower_slot(lending):
    record = lending.return_book("B001")
    assert lending.get_book("B001").is_available
    assert lending.get_borrower("M001").borrowed_book_ids == ("B002",)
    assert record.returned_at is not None and not record.is_active
    assert lending.borrower_of("B001") is None


def test_returned_book_can_be_borrowed_again(lending):
    lending.return_book("B003")
    lending.borrow_book("B003", "M001")
    assert [r.borrower_id for r in lending.get_history() if r.book_id == "B003"] == ["M002", "M001"]


def test_returning_a_book_not_on_loan_is_rejected(lending):
    with pytest.raises(LoanError, match="not on loan"):
        lending.return_book("B004")
    lending.return_book("B001")
    with pytest.raises(LoanError):
        lending.return_book("B001")


def test_return_unknown_book_raises_not_found(lending):
    with pytest.raises(NotFoundError):
        lending.return_book("B999")


def test_history_can_be_filtered_by_borrower(lending):
    lending.return_book("B001")
    assert len(lending.get_history()) == 3
    ama_history = lending.get_history("M001")
    assert [r.book_id for r in ama_history] == ["B001", "B002"]
    assert [r.is_active for r in ama_history] == [False, True]
    with pytest.raises(NotFoundError):
        lending.get_history("M999")


def test_history_with_return_dates_is_persisted(lending, tmp_path):
    lending.return_book("B002")
    path = tmp_path / "library.json"
    save_library(lending, path)
    restored = load_library(path)
    assert restored.history == lending.history
    assert restored.get_history("M001")[1].returned_at is not None


def test_cli_return_and_history(lending, tmp_path, capsys):
    data = tmp_path / "library.json"
    save_library(lending, data)
    args = ["--data", str(data)]
    assert main([*args, "return", "B001"]) == 0
    assert "'Things Fall Apart' (B001) returned by Ama Mensah (M001)" in capsys.readouterr().out

    assert main([*args, "history", "--borrower", "M001"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 2
    assert "B001 'Things Fall Apart' | M001 Ama Mensah" in lines[0]
    assert "on loan" in lines[1] and "B002" in lines[1]

    assert main([*args, "return", "B001"]) == 1
    assert "not on loan" in capsys.readouterr().err


def test_cli_history_when_empty(tmp_path, capsys):
    assert main(["--data", str(tmp_path / "x.json"), "history"]) == 0
    assert capsys.readouterr().out.strip() == "No borrowing history."
