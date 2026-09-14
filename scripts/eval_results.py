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


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_PATH = REPO_ROOT / "evals" / "cases.jsonl"


def discover_skills(root: Path = REPO_ROOT) -> set[str]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return set()
    return {
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def discover_fixtures(root: Path = REPO_ROOT) -> set[str]:
    fixtures_root = root / "evals" / "fixtures"
    if not fixtures_root.is_dir():
        return set()
    return {path.parent.name for path in fixtures_root.glob("*/manifest.json")}


SKILLS = discover_skills()
FIXTURES = discover_fixtures()
CASE_KINDS = {
    "trigger",
    "near-miss",
    "confusable",
    "procedure",
    "failure",
    "escape",
    "counterfactual",
}
INVOCATION_EXPECTATIONS = {"implicit", "explicit", "none", "not-applicable"}
HOSTS = {"codex", "claude"}
ARMS = {"no-skill", "skill", "wrong-skill", "workflow-memory"}
BASELINE_ARM = "no-skill"
FAILURE_CATEGORIES = {
    "retrieval-miss",
    "wrong-skill",
    "skill-ignored",
    "skill-misapplied",
    "procedure-not-followed",
    "environment",
    "authentication",
    "network-policy",
    "service-lifecycle",
    "shell-corruption",
    "output-schema",
    "static-only-verification",
    "visible-test-overfit",
    "oracle-contamination",
    "version-mismatch",
    "unrepresentative-workload",
    "benchmark-noise",
    "performance-guardrail",
    "algorithmic",
    "timeout",
    "stale-target",
    "scope-drift",
    "unsafe-mutation",
    "regression",
    "verifier-error",
}

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
    "selected_skill",
    "accessed",
    "procedure_adherent",
    "verifier_passed",
    "success",
    "failure_category",
    "input_tokens",
    "output_tokens",
    "skill_tokens",
    "tool_calls",
    "test_invocations",
    "trajectory_turns",
    "wall_seconds",
    "notes",
}
NUMERIC_FIELDS = {
    "input_tokens",
    "output_tokens",
    "skill_tokens",
    "tool_calls",
    "test_invocations",
    "trajectory_turns",
    "wall_seconds",
}
BOOLEAN_OR_NULL_FIELDS = {
    "selected",
    "accessed",
    "procedure_adherent",
    "verifier_passed",
    "success",
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
            raise ValueError(
                f"{path}:{line_number}: invalid JSON: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise ValueError(
                f"{path}:{line_number}: each JSONL record must be an object"
            )
        records.append(value)
    return records


def _missing(record: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(required - record.keys())


def _string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def validate_cases(records: Iterable[dict[str, Any]]) -> list[str]:
    records = list(records)
    errors: list[str] = []
    seen: set[str] = set()
    kinds_by_skill: dict[str, set[str]] = defaultdict(set)

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

        skill = record["skill"]
        if not isinstance(skill, str) or skill not in SKILLS:
            errors.append(f"{prefix}: unknown skill: {skill!r}")
        kind = record["kind"]
        if not isinstance(kind, str) or kind not in CASE_KINDS:
            errors.append(f"{prefix}: invalid kind: {kind!r}")
        elif isinstance(skill, str) and skill in SKILLS:
            kinds_by_skill[skill].add(kind)

        expected_invocation = record["expected_invocation"]
        if expected_invocation not in INVOCATION_EXPECTATIONS:
            errors.append(
                f"{prefix}: invalid expected_invocation: "
                f"{expected_invocation!r}"
            )
        if not isinstance(record["prompt"], str) or not record["prompt"].strip():
            errors.append(f"{prefix}: prompt must be a nonempty string")
        if not _string_list(record["expected"]):
            errors.append(
                f"{prefix}: expected must be a nonempty list of strings"
            )

        for optional_string in ("fixture", "notes"):
            if optional_string in record and not isinstance(
                record[optional_string], str
            ):
                errors.append(
                    f"{prefix}: {optional_string} must be a string when present"
                )
        fixture = record.get("fixture")
        if isinstance(fixture, str) and fixture and fixture not in FIXTURES:
            errors.append(f"{prefix}: unknown fixture: {fixture!r}")

        confusable_with = record.get("confusable_with")
        if confusable_with is not None:
            if not _string_list(confusable_with):
                errors.append(
                    f"{prefix}: confusable_with must be a nonempty list "
                    "of skill names"
                )
            else:
                unknown = sorted(set(confusable_with) - SKILLS)
                if unknown:
                    errors.append(
                        f"{prefix}: confusable_with contains unknown skills: "
                        f"{', '.join(unknown)}"
                    )
                if skill in confusable_with:
                    errors.append(
                        f"{prefix}: confusable_with cannot contain the target skill"
                    )
        if kind == "confusable" and not _string_list(confusable_with):
            errors.append(
                f"{prefix}: confusable cases require confusable_with"
            )

        expected_not = record.get("expected_not")
        if expected_not is not None and not _string_list(expected_not):
            errors.append(
                f"{prefix}: expected_not must be a nonempty list of strings "
                "when present"
            )

    missing_skills = sorted(SKILLS - kinds_by_skill.keys())
    if missing_skills:
        errors.append(
            f"case catalog: no cases for skills: {', '.join(missing_skills)}"
        )
    for skill in sorted(SKILLS & kinds_by_skill.keys()):
        kinds = kinds_by_skill[skill]
        required = {"trigger", "near-miss", "procedure"}
        missing_kinds = sorted(required - kinds)
        if missing_kinds:
            errors.append(
                f"case catalog: {skill} missing required kinds: "
                f"{', '.join(missing_kinds)}"
            )
        if not ({"failure", "escape"} & kinds):
            errors.append(
                f"case catalog: {skill} requires at least one failure or escape case"
            )
    return errors


def load_case_index(path: Path = DEFAULT_CASES_PATH) -> dict[str, dict[str, Any]]:
    records = read_jsonl(path)
    errors = validate_cases(records)
    if errors:
        raise ValueError("invalid case catalog: " + "; ".join(errors))
    return {record["id"]: record for record in records}


def _is_bool_or_none(value: Any) -> bool:
    return isinstance(value, bool) or value is None


def _is_nonnegative_number_or_none(value: Any) -> bool:
    return value is None or (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and value >= 0
    )


def _valid_failure_category(value: Any) -> bool:
    return (
        value is None
        or value == "none"
        or value in FAILURE_CATEGORIES
        or (isinstance(value, str) and value.startswith("other:") and len(value) > 6)
    )


def validate_result(
    record: dict[str, Any],
    *,
    index: int | None = None,
) -> list[str]:
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
    if not isinstance(record["model"], str) or not record["model"].strip():
        errors.append(f"{prefix}: model must be nonempty")

    skill = record["skill"]
    skill_valid = isinstance(skill, str) and skill in SKILLS
    if not skill_valid:
        errors.append(f"{prefix}: unknown skill: {skill!r}")

    host = record["host"]
    if not isinstance(host, str) or host not in HOSTS:
        errors.append(f"{prefix}: invalid host: {host!r}")

    arm = record["arm"]
    arm_valid = isinstance(arm, str) and arm in ARMS
    if not arm_valid:
        errors.append(f"{prefix}: invalid arm: {arm!r}")

    trial = record["trial"]
    if not isinstance(trial, int) or isinstance(trial, bool) or trial < 1:
        errors.append(f"{prefix}: trial must be an integer >= 1")

    available = record["available"]
    if not isinstance(available, bool):
        errors.append(f"{prefix}: available must be boolean")
    for field in BOOLEAN_OR_NULL_FIELDS:
        if not _is_bool_or_none(record[field]):
            errors.append(f"{prefix}: {field} must be boolean or null")

    selected_skill = record["selected_skill"]
    selected_skill_valid = selected_skill is None or (
        isinstance(selected_skill, str) and selected_skill in SKILLS
    )
    if not selected_skill_valid:
        errors.append(
            f"{prefix}: selected_skill must be a known skill name or null"
        )

    failure_category = record["failure_category"]
    if not _valid_failure_category(failure_category):
        errors.append(
            f"{prefix}: failure_category must be null, a known category, "
            "or other:<specific-label>"
        )
    for field in NUMERIC_FIELDS:
        if not _is_nonnegative_number_or_none(record[field]):
            errors.append(
                f"{prefix}: {field} must be a finite nonnegative number or null"
            )

    if arm_valid and isinstance(available, bool):
        if arm == "skill" and available is not True:
            errors.append(
                f"{prefix}: skill arm must make the target skill available"
            )
        if arm in {"no-skill", "workflow-memory", "wrong-skill"} and available:
            errors.append(
                f"{prefix}: {arm} arm must withhold the target skill"
            )

    selected = record["selected"]
    accessed = record["accessed"]
    if arm_valid:
        if arm in {"no-skill", "workflow-memory", "wrong-skill"} and accessed is True:
            errors.append(f"{prefix}: {arm} arm cannot access the target skill")
        if arm in {"no-skill", "workflow-memory"} and selected is True:
            errors.append(f"{prefix}: {arm} arm cannot select the target skill")
        if arm in {"no-skill", "workflow-memory"} and selected_skill is not None:
            errors.append(f"{prefix}: {arm} arm must have selected_skill null")
        if arm == "wrong-skill":
            if selected_skill is None or selected_skill == skill:
                errors.append(
                    f"{prefix}: wrong-skill arm must record a different "
                    "selected_skill"
                )
            if selected is True:
                errors.append(
                    f"{prefix}: wrong-skill arm cannot select the target skill"
                )
        if arm == "skill" and selected is True and selected_skill != skill:
            errors.append(
                f"{prefix}: selected target skill requires "
                f"selected_skill={skill!r}"
            )

    if selected is True and available is False:
        errors.append(f"{prefix}: unavailable target skill cannot be selected")
    if selected is False and selected_skill == skill:
        errors.append(
            f"{prefix}: selected=false conflicts with selected_skill={skill!r}"
        )
    if accessed is True:
        if available is False:
            errors.append(f"{prefix}: unavailable target skill cannot be accessed")
        if selected is False:
            errors.append(
                f"{prefix}: accessed target skill conflicts with selected=false"
            )
        if selected_skill != skill:
            errors.append(
                f"{prefix}: accessed target skill requires "
                f"selected_skill={skill!r}"
            )

    if arm in {"no-skill", "workflow-memory"} and record["skill_tokens"] not in {
        0,
        0.0,
        None,
    }:
        errors.append(
            f"{prefix}: {arm} arm must have zero or null skill_tokens"
        )

    success = record["success"]
    verifier_passed = record["verifier_passed"]
    if success is True and verifier_passed is not True:
        errors.append(
            f"{prefix}: success requires an independently observed verifier pass"
        )
    if success is True and failure_category not in (None, "none"):
        errors.append(
            f"{prefix}: successful result must not have a failure category"
        )
    if success is False and failure_category in (None, "none"):
        errors.append(
            f"{prefix}: failed result must record a failure category"
        )
    return errors


def validate_results(
    records: Iterable[dict[str, Any]],
    *,
    cases: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
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
                errors.append(
                    f"result record {index}: duplicate trial key: {key}"
                )
            else:
                seen.add(key)

        if cases is None or not isinstance(record.get("case_id"), str):
            continue
        case = cases.get(record["case_id"])
        if case is None:
            errors.append(
                f"result record {index}: unknown case_id: {record['case_id']!r}"
            )
            continue
        if record.get("skill") != case.get("skill"):
            errors.append(
                f"result record {index}: skill {record.get('skill')!r} does not "
                f"match case skill {case.get('skill')!r}"
            )
        if record.get("arm") == "wrong-skill":
            confusable = case.get("confusable_with")
            if _string_list(confusable) and record.get("selected_skill") not in confusable:
                errors.append(
                    f"result record {index}: wrong-skill selection "
                    f"{record.get('selected_skill')!r} is not one of the case's "
                    f"confusable skills: {', '.join(confusable)}"
                )
    return errors


def _rate(records: list[dict[str, Any]], field: str) -> float | None:
    values = [record[field] for record in records if isinstance(record.get(field), bool)]
    if not values:
        return None
    return sum(1 for value in values if value) / len(values)


def _sum_numeric(
    records: list[dict[str, Any]],
    field: str,
) -> int | float | None:
    values = [
        record[field]
        for record in records
        if record.get(field) is not None
        and _is_nonnegative_number_or_none(record.get(field))
    ]
    if not values:
        return None
    total = sum(values)
    return int(total) if all(isinstance(value, int) for value in values) else float(total)


def _mean_numeric(
    records: list[dict[str, Any]],
    field: str,
) -> float | None:
    values = [
        float(record[field])
        for record in records
        if record.get(field) is not None
        and _is_nonnegative_number_or_none(record.get(field))
    ]
    return None if not values else sum(values) / len(values)


def _paired_bool_delta(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
    field: str,
) -> float | None:
    deltas = [
        float(candidate[field]) - float(baseline[field])
        for candidate, baseline in pairs
        if isinstance(candidate.get(field), bool)
        and isinstance(baseline.get(field), bool)
    ]
    return None if not deltas else sum(deltas) / len(deltas)


def _paired_numeric_delta(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
    field: str,
) -> float | None:
    deltas = [
        float(candidate[field]) - float(baseline[field])
        for candidate, baseline in pairs
        if candidate.get(field) is not None
        and baseline.get(field) is not None
        and _is_nonnegative_number_or_none(candidate.get(field))
        and _is_nonnegative_number_or_none(baseline.get(field))
    ]
    return None if not deltas else sum(deltas) / len(deltas)


def summarize(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    records = list(records)
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[(record["skill"], record["host"], record["model"], record["arm"])].append(record)

    baselines = {
        (
            record["skill"],
            record["host"],
            record["model"],
            record["case_id"],
            record["trial"],
        ): record
        for record in records
        if record["arm"] == BASELINE_ARM
    }

    rows: list[dict[str, Any]] = []
    for (skill, host, model, arm), group in sorted(groups.items()):
        failure_counts: dict[str, int] = defaultdict(int)
        for record in group:
            category = record.get("failure_category")
            if category not in (None, "none", ""):
                failure_counts[str(category)] += 1

        pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
        if arm != BASELINE_ARM:
            for record in group:
                baseline = baselines.get(
                    (
                        skill,
                        host,
                        model,
                        record["case_id"],
                        record["trial"],
                    )
                )
                if baseline is not None:
                    pairs.append((record, baseline))

        row: dict[str, Any] = {
            "skill": skill,
            "host": host,
            "model": model,
            "arm": arm,
            "trials": len(group),
            "availability_rate": _rate(group, "available"),
            "selection_rate": _rate(group, "selected"),
            "access_rate": _rate(group, "accessed"),
            "procedure_adherence_rate": _rate(group, "procedure_adherent"),
            "verifier_pass_rate": _rate(group, "verifier_passed"),
            "success_rate": _rate(group, "success"),
            "failure_categories": dict(sorted(failure_counts.items())),
            "matched_pairs_vs_no_skill": len(pairs),
            "paired_delta_adherence_vs_no_skill": _paired_bool_delta(
                pairs,
                "procedure_adherent",
            ),
            "paired_delta_verifier_vs_no_skill": _paired_bool_delta(
                pairs,
                "verifier_passed",
            ),
            "paired_delta_success_vs_no_skill": _paired_bool_delta(
                pairs,
                "success",
            ),
        }
        for field in sorted(NUMERIC_FIELDS):
            row[field] = _sum_numeric(group, field)
            row[f"mean_{field}"] = _mean_numeric(group, field)
            row[f"paired_delta_{field}_vs_no_skill"] = _paired_numeric_delta(
                pairs,
                field,
            )
        rows.append(row)
    return rows


def _format_rate(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def _format_number(value: int | float | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def print_summary(
    rows: list[dict[str, Any]],
    *,
    as_json: bool = False,
) -> None:
    if as_json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return
    headers = [
        "skill",
        "host",
        "model",
        "arm",
        "trials",
        "selected",
        "accessed",
        "adherent",
        "verifier",
        "success",
        "matched_pairs",
        "paired_delta_adherence",
        "paired_delta_verifier",
        "paired_delta_success",
        "mean_input_tokens",
        "mean_output_tokens",
        "mean_skill_tokens",
        "mean_tool_calls",
        "mean_test_invocations",
        "mean_trajectory_turns",
        "mean_wall_seconds",
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
                    _format_rate(row["selection_rate"]),
                    _format_rate(row["access_rate"]),
                    _format_rate(row["procedure_adherence_rate"]),
                    _format_rate(row["verifier_pass_rate"]),
                    _format_rate(row["success_rate"]),
                    str(row["matched_pairs_vs_no_skill"]),
                    _format_rate(row["paired_delta_adherence_vs_no_skill"]),
                    _format_rate(row["paired_delta_verifier_vs_no_skill"]),
                    _format_rate(row["paired_delta_success_vs_no_skill"]),
                    _format_number(row["mean_input_tokens"]),
                    _format_number(row["mean_output_tokens"]),
                    _format_number(row["mean_skill_tokens"]),
                    _format_number(row["mean_tool_calls"]),
                    _format_number(row["mean_test_invocations"]),
                    _format_number(row["mean_trajectory_turns"]),
                    _format_number(row["mean_wall_seconds"]),
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

    cases_parser = subparsers.add_parser(
        "check-cases",
        help="validate an evaluation case catalog",
    )
    cases_parser.add_argument("path", type=Path)

    results_parser = subparsers.add_parser(
        "check-results",
        help="validate recorded evaluation trials",
    )
    results_parser.add_argument("path", type=Path)
    results_parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="case catalog used to validate case IDs and target skills",
    )

    summary_parser = subparsers.add_parser(
        "summarize",
        help="summarize recorded evaluation trials",
    )
    summary_parser.add_argument("path", type=Path)
    summary_parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="case catalog used to validate case IDs and target skills",
    )
    summary_parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON rather than tab-separated output",
    )

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

    try:
        cases = load_case_index(args.cases)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    errors = validate_results(records, cases=cases)
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
