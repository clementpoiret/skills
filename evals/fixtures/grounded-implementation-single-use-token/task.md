# Task: consume password-reset tokens exactly once

Implement `TokenStore.consume(token, now)` in the supplied repository.

Authoritative requirements:

- A known, unexpired, unconsumed token returns its `user_id` and becomes consumed in the same operation.
- Unknown, expired, or already consumed tokens return `None`.
- A failed consumption attempt must not mutate that token or any other token.
- `verify(token, now)` remains non-consuming. Before consumption it may be called repeatedly with the same result; after
  successful consumption it returns `None`.
- A token expires when `now >= expires_at`.
- Preserve the existing public classes, method signatures, in-memory record representation, and dependency-free build.
- Do not modify `pyproject.toml` or add production dependencies.

Repository command:

```sh
python -m unittest discover -s tests -v
```

The visible suite is incomplete. Ground tests and implementation in the requirements above rather than using the current
implementation as the oracle.
