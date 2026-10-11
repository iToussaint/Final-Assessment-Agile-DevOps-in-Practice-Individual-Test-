"""Shared pytest fixtures."""

import pytest

from library.inventory import Library


@pytest.fixture
def library() -> Library:
    """A library pre-loaded with a few well-known books."""
    lib = Library()
    lib.add_book("Things Fall Apart", ["Chinua Achebe"], "9780385474542", "Novel", 1958)
    lib.add_book("Arrow of God", ["Chinua Achebe"], "9780385014809", "Novel", 1964)
    lib.add_book(
        "Half of a Yellow Sun",
        ["Chimamanda Ngozi Adichie"],
        "9781400095209",
        "Historical Fiction",
        2006,
    )
    lib.add_book("Good Omens", ["Terry Pratchett", "Neil Gaiman"], "9780060853983", "Fantasy", 1990)
    return lib
