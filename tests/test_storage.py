"""Integration tests for JSON persistence (US-03: AC3.1 - AC3.5)."""

import json

import pytest

from library.exceptions import StorageError
from library.inventory import Library
from library.storage import load_library, save_library


def test_save_writes_all_books_and_authors(library, tmp_path):
    path = tmp_path / "library.json"
    save_library(library, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert len(data["books"]) == 4
    assert len(data["authors"]) == 4


def test_round_trip_restores_equal_objects(library, tmp_path):
    path = tmp_path / "library.json"
    save_library(library, path)
    restored = load_library(path)
    assert restored.books == library.books
    assert restored.authors == library.authors
    assert [b.describe() for b in restored.list_books()] == [
        b.describe() for b in library.list_books()
    ]


def test_restored_books_share_author_objects(library, tmp_path):
    path = tmp_path / "library.json"
    save_library(library, path)
    restored = load_library(path)
    achebe = restored.find_author("Chinua Achebe")
    assert all(achebe is book.authors[0] for book in restored.search_books("achebe", "author"))


def test_missing_file_gives_empty_library_and_save_creates_it(tmp_path):
    path = tmp_path / "nested" / "library.json"
    library = load_library(path)
    assert library.books == {}
    library.add_book("Arrow of God", ["Chinua Achebe"], "9780385014809", "Novel", 1964)
    save_library(library, path)
    assert path.exists()


def test_corrupted_json_raises_storage_error(tmp_path):
    path = tmp_path / "library.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(StorageError, match="not valid JSON"):
        load_library(path)


def test_invalid_records_raise_storage_error(tmp_path):
    path = tmp_path / "library.json"
    path.write_text(json.dumps({"books": [{"id": "B001"}]}), encoding="utf-8")
    with pytest.raises(StorageError, match="invalid records"):
        load_library(path)


def test_save_is_atomic_and_leaves_no_temp_file(tmp_path):
    path = tmp_path / "library.json"
    save_library(Library(), path)
    save_library(Library(), path)
    assert [p.name for p in tmp_path.iterdir()] == ["library.json"]
