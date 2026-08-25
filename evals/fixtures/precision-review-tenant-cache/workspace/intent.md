# Accepted change intent

Add tenant isolation to `ResponseCache` while preserving existing expiry and no-cache behavior.

Repository-local contracts:

- Tenant IDs and caller-provided cache keys are arbitrary non-empty UTF-8 strings. Either may contain `:`.
- Values are immutable `bytes`.
- The cache is intentionally single-threaded; callers serialize access.
- An entry is expired when `now >= expires_at`; expired entries may be removed during `get`.
- `ttl_seconds <= 0` means do not cache.
- `invalidate_tenant` must remove only entries owned by the exact tenant.
