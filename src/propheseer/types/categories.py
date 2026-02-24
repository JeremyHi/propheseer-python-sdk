"""Category type definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from propheseer._base_client import _transform_keys


@dataclass
class Category:
    """A market category with its subcategories.

    Attributes:
        id: Category identifier.
        name: Display name.
        subcategories: List of subcategory identifiers.
    """

    id: str
    name: str
    subcategories: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        """Create a Category from a dictionary, handling camelCase keys."""
        transformed = _transform_keys(data)
        return cls(
            id=transformed.get("id", ""),
            name=transformed.get("name", ""),
            subcategories=transformed.get("subcategories", []),
        )
