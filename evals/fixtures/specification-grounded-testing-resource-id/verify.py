#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

sys.dont_write_bytecode = True
from pathlib import Path


FIXTURE_ROOT = Path(__file__).resolve().parent
BASE_WORKSPACE = FIXTURE_ROOT / "workspace"

CORRECT_ALTERNATE = textwrap.dedent(
    '''\
    from __future__ import annotations

    import re


    _VALID = re.compile(r"[A-Za-z0-9_-]{1,12}", re.ASCII)


    def canonicalize_resource_id(raw: object) -> str:
        if not isinstance(raw, str):
            raise TypeError("expected string")
        value = raw.strip(" \\t")
        if _VALID.fullmatch(value) is None:
            raise ValueError("invalid resource id")
        return value.lower()
    '''
)

CORRECT_MANUAL = textwrap.dedent(
    '''\
    from __future__ import annotations


    def canonicalize_resource_id(raw: object) -> str:
        if not isinstance(raw, str):
            raise TypeError("string required")
        start = 0
        end = len(raw)
        while start < end and raw[start] in " \t":
            start += 1
        while end > start and raw[end - 1] in " \t":
            end -= 1
        value = raw[start:end]
        if len(value) < 1 or len(value) > 12:
            raise ValueError("length")
        result: list[str] = []
        for character in value:
            code = ord(character)
            if 65 <= code <= 90:
                result.append(chr(code + 32))
            elif 97 <= code <= 122 or 48 <= code <= 57 or character in {"-", "_"}:
                result.append(character)
            else:
                raise ValueError("character")
        return "".join(result)
    '''
)

WRONG_VARIANTS = {
    "unicode-whitespace-strip": textwrap.dedent(
        '''\
        from __future__ import annotations

        import re


        _VALID = re.compile(r"[A-Za-z0-9_-]{1,12}", re.ASCII)


        def canonicalize_resource_id(raw: object) -> str:
            if not isinstance(raw, str):
                raise TypeError("expected string")
            value = raw.strip()
            if _VALID.fullmatch(value) is None:
                raise ValueError("invalid resource id")
            return value.lower()
        '''
    ),
    "length-before-trim": textwrap.dedent(
        '''\
        from __future__ import annotations

        import re


        _VALID = re.compile(r"[A-Za-z0-9_-]+", re.ASCII)


        def canonicalize_resource_id(raw: object) -> str:
            if not isinstance(raw, str):
                raise TypeError("expected string")
            if not 1 <= len(raw) <= 12:
                raise ValueError("invalid length")
            value = raw.strip(" \\t")
            if _VALID.fullmatch(value) is None:
                raise ValueError("invalid resource id")
            return value.lower()
        '''
    ),
    "permissive-punctuation": textwrap.dedent(
        '''\
        from __future__ import annotations

        import re


        _VALID = re.compile(r"[A-Za-z0-9_./-]{1,12}", re.ASCII)


        def canonicalize_resource_id(raw: object) -> str:
            if not isinstance(raw, str):
                raise TypeError("expected string")
            value = raw.strip(" \\t")
            if _VALID.fullmatch(value) is None:
                raise ValueError("invalid resource id")
            return value.lower()
        '''
    ),
    "unicode-alphanumeric": textwrap.dedent(
        '''\
        from __future__ import annotations


        def canonicalize_resource_id(raw: object) -> str:
            if not isinstance(raw, str):
                raise TypeError("expected string")
            value = raw.strip(" \\t")
            if not 1 <= len(value) <= 12:
                raise ValueError("invalid length")
            if not all(character.isalnum() or character in "-_" for character in value):
                raise ValueError("invalid resource id")
            return value.lower()
        '''
    ),
    "coerce-non-string": textwrap.dedent(
        '''\
        from __future__ import annotations

        import re


        _VALID = re.compile(r"[A-Za-z0-9_-]{1,12}", re.ASCII)


        def canonicalize_resource_id(raw: object) -> str:
            value = str(raw).strip(" \\t")
            if _VALID.fullmatch(value) is None:
                raise ValueError("invalid resource id")
            return value.lower()
        '''
    ),
    "internal-ascii-whitespace": textwrap.dedent(
        '''\
        from __future__ import annotations

        import re


        _VALID = re.compile(r"[A-Za-z0-9_ \t-]{1,12}", re.ASCII)


        def canonicalize_resource_id(raw: object) -> str:
            if not isinstance(raw, str):
                raise TypeError("expected string")
            value = raw.strip(" \t")
            if _VALID.fullmatch(value) is None:
                raise ValueError("invalid resource id")
            return value.lower()
        '''
    ),
}


def run_suite(candidate: Path, implementation: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="resource-id-oracle-") as tmp:
        workspace = Path(tmp) / "workspace"
        shutil.copytree(candidate, workspace)
        (workspace / "src" / "resource_ids.py").write_text(
            implementation,
            encoding="utf-8",
        )
        for cache in workspace.rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)

        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "tests",
                    "-v",
                ],
                cwd=workspace,
                env=environment,
                text=True,
                capture_output=True,
                timeout=20,
                check=False,
            )
            output = process.stdout + process.stderr
            return process.returncode == 0, output
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            return False, f"test execution timed out: {output[-800:]}"
        except BaseException as exc:  # noqa: BLE001 - verifier reports infrastructure failure
            return False, f"test execution raised {type(exc).__name__}: {exc}"


def verify(candidate: Path) -> list[str]:
    errors: list[str] = []
    required = [
        "pyproject.toml",
        "SPEC.md",
        "src/__init__.py",
        "src/resource_ids.py",
        "tests",
    ]
    for relative in required:
        if not (candidate / relative).exists():
            errors.append(f"missing required path: {relative}")
    if errors:
        return errors

    for relative in (
        "pyproject.toml",
        "SPEC.md",
        "src/__init__.py",
        "src/resource_ids.py",
    ):
        if (candidate / relative).read_bytes() != (BASE_WORKSPACE / relative).read_bytes():
            errors.append(f"{relative} changed; this is a test-only task")

    allowed_top_level = {
        ".eval-fixture.json",
        "TASK.md",
        "SPEC.md",
        "pyproject.toml",
        "src",
        "tests",
    }
    for child in candidate.iterdir():
        if child.name not in allowed_top_level and not child.name.startswith("."):
            errors.append(f"unexpected top-level artifact: {child.name}")
    for path in (candidate / "src").iterdir():
        if path.name not in {"__init__.py", "resource_ids.py", "__pycache__"}:
            errors.append(f"unexpected production artifact: src/{path.name}")

    if errors:
        return errors

    baseline_source = (BASE_WORKSPACE / "src" / "resource_ids.py").read_text(
        encoding="utf-8"
    )
    correct_variants = {
        "repository-implementation": baseline_source,
        "independent-regex-implementation": CORRECT_ALTERNATE,
        "independent-manual-implementation": CORRECT_MANUAL,
    }
    for name, source in correct_variants.items():
        passed, output = run_suite(candidate, source)
        if not passed:
            errors.append(
                f"test suite rejected {name}; likely false positive or implementation coupling: {output[-800:]}"
            )

    for name, source in WRONG_VARIANTS.items():
        passed, _ = run_suite(candidate, source)
        if passed:
            errors.append(
                f"test suite did not reject plausible wrong behavior: {name}"
            )
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
    print(
        "PASS: tests accept independent correct implementations and reject all specification violations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
