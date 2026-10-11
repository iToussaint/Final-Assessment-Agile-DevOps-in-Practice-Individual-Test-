"""Tests for borrowers and lending (US-04: AC4.1 - AC4.5)."""

import pytest

from library.borrower import MAX_LOANS
from library.exceptions import DuplicateError, LoanError, NotFoundError
from library.loan import LoanRecord
from library.storage import load_library, save_library
from main import main


@pytest.fixture
def ama(library):
    return library.add_borrower("Ama Mensah", "ama@example.com")


# --- borrowers (AC4.1) ------------------------------------------------------------------


def test_add_borrower_assigns_member_id(library):
    borrower = library.add_borrower("Ama Mensah", "Ama@Example.com")
    assert borrower.id == "M001"
    assert library.get_borrower("M001").email == "ama@example.com"


def test_duplicate_email_is_rejected(library, ama):
    with pytest.raises(DuplicateError):
        library.add_borrower("Someone Else", "AMA@example.com")
    assert len(library.borrowers) == 1


def test_list_borrowers_sorted_by_name(library, ama):
    library.add_borrower("Kofi Boateng", "kofi@example.com")
    library.add_borrower("abena Owusu", "abena@example.com")
    assert [b.name for b in library.list_borrowers()] == [
        "abena Owusu",
        "Ama Mensah",
        "Kofi Boateng",
    ]


# --- borrowing (AC4.2 - AC4.5) ----------------------------------------------------------


def test_borrow_updates_book_borrower_and_history(library, ama):
    record = library.borrow_book("B001", ama.id)
    assert isinstance(record, LoanRecord) and record.is_active
    assert not library.get_book("B001").is_available
    assert ama.borrowed_book_ids == ("B001",)
    assert library.history == [record]
    assert record.borrowed_at[:4].isdigit()  # ISO date-time
    assert library.borrower_of("B001") is ama


def test_cannot_borrow_a_book_already_on_loan(library, ama):
    kofi = library.add_borrower("Kofi Boateng", "kofi@example.com")
    library.borrow_book("B001", ama.id)
    with pytest.raises(LoanError, match="already on loan by Ama Mensah"):
        library.borrow_book("B001", kofi.id)
    assert kofi.borrowed_book_ids == ()
    assert len(library.history) == 1


def test_loan_limit_is_enforced_without_side_effects(library, ama):
    for book_id in ["B001", "B002", "B003"][:MAX_LOANS]:
        library.borrow_book(book_id, ama.id)
    assert not ama.can_borrow
    with pytest.raises(LoanError, match="loan limit"):
        library.borrow_book("B004", ama.id)
    assert library.get_book("B004").is_available  # refused loan changed nothing


@pytest.mark.parametrize(("book_id", "borrower_id"), [("B999", "M001"), ("B001", "M999")])
def test_unknown_ids_raise_not_found(library, ama, book_id, borrower_id):
    with pytest.raises(NotFoundError):
        library.borrow_book(book_id, borrower_id)


def test_model_level_guards(library, ama):
    book = library.get_book("B001")
    with pytest.raises(LoanError):
        book.mark_returned()  # not on loan yet
    book.mark_borrowed()
    with pytest.raises(LoanError):
        book.mark_borrowed()
    with pytest.raises(LoanError):
        ama.remove_loan("B001")


def test_loans_and_history_survive_save_and_load(library, ama, tmp_path):
    library.borrow_book("B003", ama.id)
    path = tmp_path / "library.json"
    save_library(library, path)
    restored = load_library(path)
    assert not restored.get_book("B003").is_available
    assert restored.get_borrower(ama.id).borrowed_book_ids == ("B003",)
    assert restored.history == library.history


# --- CLI --------------------------------------------------------------------------------


def test_cli_register_and_borrow(tmp_path, capsys, library):
    data = tmp_path / "library.json"
    save_library(library, data)
    args = ["--data", str(data)]
    assert main([*args, "add-borrower", "--name", "Ama Mensah", "--email", "ama@example.com"]) == 0
    assert main([*args, "borrow", "B001", "M001"]) == 0
    out = capsys.readouterr().out
    assert "Registered [M001] Ama Mensah <ama@example.com> - 0 on loan" in out
    assert "'Things Fall Apart' (B001) lent to Ama Mensah (M001)" in out

    assert main([*args, "borrowers"]) == 0
    assert "[M001] Ama Mensah <ama@example.com> - 1 on loan" in capsys.readouterr().out

    assert main([*args, "borrow", "B001", "M001"]) == 1
    assert "already on loan" in capsys.readouterr().err


def test_cli_borrowers_when_none(tmp_path, capsys):
    assert main(["--data", str(tmp_path / "x.json"), "borrowers"]) == 0
    assert capsys.readouterr().out.strip() == "No borrowers registered."
