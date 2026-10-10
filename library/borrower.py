"""The Borrower entity."""

from __future__ import annotations

import re
from typing import Any

from library.resource import LibraryResource
from library.utils import require_text

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Borrower(LibraryResource):
    """A registered library member who can borrow books."""

    def __init__(
        self,
        borrower_id: str,
        name: str,
        email: str,
        borrowed_book_ids: list[str] | None = None,
    ) -> None:
        super().__init__(borrower_id)
        self.name = name
        self.email = email
        self.__borrowed_book_ids = list(borrowed_book_ids or [])

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = " ".join(require_text(value, "Borrower name").split())

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str) -> None:
        email = require_text(value, "E-mail").lower()
        if not EMAIL_PATTERN.match(email):
            raise ValueError(f"Invalid e-mail address: {value!r}")
        self.__email = email

    @property
    def borrowed_book_ids(self) -> tuple[str, ...]:
        """Ids of the books currently on loan (read-only view)."""
        return tuple(self.__borrowed_book_ids)

    def describe(self) -> str:
        return f"[{self.id}] {self.name} <{self.email}> - {len(self.__borrowed_book_ids)} on loan"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "borrowed_book_ids": list(self.__borrowed_book_ids),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Borrower:
        return cls(
            borrower_id=data["id"],
            name=data["name"],
            email=data["email"],
            borrowed_book_ids=data.get("borrowed_book_ids", []),
        )

    def __repr__(self) -> str:
        return f"Borrower(id={self.id!r}, name={self.name!r}, email={self.email!r})"

    def __eq__(self, other: object) -> bool:
        """Borrowers are identified by their (unique) e-mail address."""
        if not isinstance(other, Borrower):
            return NotImplemented
        return self.email == other.email

    def __hash__(self) -> int:
        return hash(self.email)
