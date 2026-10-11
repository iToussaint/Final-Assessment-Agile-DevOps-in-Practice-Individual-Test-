"""Domain-specific exceptions raised by the library package."""


class LibraryError(Exception):
    """Base class for all expected, user-facing library errors."""


class NotFoundError(LibraryError):
    """Raised when a book, author or borrower id does not exist."""


class DuplicateError(LibraryError):
    """Raised when adding a record that already exists (e.g. same ISBN)."""


class LoanError(LibraryError):
    """Raised when a borrow/return breaks a lending rule (already on loan, limit reached...)."""


class StorageError(LibraryError):
    """Raised when the data file cannot be read or written."""
