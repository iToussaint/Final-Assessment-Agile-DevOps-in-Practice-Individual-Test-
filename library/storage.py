"""JSON persistence for the library inventory."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from library.author import Author
from library.book import Book
from library.borrower import Borrower
from library.exceptions import StorageError
from library.inventory import Library

SCHEMA_VERSION = 1
DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "library.json"


def default_data_file() -> Path:
    """Data file location, overridable with the ``LIBRARY_DATA_FILE`` environment variable."""
    return Path(os.environ.get("LIBRARY_DATA_FILE", DEFAULT_DATA_FILE))


def library_to_dict(library: Library) -> dict[str, Any]:
    return {
        "version": SCHEMA_VERSION,
        "authors": [author.to_dict() for author in library.authors.values()],
        "books": [book.to_dict() for book in library.books.values()],
        "borrowers": [borrower.to_dict() for borrower in library.borrowers.values()],
    }


def library_from_dict(data: dict[str, Any]) -> Library:
    library = Library()
    library.authors = {item["id"]: Author.from_dict(item) for item in data.get("authors", [])}
    library.books = {
        item["id"]: Book.from_dict(item, library.authors) for item in data.get("books", [])
    }
    library.borrowers = {item["id"]: Borrower.from_dict(item) for item in data.get("borrowers", [])}
    return library


def save_library(library: Library, path: Path | str) -> None:
    """Write the library to ``path`` atomically (temp file + replace)."""
    path = Path(path)
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tmp_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(library_to_dict(library), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_path, path)
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        raise StorageError(f"Could not save library to {path}: {exc}") from exc


def load_library(path: Path | str) -> Library:
    """Load the library from ``path``; a missing file means an empty library."""
    path = Path(path)
    if not path.exists():
        return Library()
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"Data file {path} is not valid JSON (line {exc.lineno}, column {exc.colno})"
        ) from exc
    except OSError as exc:
        raise StorageError(f"Could not read data file {path}: {exc}") from exc

    try:
        return library_from_dict(data)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise StorageError(f"Data file {path} contains invalid records: {exc}") from exc
