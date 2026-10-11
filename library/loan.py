"""A single entry in the borrowing history."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any


@dataclass
class LoanRecord:
    """One loan of one book to one borrower; ``returned_at`` is set on return."""

    book_id: str
    borrower_id: str
    borrowed_at: str
    returned_at: str | None = None

    @property
    def is_active(self) -> bool:
        return self.returned_at is None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoanRecord:
        return cls(**{field.name: data.get(field.name) for field in fields(cls)})
