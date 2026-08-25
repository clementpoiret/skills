from __future__ import annotations

import unittest

from src.session_tokens import TokenStore


class TokenStoreTests(unittest.TestCase):
    def test_verify_is_non_consuming(self) -> None:
        store = TokenStore()
        store.issue("token", "user-1", expires_at=20.0)

        self.assertEqual("user-1", store.verify("token", now=10.0))
        self.assertEqual("user-1", store.verify("token", now=10.0))

    def test_consume_returns_user_for_valid_token(self) -> None:
        store = TokenStore()
        store.issue("token", "user-1", expires_at=20.0)

        self.assertEqual("user-1", store.consume("token", now=10.0))


if __name__ == "__main__":
    unittest.main()
