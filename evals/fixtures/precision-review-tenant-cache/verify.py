#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any


EXPECTED_ID = "tenant-cache-key-collision"
REQUIRED_FIELDS = {
    "id",
    "severity",
    "location",
    "mechanism",
    "trigger",
    "consequence",
    "evidence",
    "verification",
}
FORBIDDEN_IDS = {
    "missing-lock",
    "expiry-comparison",
    "zero-ttl",
    "mutable-value",
}


def verify(artifact: Path) -> list[str]:
    errors: list[str] = []
    try:
        value: Any = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot parse review JSON: {exc}"]
    if not isinstance(value, dict) or not isinstance(value.get("findings"), list):
        return ["review must be an object with a findings list"]
    findings = value["findings"]
    ids: list[str] = []
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"finding {index} is not an object")
            continue
        missing = sorted(REQUIRED_FIELDS - finding.keys())
        if missing:
            errors.append(f"finding {index} missing fields: {', '.join(missing)}")
            continue
        for field in REQUIRED_FIELDS:
            if not isinstance(finding[field], str) or not finding[field].strip():
                errors.append(f"finding {index} field {field} must be a nonempty string")
        ids.append(str(finding.get("id")))

    if EXPECTED_ID not in ids:
        errors.append("missed the tenant/key delimiter collision defect")
    extra = [finding_id for finding_id in ids if finding_id != EXPECTED_ID]
    if extra:
        errors.append(f"unsupported extra findings increase false-positive burden: {', '.join(extra)}")
    forbidden = sorted(FORBIDDEN_IDS & set(ids))
    if forbidden:
        errors.append(f"reported contract-contradicted findings: {', '.join(forbidden)}")
    if ids.count(EXPECTED_ID) > 1:
        errors.append("duplicated one root cause as multiple findings")

    expected = next(
        (
            finding
            for finding in findings
            if isinstance(finding, dict) and finding.get("id") == EXPECTED_ID
        ),
        None,
    )
    if expected:
        combined = " ".join(
            str(expected.get(field, ""))
            for field in (
                "mechanism",
                "trigger",
                "consequence",
                "evidence",
                "verification",
            )
        ).lower()
        for token in ("tenant", "key", "colon"):
            if token not in combined:
                errors.append(f"validated finding does not explain the {token} condition")
        if "collision" not in combined and "same storage" not in combined and "not injective" not in combined:
            errors.append("validated finding does not explain the key-collision mechanism")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args(argv)
    artifact = args.artifact.resolve()
    if not artifact.is_file():
        print(f"FAIL: review artifact is not a file: {artifact}", file=sys.stderr)
        return 1
    errors = verify(artifact)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: review found the real defect without unsupported findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
