from __future__ import annotations


def canonicalize_resource_id(raw: object) -> str:
    """Return the canonical resource identifier defined by SPEC.md."""
    if not isinstance(raw, str):
        raise TypeError("resource id must be a string")

    value = raw.strip(" \t")
    if not 1 <= len(value) <= 12:
        raise ValueError("resource id length is invalid")

    canonical: list[str] = []
    for character in value:
        if "A" <= character <= "Z":
            canonical.append(chr(ord(character) + 32))
        elif (
            "a" <= character <= "z"
            or "0" <= character <= "9"
            or character in "-_"
        ):
            canonical.append(character)
        else:
            raise ValueError("resource id contains an invalid character")
    return "".join(canonical)
