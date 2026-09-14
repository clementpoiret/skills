#!/usr/bin/env python3
"""Dependency-free structural validation for this Agent Skills repository."""

from __future__ import annotations

import argparse
import re
import stat
import sys
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote


MAX_SKILL_LINES = 500
MAX_NAME_CHARS = 64
MAX_DESCRIPTION_CHARS = 1024
MAX_COMPATIBILITY_CHARS = 500
# Local description-only budget; not the host's full skill-list/context budget.
MAX_INITIAL_DESCRIPTION_CHARS = 8000
MIN_OPENAI_SHORT_DESCRIPTION_CHARS = 25
MAX_OPENAI_SHORT_DESCRIPTION_CHARS = 64
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
VALIDATION_STATUSES = {"unvalidated-candidate", "candidate", "validated"}


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


def _read_skill_parts(path: Path) -> tuple[list[str], int | None, list[Issue]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [], None, [Issue("unreadable-file", path, str(exc))]

    if not lines or lines[0].strip() != "---":
        return lines, None, [Issue("missing-frontmatter", path, "SKILL.md must start with YAML frontmatter")]

    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return lines, None, [Issue("unterminated-frontmatter", path, "frontmatter has no closing ---")]
    return lines, end, []


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[Issue]]:
    lines, end, issues = _read_skill_parts(path)
    if end is None:
        return {}, issues

    values: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            # Nested maps are validated separately where this repository relies on them.
            continue
        if ":" not in line:
            issues.append(Issue("invalid-frontmatter-line", path, f"line {line_number} has no ':'"))
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in values:
            issues.append(Issue("duplicate-frontmatter-key", path, f"duplicate key: {key}"))
        values[key] = value.strip().strip('"\'')
    return values, issues


def parse_metadata(path: Path) -> tuple[dict[str, str], list[Issue]]:
    lines, end, issues = _read_skill_parts(path)
    if end is None:
        return {}, issues

    metadata: dict[str, str] = {}
    metadata_index: int | None = None
    for index, line in enumerate(lines[1:end], start=1):
        if line.strip() == "metadata:":
            metadata_index = index
            break
    if metadata_index is None:
        return {}, issues

    for line_number, line in enumerate(lines[metadata_index + 1 : end], start=metadata_index + 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            break
        stripped = line.strip()
        if ":" not in stripped:
            issues.append(Issue("invalid-metadata-line", path, f"line {line_number} has no ':'"))
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"\'')
        if not key or not value:
            issues.append(Issue("invalid-metadata-value", path, f"line {line_number} must map a key to a string"))
            continue
        metadata[key] = value
    return metadata, issues


def skill_body(path: Path) -> str:
    lines, end, _ = _read_skill_parts(path)
    if end is None:
        return ""
    return "\n".join(lines[end + 1 :])


def parse_openai_metadata(path: Path) -> tuple[dict[str, str | bool], list[Issue]]:
    if not path.exists():
        return {}, [Issue("missing-openai-metadata", path, "agents/openai.yaml is required")]
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {}, [Issue("unreadable-file", path, str(exc))]

    issues: list[Issue] = []
    values: dict[str, str | bool] = {}
    for field in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf"^\s*{re.escape(field)}\s*:\s*([^#\n]+)", text, re.MULTILINE)
        if not match:
            issues.append(Issue("missing-openai-interface", path, f"interface.{field} is required"))
            continue
        values[field] = match.group(1).strip().strip('"\'')

    match = re.search(r"^\s*allow_implicit_invocation\s*:\s*([^#\n]+)", text, re.MULTILINE)
    if not match:
        issues.append(Issue("missing-openai-policy", path, "policy.allow_implicit_invocation is required"))
    else:
        value = parse_bool(match.group(1))
        if value is None:
            issues.append(Issue("invalid-openai-policy", path, "allow_implicit_invocation must be a boolean"))
        else:
            values["allow_implicit_invocation"] = value
    return values, issues


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
                    Issue(
                        "relative-link-escapes-skill",
                        markdown,
                        f"relative link escapes the skill directory: {target}",
                    )
                )
                continue
            if not resolved.exists():
                issues.append(Issue("missing-relative-link", markdown, f"linked file does not exist: {target}"))
    return issues


