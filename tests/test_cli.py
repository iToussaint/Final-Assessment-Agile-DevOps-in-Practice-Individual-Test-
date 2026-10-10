"""End-to-end tests of the command-line interface against a temporary data file."""

import json

import pytest

from main import main

ACHEBE = [
    "add-book", "--title", "Things Fall Apart", "--author", "Chinua Achebe",
    "--isbn", "9780385474542", "--genre", "Novel", "--year", "1958",
]  # fmt: skip
GOOD_OMENS = [
    "add-book", "--title", "Good Omens", "--author", "Terry Pratchett",
    "--author", "Neil Gaiman", "--isbn", "9780060853983", "--genre", "Fantasy", "--year", "1990",
]  # fmt: skip


@pytest.fixture
def run(tmp_path, capsys):
    data_file = tmp_path / "library.json"

    def _run(*argv):
        code = main(["--data", str(data_file), *argv])
        out, err = capsys.readouterr()
        return code, out, err

    _run.data_file = data_file
    return _run


def test_add_book_persists_to_data_file(run):
    code, out, _ = run(*ACHEBE)
    assert code == 0
    assert "Added [B001] Things Fall Apart by Chinua Achebe" in out
    data = json.loads(run.data_file.read_text(encoding="utf-8"))
    assert data["books"][0]["title"] == "Things Fall Apart"


def test_data_survives_between_runs_and_list_shows_it(run):
    run(*ACHEBE)
    run(*GOOD_OMENS)
    code, out, _ = run("list")
    assert code == 0
    assert out.splitlines()[0].startswith("[B002] Good Omens by Terry Pratchett, Neil Gaiman")
    assert "[B001] Things Fall Apart" in out


def test_search_by_author(run):
    run(*ACHEBE)
    run(*GOOD_OMENS)
    code, out, _ = run("search", "gaiman", "--field", "author")
    assert code == 0
    assert "Good Omens" in out and "Things Fall Apart" not in out


def test_search_without_results(run):
    run(*ACHEBE)
    _, out, _ = run("search", "tolkien")
    assert out.strip() == "No books found."


def test_list_on_empty_library(run):
    _, out, _ = run("list")
    assert out.strip() == "The library is empty."


def test_duplicate_isbn_returns_error_code(run):
    run(*ACHEBE)
    code, _, err = run(*ACHEBE)
    assert code == 1
    assert "already catalogued" in err


def test_corrupted_data_file_reports_friendly_error(run):
    run.data_file.write_text("{oops", encoding="utf-8")
    code, _, err = run("list")
    assert code == 1
    assert err.startswith("Error: Data file")
