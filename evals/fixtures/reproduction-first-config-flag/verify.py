#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import sys

sys.dont_write_bytecode = True
from pathlib import Path


BASE_SERVICE = '''\
from __future__ import annotations

from collections.abc import Mapping

from .config_flags import parse_bool


def feature_enabled(environment: Mapping[str, str]) -> bool:
    return parse_bool(environment.get("FEATURE_X"), default=False)
'''
BASE_PYPROJECT = '''\
[project]
name = "config-flag-debug-fixture"
version = "0.0.0"
requires-python = ">=3.11"
dependencies = []
'''



def verify(candidate: Path) -> list[str]:
    errors: list[str] = []
    config_path = candidate / "src" / "config_flags.py"
    service_path = candidate / "src" / "service.py"
    if not config_path.is_file() or not service_path.is_file():
        return ["missing src/config_flags.py or src/service.py"]
    if service_path.read_text(encoding="utf-8") != BASE_SERVICE:
        errors.append("src/service.py changed; the task requires fixing the parser root cause")
    if (candidate / "pyproject.toml").read_text(encoding="utf-8") != BASE_PYPROJECT:
        errors.append("pyproject.toml changed outside the debugging scope")

    sys.path.insert(0, str(candidate))
    try:
        for name in ("src.service", "src.config_flags", "src"):
            sys.modules.pop(name, None)
        flags = importlib.import_module("src.config_flags")
        service = importlib.import_module("src.service")

        true_values = ["true", "TRUE", "  yes ", "1", "On"]
        false_values = ["false", "FALSE", "  no ", "0", "Off"]
        for value in true_values:
            if flags.parse_bool(value) is not True:
                errors.append(f"true value parsed incorrectly: {value!r}")
        for value in false_values:
            if flags.parse_bool(value) is not False:
                errors.append(f"false value parsed incorrectly: {value!r}")
        if flags.parse_bool(None, default=True) is not True:
            errors.append("None did not preserve a true default")
        if flags.parse_bool(None, default=False) is not False:
            errors.append("None did not preserve a false default")
        try:
            flags.parse_bool("sometimes")
        except ValueError:
            pass
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid value raised {type(exc).__name__}, expected ValueError")
        else:
            errors.append("invalid value did not raise ValueError")
        if service.feature_enabled({"FEATURE_X": "false"}) is not False:
            errors.append("original reproduction still fails: FEATURE_X=false is enabled")
        if service.feature_enabled({"FEATURE_X": "yes"}) is not True:
            errors.append("valid true service behavior regressed")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"behavior check raised {type(exc).__name__}: {exc}")
    finally:
        if sys.path and sys.path[0] == str(candidate):
            sys.path.pop(0)
        for name in ("src.service", "src.config_flags", "src"):
            sys.modules.pop(name, None)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args(argv)
    candidate = args.candidate.resolve()
    if not candidate.is_dir():
        print(f"FAIL: candidate workspace is not a directory: {candidate}", file=sys.stderr)
        return 1
    errors = verify(candidate)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: root-cause boolean parsing behavior verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
