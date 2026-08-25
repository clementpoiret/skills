from __future__ import annotations


class ResponseCache:
    def __init__(self) -> None:
        self._entries: dict[str, tuple[bytes, float]] = {}

    @staticmethod
    def _tenant_key(tenant_id: str, key: str) -> str:
        return f"{tenant_id}:{key}"

    def get(self, tenant_id: str, key: str, now: float) -> bytes | None:
        storage_key = self._tenant_key(tenant_id, key)
        entry = self._entries.get(storage_key)
        if entry is None:
            return None
        value, expires_at = entry
        if now >= expires_at:
            del self._entries[storage_key]
            return None
        return value

    def put(self, tenant_id: str, key: str, value: bytes, ttl_seconds: float, now: float) -> None:
        if ttl_seconds <= 0:
            return
        self._entries[self._tenant_key(tenant_id, key)] = (value, now + ttl_seconds)

    def invalidate_tenant(self, tenant_id: str) -> None:
        prefix = f"{tenant_id}:"
        for storage_key in [key for key in self._entries if key.startswith(prefix)]:
            del self._entries[storage_key]
