from __future__ import annotations

from collections.abc import Mapping

from .config_flags import parse_bool


def feature_enabled(environment: Mapping[str, str]) -> bool:
    return parse_bool(environment.get("FEATURE_X"), default=False)
