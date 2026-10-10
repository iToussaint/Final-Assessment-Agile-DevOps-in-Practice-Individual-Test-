"""Small, reusable helper functions shared across the package."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date


def generate_id(prefix: str, existing_ids: Iterable[str]) -> str:
    """Return the next sequential id such as ``B001`` for the given prefix.

    >>> generate_id("B", ["B001", "B007", "A003"])
    'B008'
    """
    numbers = [
        int(item[len(prefix) :])
        for item in existing_ids
        if item.startswith(prefix) and item[len(prefix) :].isdigit()
    ]
    return f"{prefix}{max(numbers, default=0) + 1:03d}"


def normalise_isbn(raw: str) -> str:
    """Strip spaces/hyphens from an ISBN and validate its length (10 or 13).

    >>> normalise_isbn("978-0-385-47454-2")
    '9780385474542'
    """
    isbn = "".join(ch for ch in str(raw) if ch not in " -").upper()
    is_isbn10 = len(isbn) == 10 and isbn[:9].isdigit() and (isbn[9].isdigit() or isbn[9] == "X")
    is_isbn13 = len(isbn) == 13 and isbn.isdigit()
    if not (is_isbn10 or is_isbn13):
        raise ValueError(f"Invalid ISBN {raw!r}: expected 10 or 13 digits")
    return isbn


def require_text(value: object, field: str) -> str:
    """Return ``value`` stripped, raising ``ValueError`` if it is blank."""
    text = str(value).strip() if value is not None else ""
    if not text:
        raise ValueError(f"{field} must not be empty")
    return text


def current_year() -> int:
    """Return the current calendar year (wrapped so tests can rely on it)."""
    return date.today().year
