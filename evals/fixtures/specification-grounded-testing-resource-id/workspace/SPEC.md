# Resource identifier contract

`canonicalize_resource_id(raw)` returns the canonical identifier.

Normative behavior:

1. `raw` must be a string. Any non-string input raises `TypeError`.
2. Remove ASCII space (`U+0020`) and horizontal tab (`U+0009`) only from the beginning and end.
3. After that trim, the identifier length must be from 1 through 12 characters inclusive; otherwise raise `ValueError`.
4. Valid identifier characters are ASCII letters, ASCII digits, hyphen (`-`), and underscore (`_`) only.
5. ASCII uppercase letters are converted to lowercase. Digits, hyphen, and underscore are preserved.
6. Internal whitespace, line breaks, slash, dot, and all non-ASCII characters are invalid and raise `ValueError`.
7. Exception message text is not part of the contract.

The function has no side effects.
