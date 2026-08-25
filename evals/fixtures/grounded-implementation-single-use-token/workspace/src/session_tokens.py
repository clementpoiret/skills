from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TokenRecord:
    user_id: str
    expires_at: float
    consumed: bool = False


class TokenStore:
    def __init__(self) -> None:
        self._records: dict[str, TokenRecord] = {}

    def issue(self, token: str, user_id: str, expires_at: float) -> None:
        self._records[token] = TokenRecord(user_id=user_id, expires_at=expires_at)

    def verify(self, token: str, now: float) -> str | None:
        record = self._records.get(token)
        if record is None or record.consumed or now >= record.expires_at:
            return None
        return record.user_id
