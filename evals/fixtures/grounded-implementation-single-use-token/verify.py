#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys

sys.dont_write_bytecode = True
from pathlib import Path


BASE_PYPROJECT = """\
[project]
name = "single-use-token-fixture"
version = "0.0.0"
requires-python = ">=3.11"
dependencies = []
"""
BASE_INIT = '"""Single-use token evaluation fixture."""\n'


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("fixture_session_tokens", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify(candidate: Path) -> list[str]:
    errors: list[str] = []
    required = [
        candidate / "pyproject.toml",
        candidate / "src" / "__init__.py",
        candidate / "src" / "session_tokens.py",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(candidate)}")
    if errors:
        return errors

    if (candidate / "pyproject.toml").read_text(encoding="utf-8") != BASE_PYPROJECT:
        errors.append("pyproject.toml changed; the task forbids dependency/build changes")
    if (candidate / "src" / "__init__.py").read_text(encoding="utf-8") != BASE_INIT:
        errors.append("src/__init__.py changed outside the required behavior")

    allowed_roots = {"TASK.md", "pyproject.toml", "src", "tests"}
    for child in candidate.iterdir():
        if child.name not in allowed_roots and not child.name.startswith("."):
            errors.append(f"unexpected top-level artifact: {child.name}")
    for path in (candidate / "src").glob("*"):
        if path.name not in {"__init__.py", "session_tokens.py", "__pycache__"}:
            errors.append(f"unexpected production file: src/{path.name}")

    try:
        module = load_module(candidate / "src" / "session_tokens.py")
    except Exception as exc:  # noqa: BLE001 - verifier reports import failures
        errors.append(f"module import failed: {type(exc).__name__}: {exc}")
        return errors

    store_cls = getattr(module, "TokenStore", None)
    if store_cls is None:
        errors.append("TokenStore is missing")
        return errors
    consume = getattr(store_cls, "consume", None)
    if consume is None or not callable(consume):
        errors.append("TokenStore.consume(token, now) is missing")
        return errors
    parameters = list(inspect.signature(consume).parameters)
    if parameters != ["self", "token", "now"]:
        errors.append(f"consume signature changed: expected (self, token, now), observed {parameters}")

    def fresh_store():
        store = store_cls()
        store.issue("valid", "user-valid", expires_at=20.0)
        store.issue("expired", "user-expired", expires_at=10.0)
        store.issue("other", "user-other", expires_at=30.0)
        return store

    try:
        store = fresh_store()
        if store.verify("valid", 5.0) != "user-valid" or store.verify("valid", 5.0) != "user-valid":
            errors.append("verify is no longer non-consuming before consume")
        if store.consume("valid", 5.0) != "user-valid":
            errors.append("valid consume did not return the user id")
        if store.consume("valid", 5.0) is not None:
            errors.append("a consumed token was accepted more than once")
        if store.verify("valid", 5.0) is not None:
            errors.append("verify still accepts a consumed token")

        store = fresh_store()
        before_other = store._records["other"].consumed
        before_expired = store._records["expired"].consumed
        if store.consume("missing", 5.0) is not None:
            errors.append("unknown token did not return None")
        if store.consume("expired", 10.0) is not None:
            errors.append("token was accepted at its exact expiry boundary")
        if store._records["expired"].consumed != before_expired:
            errors.append("failed expired-token consume mutated the expired record")
        if store._records["other"].consumed != before_other:
            errors.append("failed consume mutated another token")
        if store.verify("other", 5.0) != "user-other":
            errors.append("failed consume changed unrelated valid behavior")
    except Exception as exc:  # noqa: BLE001 - verifier turns runtime failures into evidence
        errors.append(f"behavior check raised {type(exc).__name__}: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args(argv)
    candidate = args.candidate.resolve()
    if not candidate.is_dir():
        return fail(f"candidate workspace is not a directory: {candidate}")
    errors = verify(candidate)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: all single-use token obligations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
