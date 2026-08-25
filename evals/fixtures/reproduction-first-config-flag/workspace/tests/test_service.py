from __future__ import annotations

import unittest

from src.service import feature_enabled


class FeatureFlagTests(unittest.TestCase):
    def test_false_string_disables_feature(self) -> None:
        self.assertFalse(feature_enabled({"FEATURE_X": "false"}))

    def test_missing_flag_uses_default(self) -> None:
        self.assertFalse(feature_enabled({}))


if __name__ == "__main__":
    unittest.main()
