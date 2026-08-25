from __future__ import annotations

import unittest

from src.resource_ids import canonicalize_resource_id


class ResourceIdSmokeTests(unittest.TestCase):
    def test_simple_identifier_is_lowercased(self) -> None:
        self.assertEqual("item-7", canonicalize_resource_id("Item-7"))


if __name__ == "__main__":
    unittest.main()
