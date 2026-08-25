#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import inspect
import sys

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any


FIXTURE_ROOT = Path(__file__).resolve().parent
BASE_WORKSPACE = FIXTURE_ROOT / "workspace"


class SemanticKey:
    def __init__(self, value: str, hash_value: int | None = None) -> None:
        self.value = value
        self.hash_value = hash(value) if hash_value is None else hash_value

    def __hash__(self) -> int:
        return self.hash_value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SemanticKey) and self.value == other.value


class ProbeKey:
    equality_operations = 0
    hash_operations = 0

    def __init__(self, value: int) -> None:
        self.value = value

    def __hash__(self) -> int:
        type(self).hash_operations += 1
        return self.value * 1_000_003

    def __eq__(self, other: object) -> bool:
        type(self).equality_operations += 1
        return isinstance(other, ProbeKey) and self.value == other.value

    @classmethod
    def reset(cls) -> None:
        cls.equality_operations = 0
        cls.hash_operations = 0

    @classmethod
    def operations(cls) -> int:
        return cls.equality_operations + cls.hash_operations


def load_module(path: Path):
    name = f"fixture_batch_lookup_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def measure(module: Any, size: int) -> tuple[int, list[int | None]]:
    entries = [module.Entry(ProbeKey(index), index) for index in range(size)]
    present = [ProbeKey(index) for index in range(0, size, 2)]
    missing = [ProbeKey(size + index) for index in range(size - len(present))]
    queries = present + missing
    expected = list(range(0, size, 2)) + [None] * len(missing)
    ProbeKey.reset()
    observed = module.resolve_first(entries, queries)
    operations = ProbeKey.operations()
    if not isinstance(observed, list):
        raise AssertionError("resolve_first must return a list")
    if observed != expected:
        raise AssertionError("representative workload returned incorrect results")
    return operations, observed


def verify(candidate: Path) -> list[str]:
    errors: list[str] = []
    required = [
        "pyproject.toml",
        "PERFORMANCE.md",
        "benchmark.py",
        "src/__init__.py",
        "src/batch_lookup.py",
        "tests",
    ]
    for relative in required:
        if not (candidate / relative).exists():
            errors.append(f"missing required path: {relative}")
    if errors:
        return errors

    for relative in (
        "pyproject.toml",
        "PERFORMANCE.md",
        "benchmark.py",
        "src/__init__.py",
    ):
        if (candidate / relative).read_bytes() != (BASE_WORKSPACE / relative).read_bytes():
            errors.append(f"{relative} changed outside the optimization scope")

    allowed_top_level = {
        ".eval-fixture.json",
        "TASK.md",
        "PERFORMANCE.md",
        "benchmark.py",
        "pyproject.toml",
        "src",
        "tests",
    }
    for child in candidate.iterdir():
        if child.name not in allowed_top_level and not child.name.startswith("."):
            errors.append(f"unexpected top-level artifact: {child.name}")
    for path in (candidate / "src").iterdir():
        if path.name not in {"__init__.py", "batch_lookup.py", "__pycache__"}:
            errors.append(f"unexpected production artifact: src/{path.name}")

    if errors:
        return errors

    try:
        module = load_module(candidate / "src" / "batch_lookup.py")
    except Exception as exc:  # noqa: BLE001 - verifier reports candidate import failure
        return [f"module import failed: {type(exc).__name__}: {exc}"]

    entry_cls = getattr(module, "Entry", None)
    resolve = getattr(module, "resolve_first", None)
    if entry_cls is None or not dataclasses.is_dataclass(entry_cls):
        errors.append("Entry must remain a dataclass")
        return errors
    field_names = [field.name for field in dataclasses.fields(entry_cls)]
    if field_names != ["key", "value"]:
        errors.append(f"Entry fields changed: observed {field_names}")
    params = getattr(entry_cls, "__dataclass_params__", None)
    if params is None or not params.frozen:
        errors.append("Entry must remain frozen")
    if resolve is None or not callable(resolve):
        errors.append("resolve_first is missing")
        return errors
    parameter_names = list(inspect.signature(resolve).parameters)
    if parameter_names != ["entries", "queries"]:
        errors.append(
            "resolve_first signature changed: expected (entries, queries), "
            f"observed {parameter_names}"
        )

    try:
        entries = [entry_cls("a", 1), entry_cls("b", 2), entry_cls("a", 3)]
        queries = ["a", "b", "a", "missing"]
        entries_snapshot = list(entries)
        queries_snapshot = list(queries)
        observed = resolve(entries, queries)
        if observed != [1, 2, 1, None]:
            errors.append("first-match, duplicate-query, ordering, or missing semantics changed")
        if entries != entries_snapshot or queries != queries_snapshot:
            errors.append("resolve_first mutated an input sequence")
        if resolve((), ()) != []:
            errors.append("empty sequences did not return an empty list")
        if resolve((), ("x", "x")) != [None, None]:
            errors.append("empty entries did not preserve duplicate missing queries")

        collision = 17
        first_key = SemanticKey("same", collision)
        equal_query = SemanticKey("same", collision)
        other_key = SemanticKey("other", collision)
        collision_entries = [
            entry_cls(first_key, 10),
            entry_cls(other_key, 20),
            entry_cls(SemanticKey("same", collision), 30),
        ]
        if resolve(collision_entries, [equal_query, SemanticKey("other", collision)]) != [10, 20]:
            errors.append("equal distinct or hash-collision keys violate first-match semantics")

        mutable_entries = [entry_cls("key", 1)]
        if resolve(mutable_entries, ["key"]) != [1]:
            errors.append("initial repeated-call check failed")
        mutable_entries[0] = entry_cls("key", 9)
        if resolve(mutable_entries, ["key"]) != [9]:
            errors.append("results are stale across calls; persistent caching is not allowed")
    except Exception as exc:  # noqa: BLE001 - verifier converts runtime failure to evidence
        errors.append(f"correctness check raised {type(exc).__name__}: {exc}")

    try:
        small_size = 180
        large_size = 360
        small_operations, _ = measure(module, small_size)
        large_operations, _ = measure(module, large_size)
        budget = 8 * (large_size + large_size)
        ratio = large_operations / max(small_operations, 1)
        if large_operations > budget:
            errors.append(
                "representative key-operation budget exceeded: "
                f"observed {large_operations}, budget {budget}"
            )
        if ratio > 3.0:
            errors.append(
                "key-operation growth is too steep when workload doubles: "
                f"small {small_operations}, large {large_operations}, ratio {ratio:.3f}"
            )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"performance check raised {type(exc).__name__}: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args(argv)
    candidate = args.candidate.resolve()
    if not candidate.is_dir():
        print(
            f"FAIL: candidate workspace is not a directory: {candidate}",
            file=sys.stderr,
        )
        return 1
    errors = verify(candidate)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: correctness preserved and deterministic performance targets met")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
