#!/usr/bin/env python3
"""Validate Agent Skill evaluation JSONL and summarize recorded trials."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


SKILLS = {
    "change-contract",
    "cross-agent",
    "simplify-after-green",
    "simplify-tests-after-green",
    "jujutsu",
}
CASE_KINDS = {"trigger", "near-miss", "procedure", "failure", "counterfactual"}
INVOCATION_EXPECTATIONS = {"implicit", "explicit", "none", "not-applicable"}
HOSTS = {"codex", "claude"}
ARMS = {"raw", "workflow-memory", "skill"}

CASE_REQUIRED = {
    "id",
    "skill",
    "kind",
    "prompt",
    "expected_invocation",
    "expected",
}
RESULT_REQUIRED = {
    "case_id",
    "skill",
    "host",
    "model",
    "arm",
    "trial",
    "available",
    "selected",
    "accessed",
    "success",
    "failure_category",
    "input_tokens",
    "output_tokens",
    "wall_seconds",
    "notes",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a UTF-8 JSONL file and return object records."""
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc

    for line_number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: each JSONL record must be an object")
        records.append(value)
    return records


def _missing(record: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(required - record.keys())


def validate_cases(records: Iterable[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(records, start=1):
        prefix = f"case record {index}"
        missing = _missing(record, CASE_REQUIRED)
        if missing:
            errors.append(f"{prefix}: missing fields: {', '.join(missing)}")
            continue

        case_id = record["id"]
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{prefix}: id must be a nonempty string")
        elif case_id in seen:
            errors.append(f"{prefix}: duplicate case id: {case_id}")
        else:
            seen.add(case_id)

        if record["skill"] not in SKILLS:
            errors.append(f"{prefix}: unknown skill: {record['skill']!r}")
        if record["kind"] not in CASE_KINDS:
            errors.append(f"{prefix}: invalid kind: {record['kind']!r}")
        if record["expected_invocation"] not in INVOCATION_EXPECTATIONS:
            errors.append(
                f"{prefix}: invalid expected_invocation: {record['expected_invocation']!r}"
            )
        if not isinstance(record["prompt"], str) or not record["prompt"].strip():
            errors.append(f"{prefix}: prompt must be a nonempty string")
        expected = record["expected"]
        if not isinstance(expected, list) or not expected or not all(
            isinstance(item, str) and item.strip() for item in expected
        ):
            errors.append(f"{prefix}: expected must be a nonempty list of strings")

        for optional_string in ("fixture", "notes"):
            if optional_string in record and not isinstance(record[optional_string], str):
                errors.append(f"{prefix}: {optional_string} must be a string when present")
    return errors


def _is_bool_or_none(value: Any) -> bool:
    return isinstance(value, bool) or value is None


def _is_nonnegative_number_or_none(value: Any) -> bool:
    return value is None or (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and value >= 0
    )


def validate_result(record: dict[str, Any], *, index: int | None = None) -> list[str]:
    prefix = f"result record {index}" if index is not None else "result"
    errors: list[str] = []
    missing = _missing(record, RESULT_REQUIRED)
    if missing:
        errors.append(f"{prefix}: missing fields: {', '.join(missing)}")
        return errors

    for field in ("case_id", "model", "notes"):
        if not isinstance(record[field], str):
            errors.append(f"{prefix}: {field} must be a string")
    if not isinstance(record["case_id"], str) or not record["case_id"].strip():
        errors.append(f"{prefix}: case_id must be nonempty")
    if record["skill"] not in SKILLS:
        errors.append(f"{prefix}: unknown skill: {record['skill']!r}")
    if record["host"] not in HOSTS:
        errors.append(f"{prefix}: invalid host: {record['host']!r}")
    if record["arm"] not in ARMS:
        errors.append(f"{prefix}: invalid arm: {record['arm']!r}")
    if not isinstance(record["trial"], int) or isinstance(record["trial"], bool) or record["trial"] < 1:
        errors.append(f"{prefix}: trial must be an integer >= 1")
    if not isinstance(record["available"], bool):
        errors.append(f"{prefix}: available must be boolean")
    for field in ("selected", "accessed", "success"):
        if not _is_bool_or_none(record[field]):
            errors.append(f"{prefix}: {field} must be boolean or null")
    if record["failure_category"] is not None and not isinstance(record["failure_category"], str):
        errors.append(f"{prefix}: failure_category must be a string or null")
    for field in ("input_tokens", "output_tokens", "wall_seconds"):
        if not _is_nonnegative_number_or_none(record[field]):
            errors.append(f"{prefix}: {field} must be a finite nonnegative number or null")

    if record["arm"] == "raw" and record["accessed"] is True:
        errors.append(f"{prefix}: raw arm cannot access the target skill")
    if record["success"] is True and record["failure_category"] not in (None, "none"):
        errors.append(f"{prefix}: successful result must not have a failure category")
    return errors


def validate_results(records: Iterable[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[tuple[str, str, str, str, int]] = set()
    for index, record in enumerate(records, start=1):
        errors.extend(validate_result(record, index=index))
        if RESULT_REQUIRED <= record.keys() and isinstance(record.get("trial"), int):
            key = (
                str(record.get("case_id")),
                str(record.get("host")),
                str(record.get("model")),
                str(record.get("arm")),
                record["trial"],
            )
            if key in seen:
                errors.append(f"result record {index}: duplicate trial key: {key}")
            else:
                seen.add(key)
    return errors


def _rate(records: list[dict[str, Any]], field: str) -> float | None:
    values = [record[field] for record in records if isinstance(record.get(field), bool)]
    if not values:
        return None
    return sum(1 for value in values if value) / len(values)


def _sum_numeric(records: list[dict[str, Any]], field: str) -> int | float | None:
    values = [record[field] for record in records if _is_nonnegative_number_or_none(record.get(field)) and record.get(field) is not None]
    if not values:
        return None
    total = sum(values)
    return int(total) if all(isinstance(value, int) for value in values) else float(total)


def summarize(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["skill"], record["host"], record["model"], record["arm"])].append(record)

    rows: list[dict[str, Any]] = []
    for (skill, host, model, arm), group in sorted(groups.items()):
        failure_counts: dict[str, int] = defaultdict(int)
        for record in group:
            category = record.get("failure_category")
            if category not in (None, "none", ""):
                failure_counts[str(category)] += 1
        rows.append(
            {
                "skill": skill,
                "host": host,
                "model": model,
                "arm": arm,
                "trials": len(group),
                "availability_rate": _rate(group, "available"),
                "selection_rate": _rate(group, "selected"),
                "access_rate": _rate(group, "accessed"),
                "success_rate": _rate(group, "success"),
                "input_tokens": _sum_numeric(group, "input_tokens"),
                "output_tokens": _sum_numeric(group, "output_tokens"),
                "wall_seconds": _sum_numeric(group, "wall_seconds"),
                "failure_categories": dict(sorted(failure_counts.items())),
            }
        )
    return rows


def _format_rate(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def print_summary(rows: list[dict[str, Any]], *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return
    headers = [
        "skill",
        "host",
        "model",
        "arm",
        "trials",
        "available",
        "selected",
        "accessed",
        "success",
        "input_tokens",
        "output_tokens",
        "wall_seconds",
        "failures",
    ]
    print("\t".join(headers))
    for row in rows:
        print(
            "\t".join(
                [
                    str(row["skill"]),
                    str(row["host"]),
                    str(row["model"]),
                    str(row["arm"]),
                    str(row["trials"]),
                    _format_rate(row["availability_rate"]),
                    _format_rate(row["selection_rate"]),
                    _format_rate(row["access_rate"]),
                    _format_rate(row["success_rate"]),
                    str(row["input_tokens"] if row["input_tokens"] is not None else "n/a"),
                    str(row["output_tokens"] if row["output_tokens"] is not None else "n/a"),
                    str(row["wall_seconds"] if row["wall_seconds"] is not None else "n/a"),
                    json.dumps(row["failure_categories"], sort_keys=True),
                ]
            )
        )


def _print_errors(errors: list[str]) -> None:
    for error in errors:
        print(error, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    cases_parser = subparsers.add_parser("check-cases", help="validate an evaluation case catalog")
    cases_parser.add_argument("path", type=Path)

    results_parser = subparsers.add_parser("check-results", help="validate recorded evaluation trials")
    results_parser.add_argument("path", type=Path)

    summary_parser = subparsers.add_parser("summarize", help="summarize recorded evaluation trials")
    summary_parser.add_argument("path", type=Path)
    summary_parser.add_argument("--json", action="store_true", help="emit JSON rather than tab-separated output")

    args = parser.parse_args(argv)
    try:
        records = read_jsonl(args.path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.command == "check-cases":
        errors = validate_cases(records)
        if errors:
            _print_errors(errors)
            return 1
        print(f"case catalog valid: {len(records)} case(s)")
        return 0

    errors = validate_results(records)
    if errors:
        _print_errors(errors)
        return 1
    if args.command == "check-results":
        print(f"results valid: {len(records)} trial(s)")
        return 0

    print_summary(summarize(records), as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
