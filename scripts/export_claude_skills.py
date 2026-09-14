#!/usr/bin/env python3
"""Export a separate Claude-compatible copy; never edit or install canonical skills."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from validate_skills import parse_openai_metadata, validate_repository


def export_skills(root: Path, destination: Path) -> int:
    root = root.resolve()
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"destination already exists: {destination}")
    if destination.resolve().is_relative_to(root):
        raise ValueError("destination must be outside the source repository")
    issues = validate_repository(root)
    if issues:
        raise ValueError("invalid source repository: " + "; ".join(i.format(root) for i in issues))
    source = root / "skills"
    if any(path.is_symlink() for path in source.rglob("*")):
        raise ValueError("export requires regular source files, not symlinks")

    plan: list[tuple[Path, str]] = []
    for skill in sorted(p for p in source.iterdir() if p.is_dir()):
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        header, body = text[4:].split("\n---\n", 1)
        if "disable-model-invocation:" in header or "user-invocable:" in header:
            raise ValueError("source must be the canonical Codex copy, not an earlier export")
        metadata, _ = parse_openai_metadata(skill / "agents" / "openai.yaml")
        disabled = not metadata["allow_implicit_invocation"]
        rendered = (
            "---\n" + header + "\nuser-invocable: true\n"
            f"disable-model-invocation: {str(disabled).lower()}\n---\n" + body
        )
        plan.append((skill, rendered))

    destination.mkdir(parents=True, exist_ok=False)
    try:
        for skill, rendered in plan:
            target = destination / skill.name
            shutil.copytree(skill, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            (target / "SKILL.md").write_text(rendered, encoding="utf-8")
    except Exception:
        # Only remove the fresh output created by this invocation.
        shutil.rmtree(destination)
        raise
    return len(plan)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new directory outside the source repository")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        count = export_skills(args.root, args.destination)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"export failed: {exc}\n")
    print(f"exported {count} skill(s) to {args.destination}; nothing installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
