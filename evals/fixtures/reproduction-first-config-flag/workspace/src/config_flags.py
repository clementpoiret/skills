from __future__ import annotations


TRUE_VALUES = frozenset({"true", "1", "yes", "on"})
FALSE_VALUES = frozenset({"false", "0", "no", "off"})


def parse_bool(raw: str | None, *, default: bool = False) -> bool:
    """Parse a repository boolean setting.

    Values are case-insensitive and ignore surrounding whitespace. Accepted true values are
    true/1/yes/on; accepted false values are false/0/no/off. None returns ``default`` and any
    other value raises ValueError.
    """

    if raw is None:
        return default
    return bool(raw)
