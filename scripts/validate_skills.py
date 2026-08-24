#!/usr/bin/env python3
"""Dependency-free static validation for this Agent Skills repository."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote


MAX_SKILL_LINES = 500
MAX_DESCRIPTION_CHARS = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class Issue(NamedTuple):
    code: str
    path: Path
    message: str

    def format(self, root: Path) -> str:
        try:
            display = self.path.relative_to(root)
        except ValueError:
            display = self.path
        return f"{display}: [{self.code}] {self.message}"


def parse_bool(value: str) -> bool | None:
    normalized = value.strip().strip('"\'').lower()
    if normalized in {"true", "yes", "on", "1"}:
        return True
    if normalized in {"false", "no", "off", "0"}:
        return False
    return None


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[Issue]]:
    issues: list[Issue] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {}, [Issue("unreadable-file", path, str(exc))]

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, [Issue("missing-frontmatter", path, "SKILL.md must start with YAML frontmatter")]

    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, [Issue("unterminated-frontmatter", path, "frontmatter has no closing ---")]

    values: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            # Nested YAML is not needed by the current frontmatter checks.
            continue
        if ":" not in line:
            issues.append(Issue("invalid-frontmatter-line", path, f"line {line_number} has no ':'"))
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values, issues


def parse_openai_implicit_policy(path: Path) -> tuple[bool | None, list[Issue]]:
    if not path.exists():
        return None, [Issue("missing-openai-metadata", path, "agents/openai.yaml is required")]
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, [Issue("unreadable-file", path, str(exc))]

    match = re.search(r"^\s*allow_implicit_invocation\s*:\s*([^#\n]+)", text, re.MULTILINE)
    if not match:
        return None, [Issue("missing-openai-policy", path, "policy.allow_implicit_invocation is required")]
    value = parse_bool(match.group(1))
    if value is None:
        return None, [Issue("invalid-openai-policy", path, "allow_implicit_invocation must be a boolean")]
    return value, []


def relative_markdown_targets(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []
    targets: list[str] = []
    for match in LINK_RE.finditer(text):
        raw = match.group(1).strip()
        if not raw:
            continue
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1].strip()
        # Markdown titles follow a whitespace separator. Paths in this repository do not contain spaces.
        raw = raw.split(maxsplit=1)[0]
        if raw.startswith(("#", "/")) or "://" in raw or raw.startswith(("mailto:", "data:")):
            continue
        targets.append(unquote(raw.split("#", 1)[0].split("?", 1)[0]))
    return targets


def validate_markdown_links(skill_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    for markdown in sorted(skill_dir.rglob("*.md")):
        for target in relative_markdown_targets(markdown):
            if not target:
                continue
            resolved = (markdown.parent / target).resolve()
            try:
                resolved.relative_to(skill_dir.resolve())
            except ValueError:
                issues.append(
                    Issue("relative-link-escapes-skill", markdown, f"relative link escapes the skill directory: {target}")
                )
                continue
            if not resolved.exists():
                issues.append(Issue("missing-relative-link", markdown, f"linked file does not exist: {target}"))
    return issues


def validate_skill(skill_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [Issue("missing-skill-file", skill_md, "skill directory has no SKILL.md")]

    frontmatter, frontmatter_issues = parse_frontmatter(skill_md)
    issues.extend(frontmatter_issues)

    name = frontmatter.get("name", "")
    if not name:
        issues.append(Issue("missing-name", skill_md, "frontmatter.name is required"))
    elif not NAME_RE.fullmatch(name):
        issues.append(Issue("invalid-name", skill_md, "name must use lowercase kebab-case"))
    elif name != skill_dir.name:
        issues.append(Issue("name-directory-mismatch", skill_md, f"name '{name}' must match directory '{skill_dir.name}'"))

    description = frontmatter.get("description", "")
    if not description:
        issues.append(Issue("missing-description", skill_md, "frontmatter.description is required"))
    elif len(description) > MAX_DESCRIPTION_CHARS:
        issues.append(
            Issue(
                "description-too-long",
                skill_md,
                f"description has {len(description)} characters; maximum is {MAX_DESCRIPTION_CHARS}",
            )
        )

    try:
        line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeError):
        line_count = 0
    if line_count > MAX_SKILL_LINES:
        issues.append(
            Issue(
                "skill-too-long",
                skill_md,
                f"SKILL.md has {line_count} lines; move details into references/ and keep it at or below {MAX_SKILL_LINES}",
            )
        )

    disable_raw = frontmatter.get("disable-model-invocation")
    disable_model = parse_bool(disable_raw) if disable_raw is not None else False
    if disable_model is None:
        issues.append(
            Issue("invalid-claude-policy", skill_md, "disable-model-invocation must be a boolean when present")
        )
    allow_implicit, metadata_issues = parse_openai_implicit_policy(skill_dir / "agents" / "openai.yaml")
    issues.extend(metadata_issues)
    if disable_model is not None and allow_implicit is not None and allow_implicit == disable_model:
        issues.append(
            Issue(
                "invocation-policy-mismatch",
                skill_dir,
                "Claude disable-model-invocation and Codex allow_implicit_invocation disagree",
            )
        )

    issues.extend(validate_markdown_links(skill_dir))
    return issues


def validate_repository(root: Path) -> list[Issue]:
    root = root.resolve()
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return [Issue("missing-skills-directory", skills_root, "repository has no skills/ directory")]

    issues: list[Issue] = []
    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    if not skill_dirs:
        issues.append(Issue("no-skills", skills_root, "no skill directories found"))
        return issues

    for skill_dir in skill_dirs:
        issues.extend(validate_skill(skill_dir))
    return sorted(issues, key=lambda issue: (str(issue.path), issue.code, issue.message))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)

    issues = validate_repository(args.root)
    if issues:
        for issue in issues:
            print(issue.format(args.root.resolve()), file=sys.stderr)
        print(f"validation failed: {len(issues)} issue(s)", file=sys.stderr)
        return 1

    skill_count = sum(1 for path in (args.root / "skills").iterdir() if path.is_dir())
    print(f"validation passed: {skill_count} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
