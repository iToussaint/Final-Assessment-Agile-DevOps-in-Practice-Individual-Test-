"""Unit tests for search_books() (US-02: AC2.1 - AC2.4)."""

import pytest


def titles(books):
    return [book.title for book in books]


def test_search_by_title_is_partial_and_case_insensitive(library):
    assert titles(library.search_books("FALL", field="title")) == ["Things Fall Apart"]


def test_search_by_author_matches_any_co_author(library):
    assert titles(library.search_books("gaiman", field="author")) == ["Good Omens"]
    assert titles(library.search_books("achebe", field="author")) == [
        "Arrow of God",
        "Things Fall Apart",
    ]


def test_search_all_fields_by_default(library):
    # "sun" matches a title, "chimamanda" matches an author
    assert titles(library.search_books("sun")) == ["Half of a Yellow Sun"]
    assert titles(library.search_books("chimamanda")) == ["Half of a Yellow Sun"]


def test_search_title_only_ignores_author_names(library):
    assert library.search_books("achebe", field="title") == []


def test_search_without_match_returns_empty_list(library):
    assert library.search_books("harry potter") == []


def test_blank_search_term_returns_nothing(library):
    assert library.search_books("   ") == []


def test_unknown_search_field_is_rejected(library):
    with pytest.raises(ValueError):
        library.search_books("x", field="isbn")
