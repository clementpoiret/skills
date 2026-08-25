from __future__ import annotations

from collections.abc import Hashable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entry:
    key: Hashable
    value: int


def resolve_first(
    entries: Sequence[Entry],
    queries: Sequence[Hashable],
) -> list[int | None]:
    """Resolve each query to the value of its first matching entry."""
    return [
        next((entry.value for entry in entries if entry.key == query), None)
        for query in queries
    ]
