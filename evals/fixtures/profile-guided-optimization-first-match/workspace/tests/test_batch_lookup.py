from __future__ import annotations

import unittest

from src.batch_lookup import Entry, resolve_first


class BatchLookupTests(unittest.TestCase):
    def test_preserves_first_match_and_query_order(self) -> None:
        entries = [
            Entry("a", 1),
            Entry("b", 2),
            Entry("a", 3),
        ]
        self.assertEqual([1, 2, 1, None], resolve_first(entries, ["a", "b", "a", "x"]))

    def test_empty_inputs(self) -> None:
        self.assertEqual([], resolve_first([], []))
        self.assertEqual([None], resolve_first([], ["missing"]))


if __name__ == "__main__":
    unittest.main()
