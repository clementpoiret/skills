from __future__ import annotations


class ResponseCache:
    def __init__(self) -> None:
        self._entries: dict[str, tuple[bytes, float]] = {}

    def get(self, key: str, now: float) -> bytes | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if now >= expires_at:
            del self._entries[key]
            return None
        return value

    def put(self, key: str, value: bytes, ttl_seconds: float, now: float) -> None:
        if ttl_seconds <= 0:
            return
        self._entries[key] = (value, now + ttl_seconds)
