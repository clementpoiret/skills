#!/usr/bin/env python3
"""Validate, materialize, and run deterministic Agent Skill evaluation fixtures."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_ROOT = REPO_ROOT / "evals" / "fixtures"
MANIFEST_REQUIRED = {"id", "skill", "mode", "task", "workspace", "verifier"}
MODES = {"workspace", "artifact"}


def discover_skills(root: Path = REPO_ROOT) -> set[str]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return set()
    return {
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: manifest must be a JSON object")
    return value


def load_manifest_entries(
    root: Path = FIXTURES_ROOT,
) -> list[tuple[Path, dict[str, Any]]]:
    """Load every manifest, including malformed IDs that validation must report."""
    if not root.is_dir():
        return []
    return [
        (path.parent, read_manifest(path))
        for path in sorted(root.glob("*/manifest.json"))
    ]


def discover_manifests(
    root: Path = FIXTURES_ROOT,
) -> dict[str, tuple[Path, dict[str, Any]]]:
    """Return operationally usable manifests, rejecting invalid or duplicate IDs."""
    manifests: dict[str, tuple[Path, dict[str, Any]]] = {}
    for fixture_dir, manifest in load_manifest_entries(root):
        fixture_id = manifest.get("id")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise ValueError(f"{fixture_dir}: id must be a nonempty string")
        if fixture_id in manifests:
            other_dir = manifests[fixture_id][0]
            raise ValueError(
                f"duplicate fixture id {fixture_id!r}: {other_dir} and {fixture_dir}"
            )
        manifests[fixture_id] = (fixture_dir, manifest)
    return manifests


def _contained_path(
    fixture_dir: Path,
    value: Any,
    *,
    field: str,
    directory: bool,
) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value:
        return None, f"{fixture_dir}: {field} must be a nonempty relative path"
    if Path(value).is_absolute():
        return None, f"{fixture_dir}: {field} must be a relative path"

    root = fixture_dir.resolve()
    unresolved_target = fixture_dir / value
    if unresolved_target.is_symlink():
        return None, f"{fixture_dir}: {field} must not be a symlink"
    target = unresolved_target.resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None, f"{fixture_dir}: {field} escapes the fixture directory"

    if directory and not target.is_dir():
        return None, f"{fixture_dir}: workspace directory does not exist: {value}"
    if not directory and not target.is_file():
        return None, f"{fixture_dir}: file does not exist: {value}"
    return target, None


def validate_fixture(
    fixture_dir: Path,
    manifest: dict[str, Any],
    *,
    skills: set[str],
) -> list[str]:
    errors: list[str] = []
    missing = sorted(MANIFEST_REQUIRED - manifest.keys())
    if missing:
        return [f"{fixture_dir}: missing manifest fields: {', '.join(missing)}"]

    fixture_id = manifest["id"]
    if not isinstance(fixture_id, str) or not fixture_id:
        errors.append(f"{fixture_dir}: id must be a nonempty string")
    elif fixture_id != fixture_dir.name:
        errors.append(
            f"{fixture_dir}: id {fixture_id!r} must match directory name"
        )

    skill = manifest["skill"]
    if not isinstance(skill, str) or not skill:
        errors.append(f"{fixture_dir}: skill must be a nonempty string")
    elif skill not in skills:
        errors.append(f"{fixture_dir}: unknown skill {skill!r}")

    mode = manifest["mode"]
    if not isinstance(mode, str) or mode not in MODES:
        errors.append(
            f"{fixture_dir}: mode must be one of {sorted(MODES)}, observed {mode!r}"
        )

    for field in ("task", "verifier"):
        _, error = _contained_path(
            fixture_dir,
            manifest[field],
            field=field,
            directory=False,
        )
        if error:
            errors.append(error)
    _, error = _contained_path(
        fixture_dir,
        manifest["workspace"],
        field="workspace",
        directory=True,
    )
    if error:
        errors.append(error)

    if mode == "workspace" and manifest.get("baseline_expected") not in {
        "pass",
        "fail",
    }:
        errors.append(
            f"{fixture_dir}: workspace fixture requires baseline_expected pass|fail"
        )
    if mode == "artifact":
        for field in ("accepted_sample", "rejected_sample"):
            _, error = _contained_path(
                fixture_dir,
                manifest.get(field),
                field=field,
                directory=False,
            )
            if error:
                errors.append(error)
    return errors


def _repository_root_for_fixtures(root: Path) -> Path:
    resolved = root.resolve()
    if resolved.name == "fixtures" and resolved.parent.name == "evals":
        return resolved.parent.parent
    return REPO_ROOT


def validate_all(root: Path = FIXTURES_ROOT) -> list[str]:
    errors: list[str] = []
    skills = discover_skills(_repository_root_for_fixtures(root))
    try:
        entries = load_manifest_entries(root)
    except ValueError as exc:
        return [str(exc)]
    if not entries:
        return [f"{root}: no fixtures found"]

    seen: dict[str, Path] = {}
    for fixture_dir, manifest in entries:
        fixture_id = manifest.get("id")
        if isinstance(fixture_id, str) and fixture_id:
            if fixture_id in seen:
                errors.append(
                    f"duplicate fixture id {fixture_id!r}: "
                    f"{seen[fixture_id]} and {fixture_dir}"
                )
            else:
                seen[fixture_id] = fixture_dir
        errors.extend(validate_fixture(fixture_dir, manifest, skills=skills))
    return errors


def run_verifier(
    fixture_dir: Path,
    manifest: dict[str, Any],
    candidate: Path,
    *,
    timeout: float = 30.0,
) -> subprocess.CompletedProcess[str]:
    verifier = (fixture_dir / str(manifest["verifier"])).resolve()
    return subprocess.run(
        [sys.executable, str(verifier), str(candidate)],
        cwd=fixture_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def self_check(root: Path = FIXTURES_ROOT) -> list[str]:
    errors = validate_all(root)
    if errors:
        return errors
    try:
        manifests = discover_manifests(root)
    except ValueError as exc:
        return [str(exc)]

    for fixture_id, (fixture_dir, manifest) in manifests.items():
        mode = manifest["mode"]
        try:
            if mode == "workspace":
                candidate = fixture_dir / str(manifest["workspace"])
                result = run_verifier(fixture_dir, manifest, candidate)
                expected_pass = manifest["baseline_expected"] == "pass"
                if (result.returncode == 0) != expected_pass:
                    errors.append(
                        f"{fixture_id}: baseline verifier expectation mismatch; "
                        f"exit={result.returncode}; stdout={result.stdout.strip()!r}; "
                        f"stderr={result.stderr.strip()!r}"
                    )
            else:
                accepted = fixture_dir / str(manifest["accepted_sample"])
                rejected = fixture_dir / str(manifest["rejected_sample"])
                accepted_result = run_verifier(fixture_dir, manifest, accepted)
                rejected_result = run_verifier(fixture_dir, manifest, rejected)
                if accepted_result.returncode != 0:
                    errors.append(
                        f"{fixture_id}: accepted sample failed; "
                        f"stdout={accepted_result.stdout.strip()!r}; "
                        f"stderr={accepted_result.stderr.strip()!r}"
                    )
                if rejected_result.returncode == 0:
                    errors.append(
                        f"{fixture_id}: rejected sample unexpectedly passed"
                    )
        except subprocess.TimeoutExpired:
            errors.append(f"{fixture_id}: verifier exceeded 30 seconds")
    return errors


def get_fixture(
    fixture_id: str,
    root: Path = FIXTURES_ROOT,
) -> tuple[Path, dict[str, Any]]:
    validation_errors = validate_all(root)
    if validation_errors:
        raise ValueError("; ".join(validation_errors))
    manifests = discover_manifests(root)
    try:
        return manifests[fixture_id]
    except KeyError as exc:
        raise ValueError(f"unknown fixture: {fixture_id}") from exc


def materialize(
    fixture_id: str,
    destination: Path,
    *,
    root: Path = FIXTURES_ROOT,
) -> Path:
    fixture_dir, manifest = get_fixture(fixture_id, root)
    destination = destination.resolve()
    fixture_root = fixture_dir.resolve()
    try:
        destination.relative_to(fixture_root)
    except ValueError:
        pass
    else:
        raise ValueError(
            "destination must be outside the fixture directory so hidden "
            f"verifier files are not exposed: {destination}"
        )
    if destination.exists():
        if not destination.is_dir() or any(destination.iterdir()):
            raise ValueError(
                f"destination must not exist or must be empty: {destination}"
            )
    destination.mkdir(parents=True, exist_ok=True)
    workspace = fixture_dir / str(manifest["workspace"])
    shutil.copytree(workspace, destination, dirs_exist_ok=True)
    shutil.copy2(
        fixture_dir / str(manifest["task"]),
        destination / "TASK.md",
    )
    (destination / ".eval-fixture.json").write_text(
        json.dumps(
            {
                "id": fixture_id,
                "skill": manifest["skill"],
                "mode": manifest["mode"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "check",
        help="validate fixture structure and verifier self-tests",
    )
    list_parser = subparsers.add_parser("list", help="list available fixtures")
    list_parser.add_argument("--json", action="store_true")

    materialize_parser = subparsers.add_parser(
        "materialize",
        help="copy a fixture workspace without its verifier",
    )
    materialize_parser.add_argument("fixture_id")
    materialize_parser.add_argument("destination", type=Path)

    verify_parser = subparsers.add_parser(
        "verify",
        help="run one fixture verifier against a candidate",
    )
    verify_parser.add_argument("fixture_id")
    verify_parser.add_argument("candidate", type=Path)
    verify_parser.add_argument(
        "--allow-untrusted-code",
        action="store_true",
        help=(
            "acknowledge that workspace verifiers execute candidate code; "
            "use only inside a disposable sandbox"
        ),
    )

    args = parser.parse_args(argv)
    if args.command == "check":
        errors = self_check()
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print(
            f"fixture validation passed: {len(discover_manifests())} fixture(s)"
        )
        return 0

    if args.command == "list":
        try:
            manifests = discover_manifests()
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 1
        rows = [
            {
                "id": fixture_id,
                "skill": manifest["skill"],
                "mode": manifest["mode"],
            }
            for fixture_id, (_, manifest) in sorted(manifests.items())
        ]
        if args.json:
            print(json.dumps(rows, indent=2, sort_keys=True))
        else:
            for row in rows:
                print(f"{row['id']}\t{row['skill']}\t{row['mode']}")
        return 0

    try:
        if args.command == "materialize":
            path = materialize(args.fixture_id, args.destination)
            print(path)
            return 0
        fixture_dir, manifest = get_fixture(args.fixture_id)
        if manifest["mode"] == "workspace" and not args.allow_untrusted_code:
            print(
                "refusing to execute candidate code without "
                "--allow-untrusted-code; run workspace verification only "
                "inside a disposable sandbox",
                file=sys.stderr,
            )
            return 2
        result = run_verifier(
            fixture_dir,
            manifest,
            args.candidate.resolve(),
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("verifier exceeded 30 seconds", file=sys.stderr)
        return 124

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
