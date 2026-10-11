"""Shared pytest fixtures."""

import logging

import pytest

from library.inventory import Library


@pytest.fixture(autouse=True)
def isolated_log_file(tmp_path, monkeypatch):
    """Send every test's logs to a temporary file instead of the project's logs/ folder."""
    log_file = tmp_path / "logs" / "library.log"
    monkeypatch.setenv("LIBRARY_LOG_FILE", str(log_file))
    yield log_file
    logger = logging.getLogger("library")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


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
