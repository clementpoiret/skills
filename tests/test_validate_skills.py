from __future__ import annotations

import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_skills.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skills", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_skill(
    root: Path,
    name: str,
    *,
    disable_model_invocation: bool,
    allow_implicit_invocation: bool,
    body: str = "# Test\n",
) -> Path:
    skill = root / "skills" / name
    (skill / "agents").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: Test skill for repository validation.\n"
        "user-invocable: true\n"
        f"disable-model-invocation: {str(disable_model_invocation).lower()}\n"
        "---\n\n"
        f"{body.rstrip()}\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text(
        textwrap.dedent(
            f"""\
            interface:
              display_name: "Test"
              short_description: "Test"
              default_prompt: "Use ${name}."

            policy:
              allow_implicit_invocation: {str(allow_implicit_invocation).lower()}
            """
        ),
        encoding="utf-8",
    )
    return skill


class ValidatorUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()

    def test_rejects_cross_host_invocation_policy_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "manual-skill",
                disable_model_invocation=True,
                allow_implicit_invocation=True,
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "invocation-policy-mismatch" for issue in issues), issues)

    def test_rejects_skill_body_over_500_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = "# Test\n" + "instruction\n" * 501
            write_skill(
                root,
                "large-skill",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                body=body,
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "skill-too-long" for issue in issues), issues)

    def test_rejects_missing_relative_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "broken-link",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                body="# Test\nRead [details](references/missing.md).\n",
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "missing-relative-link" for issue in issues), issues)

    def test_accepts_a_small_aligned_skill_with_existing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = write_skill(
                root,
                "good-skill",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                body="# Test\nRead [details](references/details.md).\n",
            )
            (skill / "references").mkdir()
            (skill / "references" / "details.md").write_text("# Details\n", encoding="utf-8")
            issues = self.validator.validate_repository(root)
            self.assertEqual([], issues)


class RepositoryRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()

    def test_repository_passes_static_validation(self) -> None:
        issues = self.validator.validate_repository(REPO_ROOT)
        self.assertEqual([], issues)

    def test_manual_cross_agent_composition_is_explicit(self) -> None:
        for relative in (
            "skills/change-contract/SKILL.md",
            "skills/simplify-after-green/SKILL.md",
        ):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("does not invoke `cross-agent` itself", text)
            self.assertIn("`$cross-agent`", text)
            self.assertIn("`/cross-agent`", text)

    def test_readme_describes_the_actual_invocation_policy(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("| `change-contract` | Explicit only | Explicit only |", readme)
        self.assertIn("| `cross-agent` | Explicit only | Explicit only |", readme)
        self.assertIn("| `simplify-after-green` | Explicit only | Explicit only |", readme)
        self.assertIn("| `simplify-tests-after-green` | Explicit only | Explicit only |", readme)
        self.assertIn("| `jujutsu` | Automatic or explicit | Automatic or explicit |", readme)

    def test_jujutsu_uses_progressive_disclosure(self) -> None:
        skill = REPO_ROOT / "skills" / "jujutsu" / "SKILL.md"
        self.assertLessEqual(len(skill.read_text(encoding="utf-8").splitlines()), 500)
        references = skill.parent / "references"
        expected = {
            "bookmarks-remotes-tags.md",
            "configuration-and-run.md",
            "conflicts-and-recovery.md",
            "descriptions.md",
            "history-and-rewrites.md",
            "version-compatibility.md",
            "workspaces.md",
        }
        self.assertEqual(expected, {path.name for path in references.glob("*.md")})

    def test_jujutsu_does_not_impose_conventional_commits_globally(self) -> None:
        frontmatter = (REPO_ROOT / "skills" / "jujutsu" / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        self.assertNotIn("Requires Conventional Commits", frontmatter)
        text = (REPO_ROOT / "skills" / "jujutsu" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Follow the repository's revision-description policy", text)
        self.assertIn("It is not a\nsandbox and does not deny other tools", text)

    def test_cross_agent_is_capability_aware_and_has_a_bounded_retry_rule(self) -> None:
        skill = REPO_ROOT / "skills" / "cross-agent"
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Preflight before starting peer inference", text)
        self.assertIn("at most one corrected retry", text)
        self.assertIn("do not retry automatically", text)
        references = {path.name for path in (skill / "references").glob("*.md")}
        self.assertEqual(
            {"bounded-edit.md", "claude-peer.md", "codex-peer.md", "failure-state-machine.md"},
            references,
        )
        for reference in references:
            self.assertIn(f"references/{reference}", text)

    def test_production_simplification_has_risk_and_search_budgets(self) -> None:
        text = (REPO_ROOT / "skills" / "simplify-after-green" / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"For\s+`R2` or `R3`, require an explicit accepted contract")
        self.assertIn("inspect no more than three plausible candidates", text)
        self.assertIn("choose at most one conceptual removal", text)

    def test_test_simplification_has_safe_discriminators_and_budgets(self) -> None:
        text = (REPO_ROOT / "skills" / "simplify-tests-after-green" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("use at most three narrowly scoped mutants", text)
        self.assertIn("a temporary mutation in an isolated workspace or temporary copy", text)
        self.assertIn("an inline inverse-edit mutation only when", text)
        self.assertIn("retain the test rather than exhaust the budget", text)


if __name__ == "__main__":
    unittest.main()