def validate_skill_scripts(skill_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.exists():
        return issues
    for path in sorted(scripts_dir.rglob("*")):
        if path.is_symlink():
            issues.append(Issue("symlinked-skill-script", path, "skill scripts must be auditable regular files"))
        elif path.is_file() and not (path.stat().st_mode & stat.S_IXUSR):
            issues.append(Issue("nonexecutable-skill-script", path, "skill scripts must be executable by the owner"))
    return issues


def validate_skill(skill_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [Issue("missing-skill-file", skill_md, "skill directory has no SKILL.md")]

    frontmatter, frontmatter_issues = parse_frontmatter(skill_md)
    issues.extend(frontmatter_issues)
    metadata, metadata_issues = parse_metadata(skill_md)
    issues.extend(metadata_issues)

    name = frontmatter.get("name", "")
    if not name:
        issues.append(Issue("missing-name", skill_md, "frontmatter.name is required"))
    elif len(name) > MAX_NAME_CHARS:
        issues.append(
            Issue(
                "name-too-long",
                skill_md,
                f"name has {len(name)} characters; maximum is {MAX_NAME_CHARS}",
            )
        )
    elif not NAME_RE.fullmatch(name):
        issues.append(
            Issue(
                "invalid-name",
                skill_md,
                "name must use lowercase kebab-case without consecutive hyphens",
            )
        )
    elif name != skill_dir.name:
        issues.append(
            Issue(
                "name-directory-mismatch",
                skill_md,
                f"name '{name}' must match directory '{skill_dir.name}'",
            )
        )

    description = frontmatter.get("description", "")
    if not description:
        issues.append(Issue("missing-description", skill_md, "frontmatter.description is required"))
    else:
        if len(description) > MAX_DESCRIPTION_CHARS:
            issues.append(
                Issue(
                    "description-too-long",
                    skill_md,
                    f"description has {len(description)} characters; maximum is {MAX_DESCRIPTION_CHARS}",
                )
            )
        if "<" in description or ">" in description:
            issues.append(Issue("invalid-description", skill_md, "description must not contain angle brackets"))

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None and (not compatibility or len(compatibility) > MAX_COMPATIBILITY_CHARS):
        issues.append(
            Issue(
                "invalid-compatibility",
                skill_md,
                f"compatibility must contain 1-{MAX_COMPATIBILITY_CHARS} characters when present",
            )
        )

    # Legacy provenance is checked when present, not required in model-visible metadata.
    status = metadata.get("assurance-validation-status")
    if status is not None and status not in VALIDATION_STATUSES:
        issues.append(
            Issue(
                "invalid-assurance-status",
                skill_md,
                f"assurance-validation-status must be one of {sorted(VALIDATION_STATUSES)}",
            )
        )
    catalog = metadata.get("assurance-eval-catalog")
    if catalog is not None:
        catalog_path = Path(catalog)
        repository_root = skill_dir.parents[1].resolve()
        if catalog_path.is_absolute():
            issues.append(
                Issue(
                    "invalid-assurance-catalog",
                    skill_md,
                    "assurance-eval-catalog must be a repository-relative path",
                )
            )
        else:
            resolved_catalog = (repository_root / catalog_path).resolve()
            try:
                resolved_catalog.relative_to(repository_root)
            except ValueError:
                issues.append(
                    Issue(
                        "invalid-assurance-catalog",
                        skill_md,
                        "assurance-eval-catalog escapes the repository",
                    )
                )
            else:
                if not resolved_catalog.is_file():
                    issues.append(
                        Issue(
                            "missing-assurance-catalog",
                            skill_md,
                            f"assurance eval catalog does not exist: {catalog}",
                        )
                    )

    body = skill_body(skill_md)
    if not body.strip():
        issues.append(Issue("empty-skill-body", skill_md, "skill instructions must not be empty"))

    try:
        line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeError):
        line_count = 0
    if line_count > MAX_SKILL_LINES:
        issues.append(
            Issue(
                "skill-too-long",
                skill_md,
                f"SKILL.md has {line_count} lines; move details into references/ "
                f"and keep it at or below {MAX_SKILL_LINES}",
            )
        )

    user_invocable_raw = frontmatter.get("user-invocable")
    user_invocable = (
        parse_bool(user_invocable_raw) if user_invocable_raw is not None else None
    )
    if user_invocable_raw is not None and user_invocable is None:
        issues.append(
            Issue(
                "invalid-claude-policy",
                skill_md,
                "user-invocable must be an explicit boolean",
            )
        )

    disable_raw = frontmatter.get("disable-model-invocation")
    disable_model = parse_bool(disable_raw) if disable_raw is not None else None
    if disable_raw is not None and disable_model is None:
        issues.append(
            Issue(
                "invalid-claude-policy",
                skill_md,
                "disable-model-invocation must be an explicit boolean",
            )
        )

    openai_path = skill_dir / "agents" / "openai.yaml"
    openai, openai_issues = parse_openai_metadata(openai_path)
    issues.extend(openai_issues)
    allow_implicit = openai.get("allow_implicit_invocation")
    if disable_model is not None and isinstance(allow_implicit, bool) and allow_implicit == disable_model:
        issues.append(
            Issue(
                "invocation-policy-mismatch",
                skill_dir,
                "Claude disable-model-invocation and Codex allow_implicit_invocation disagree",
            )
        )

    short_description = openai.get("short_description")
    if isinstance(short_description, str) and not (
        MIN_OPENAI_SHORT_DESCRIPTION_CHARS <= len(short_description) <= MAX_OPENAI_SHORT_DESCRIPTION_CHARS
    ):
        issues.append(
            Issue(
                "invalid-openai-short-description-length",
                openai_path,
                f"short_description has {len(short_description)} characters; "
                f"expected {MIN_OPENAI_SHORT_DESCRIPTION_CHARS}-{MAX_OPENAI_SHORT_DESCRIPTION_CHARS}",
            )
        )
    default_prompt = openai.get("default_prompt")
    if name and isinstance(default_prompt, str) and f"${name}" not in default_prompt:
        issues.append(
            Issue(
                "openai-default-prompt-missing-skill",
                openai_path,
                f"default_prompt must explicitly mention ${name}",
            )
        )

    issues.extend(validate_markdown_links(skill_dir))
    issues.extend(validate_skill_scripts(skill_dir))
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

    description_total = 0
    for skill_dir in skill_dirs:
        issues.extend(validate_skill(skill_dir))
        frontmatter, _ = parse_frontmatter(skill_dir / "SKILL.md")
        description_total += len(frontmatter.get("description", ""))
    if description_total > MAX_INITIAL_DESCRIPTION_CHARS:
        issues.append(
            Issue(
                "initial-description-budget-exceeded",
                skills_root,
                f"skill descriptions total {description_total} characters; budget is {MAX_INITIAL_DESCRIPTION_CHARS}",
            )
        )
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
