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
    description: str = "Use for repository validation tests. Do not use for unrelated tasks.",
    compatibility: str | None = None,
    include_metadata: bool = True,
    body: str = "# Test\n\n## Do not use when\n\n- The test does not apply.\n",
    default_prompt: str | None = None,
) -> Path:
    skill = root / "skills" / name
    (skill / "agents").mkdir(parents=True)
    (root / "evals").mkdir(exist_ok=True)
    (root / "evals" / "cases.jsonl").touch()
    compatibility_line = f"compatibility: {compatibility}\n" if compatibility is not None else ""
    metadata = (
        "metadata:\n"
        "  assurance-validation-status: \"candidate\"\n"
        "  assurance-eval-catalog: \"evals/cases.jsonl\"\n"
        if include_metadata
        else ""
    )
    (skill / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"{compatibility_line}"
        f"{metadata}"
        "user-invocable: true\n"
        f"disable-model-invocation: {str(disable_model_invocation).lower()}\n"
        "---\n\n"
        f"{body.rstrip()}\n",
        encoding="utf-8",
    )
    prompt = default_prompt or f"Use ${name}."
    (skill / "agents" / "openai.yaml").write_text(
        textwrap.dedent(
            f"""\
            interface:
              display_name: "Test"
              short_description: "Test skill"
              default_prompt: "{prompt}"

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
            write_skill(root, "manual-skill", disable_model_invocation=True, allow_implicit_invocation=True)
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "invocation-policy-mismatch" for issue in issues), issues)

    def test_rejects_skill_body_over_500_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = "# Test\n\n## Do not use when\n\n- Never.\n" + "instruction\n" * 501
            write_skill(root, "large-skill", disable_model_invocation=False, allow_implicit_invocation=True, body=body)
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
                body="# Test\n\n## Do not use when\n\n- Never.\n\nRead [details](references/missing.md).\n",
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "missing-relative-link" for issue in issues), issues)

    def test_rejects_missing_anti_applicability_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "missing-anti",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                body="# Test\nNo anti-trigger section.\n",
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "missing-anti-applicability-section" for issue in issues), issues)

    def test_rejects_description_without_negative_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "broad-skill",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                description="Use whenever coding.",
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "description-missing-negative-trigger" for issue in issues), issues)

    def test_rejects_missing_assurance_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "missing-metadata",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                include_metadata=False,
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "missing-assurance-metadata" for issue in issues), issues)

    def test_rejects_name_and_compatibility_over_spec_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = "a" * 65
            write_skill(
                root,
                name,
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                compatibility="x" * 501,
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "name-too-long" for issue in issues), issues)
            self.assertTrue(any(issue.code == "invalid-compatibility" for issue in issues), issues)

    def test_rejects_openai_prompt_that_does_not_name_the_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "prompt-skill",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                default_prompt="Use the workflow.",
            )
            issues = self.validator.validate_repository(root)
            self.assertTrue(any(issue.code == "openai-default-prompt-missing-skill" for issue in issues), issues)


    def test_rejects_invalid_assurance_status_and_missing_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = write_skill(
                root,
                "bad-provenance",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
            )
            skill_md = skill / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            text = text.replace(
                'assurance-validation-status: "candidate"',
                'assurance-validation-status: "proven"',
            ).replace(
                'assurance-eval-catalog: "evals/cases.jsonl"',
                'assurance-eval-catalog: "evals/missing.jsonl"',
            )
            skill_md.write_text(text, encoding="utf-8")
            issues = self.validator.validate_repository(root)
            self.assertTrue(
                any(issue.code == "invalid-assurance-status" for issue in issues),
                issues,
            )
            self.assertTrue(
                any(issue.code == "missing-assurance-catalog" for issue in issues),
                issues,
            )

    def test_requires_explicit_claude_invocation_booleans(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = write_skill(
                root,
                "missing-policy",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
            )
            skill_md = skill / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            text = text.replace("user-invocable: true\n", "")
            text = text.replace("disable-model-invocation: false\n", "")
            skill_md.write_text(text, encoding="utf-8")
            issues = self.validator.validate_repository(root)
            invalid = [issue for issue in issues if issue.code == "invalid-claude-policy"]
            self.assertEqual(2, len(invalid), issues)

    def test_accepts_a_small_aligned_skill_with_existing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = write_skill(
                root,
                "good-skill",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                body="# Test\n\n## Do not use when\n\n- Never.\n\nRead [details](references/details.md).\n",
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

    def test_repository_text_files_have_no_trailing_whitespace(self) -> None:
        text_suffixes = {".diff", ".json", ".jsonl", ".md", ".py", ".toml", ".yaml", ".yml"}
        text_names = {".gitignore", "LICENSE"}
        ignored_parts = {".git", ".jj", ".claude", ".eval-results", "__pycache__"}
        for file_path in REPO_ROOT.rglob("*"):
            if not file_path.is_file() or any(part in ignored_parts for part in file_path.parts):
                continue
            if file_path.suffix not in text_suffixes and file_path.name not in text_names:
                continue
            for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), 1):
                self.assertEqual(
                    line.rstrip(" \t"),
                    line,
                    f"trailing whitespace at {file_path.relative_to(REPO_ROOT)}:{line_number}",
                )

    def test_repository_has_the_deliberate_ten_skill_architecture(self) -> None:
        expected = {
            "change-contract",
            "cross-agent",
            "grounded-implementation",
            "jujutsu",
            "profile-guided-optimization",
            "precision-review",
            "reproduction-first-debugging",
            "simplify-after-green",
            "simplify-tests-after-green",
            "specification-grounded-testing",
        }
        actual = {path.name for path in (REPO_ROOT / "skills").iterdir() if path.is_dir()}
        self.assertEqual(expected, actual)

    def test_all_skills_have_explicit_anti_triggers_and_candidate_metadata(self) -> None:
        for skill_dir in (REPO_ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            self.assertIn("Do not use", frontmatter, skill_dir.name)
            self.assertIn("assurance-validation-status", frontmatter, skill_dir.name)
            self.assertIn("assurance-eval-catalog", frontmatter, skill_dir.name)
            self.assertIn("## Do not use when", text, skill_dir.name)

    def test_manual_cross_agent_composition_is_explicit(self) -> None:
        for relative in (
            "skills/change-contract/SKILL.md",
            "skills/simplify-after-green/SKILL.md",
        ):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            # Examples must support both hosts; prose and Markdown styling can vary.
            self.assertIn("$cross-agent $", text)
            self.assertIn("/cross-agent /", text)
        frontmatter, issues = self.validator.parse_frontmatter(REPO_ROOT / "skills/cross-agent/SKILL.md")
        self.assertEqual([], issues)
        self.assertTrue(self.validator.parse_bool(frontmatter["disable-model-invocation"]))

    def test_readme_describes_the_actual_invocation_policy(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        rows = {
            cells[0].strip("`"): cells[1:]
            for line in readme.splitlines()
            if line.startswith("|")
            and len(cells := [cell.strip() for cell in line.strip("|").split("|")]) == 3
        }
        for skill in (
            "grounded-implementation",
            "profile-guided-optimization",
            "precision-review",
            "reproduction-first-debugging",
            "specification-grounded-testing",
            "jujutsu",
        ):
            self.assertEqual(["Automatic or explicit", "Automatic or explicit"], rows[skill])
        for skill in ("change-contract", "cross-agent", "simplify-after-green", "simplify-tests-after-green"):
            self.assertEqual(["Explicit only", "Explicit only"], rows[skill])
        self.assertIn("select at most one\nprimary task-family skill", readme)

    def test_grounded_implementation_has_local_truth_and_completion_gates(self) -> None:
        text = (REPO_ROOT / "skills" / "grounded-implementation" / "SKILL.md").read_text(encoding="utf-8").lower()
        for marker in (
            "fix the behavioral basis",
            "build a compact local-truth map",
            "version-dependent api or behavior",
            "the implementation does not redefine it",
            "run the completion gate",
            "success requires observable evidence",
            "stop, inspect the newly affected boundary",
        ):
            self.assertIn(marker, text)

    def test_debugging_forces_reproduction_hypothesis_invalidation_and_original_rerun(self) -> None:
        text = (REPO_ROOT / "skills" / "reproduction-first-debugging" / "SKILL.md").read_text(encoding="utf-8").lower()
        for marker in (
            "reproduce before modifying",
            "form competing hypotheses",
            "falsified by",
            "change one causal variable at a time",
            "if two production patches fail",
            "the original reproduction with the same relevant environment and input",
        ):
            self.assertIn(marker, text)

    def test_precision_review_requires_mechanism_trigger_evidence_and_suppression(self) -> None:
        text = (REPO_ROOT / "skills" / "precision-review" / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "Fix the target and intent",
            "Build the affected-evidence map",
            "Mechanism:",
            "Trigger:",
            "Falsifier:",
            "Do not report:",
            "A valid no-findings result",
        ):
            self.assertIn(marker, text)

    def test_specification_grounded_testing_requires_an_independent_oracle(self) -> None:
        text = (
            REPO_ROOT / "skills" / "specification-grounded-testing" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Freeze the behavioral oracle",
            "Plausible wrong behavior",
            "Validate the oracle independently",
            "known-valid",
            "defect-exposed",
            "Production code remains unchanged",
        ):
            self.assertIn(marker, text)

    def test_profile_guided_optimization_requires_measurement_and_reversion(self) -> None:
        text = (
            REPO_ROOT / "skills" / "profile-guided-optimization" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Define the performance contract",
            "Profile before optimizing",
            "Form one falsifiable bottleneck hypothesis",
            "Measure, compare, and keep or revert",
            "If two consecutive candidates",
            "A valid result may be",
        ):
            self.assertIn(marker, text)

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

if __name__ == "__main__":
    unittest.main()
