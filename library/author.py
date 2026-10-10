"""The Author entity."""

from __future__ import annotations

from typing import Any

from library.resource import LibraryResource
from library.utils import require_text


class Author(LibraryResource):
    """A person who wrote one or more books."""

    def __init__(self, author_id: str, name: str) -> None:
        super().__init__(author_id)
        self.name = name

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = " ".join(require_text(value, "Author name").split())

    def describe(self) -> str:
        return self.name

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Author:
        return cls(author_id=data["id"], name=data["name"])

    def __repr__(self) -> str:
        return f"Author(id={self.id!r}, name={self.name!r})"

    def __eq__(self, other: object) -> bool:
        """Two authors are the same person if their names match (case-insensitive)."""
        if not isinstance(other, Author):
            return NotImplemented
        return self.name.casefold() == other.name.casefold()

    def __hash__(self) -> int:
        return hash(self.name.casefold())
