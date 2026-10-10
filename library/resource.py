"""Abstract base class shared by every entity managed by the library."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LibraryResource(ABC):
    """Common interface for books, authors and borrowers.

    Every resource has an immutable identifier and must be able to describe
    itself for display and serialise itself for persistence.
    """

    def __init__(self, resource_id: str) -> None:
        if not str(resource_id).strip():
            raise ValueError("Resource id must not be empty")
        self.__id = str(resource_id).strip()

    @property
    def id(self) -> str:
        """Unique identifier of the resource (read-only)."""
        return self.__id

    @abstractmethod
    def describe(self) -> str:
        """Return a human-readable, one-line description."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation of the resource."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LibraryResource):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.id))
