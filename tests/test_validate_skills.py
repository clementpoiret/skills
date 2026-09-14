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
              short_description: "Validate a focused test skill"
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

    def test_accepts_body_without_a_repeated_routing_section(self) -> None:
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
            self.assertEqual([], issues)

    def test_accepts_precise_description_without_magic_trigger_words(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "broad-skill",
                disable_model_invocation=False,
                allow_implicit_invocation=True,
                description="Normalize a repository release manifest before publishing.",
            )
            issues = self.validator.validate_repository(root)
            self.assertEqual([], issues)

    def test_accepts_absent_model_evaluation_metadata(self) -> None:
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
            self.assertEqual([], issues)

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

    def test_accepts_codex_metadata_without_claude_fields(self) -> None:
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
            self.assertEqual([], invalid)

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
        self.assertEqual([], self.validator.validate_repository(REPO_ROOT))

    def test_names_and_codex_invocation_policies_are_preserved(self) -> None:
        expected = {
            "change-contract": False,
            "cross-agent": False,
            "grounded-implementation": True,
            "jujutsu": True,
            "precision-review": True,
            "profile-guided-optimization": True,
            "reproduction-first-debugging": True,
            "simplify-after-green": False,
            "simplify-tests-after-green": False,
            "specification-grounded-testing": True,
        }
        actual = {}
        for skill in (REPO_ROOT / "skills").iterdir():
            if not skill.is_dir():
                continue
            metadata, issues = self.validator.parse_openai_metadata(skill / "agents" / "openai.yaml")
            self.assertEqual([], issues)
            actual[skill.name] = metadata["allow_implicit_invocation"]
        self.assertEqual(expected, actual)

    def test_canonical_skills_have_minimal_frontmatter_and_local_brevity_budget(self) -> None:
        # These are this library's budgets, not universal OpenAI format limits.
        for path in (REPO_ROOT / "skills").glob("*/SKILL.md"):
            metadata, issues = self.validator.parse_frontmatter(path)
            self.assertEqual([], issues)
            self.assertEqual({"name", "description"}, set(metadata), path)
            self.assertLessEqual(len(metadata["description"]), 250, path)
            self.assertLessEqual(len(path.read_text().split()), 650, path)

    def test_every_reference_is_routed_from_its_skill_root(self) -> None:
        for skill in (REPO_ROOT / "skills").iterdir():
            if not skill.is_dir():
                continue
            linked = set(self.validator.relative_markdown_targets(skill / "SKILL.md"))
            for reference in (skill / "references").glob("*.md"):
                self.assertIn(reference.relative_to(skill).as_posix(), linked, reference)

    def test_repository_text_files_have_no_trailing_whitespace(self) -> None:
        suffixes = {".diff", ".json", ".jsonl", ".md", ".py", ".toml", ".yaml", ".yml"}
        for path in REPO_ROOT.rglob("*"):
            if not path.is_file() or any(part in {".git", ".jj", "__pycache__", ".eval-results"} for part in path.parts):
                continue
            if path.suffix not in suffixes and path.name not in {".gitignore", "LICENSE"}:
                continue
            for number, line in enumerate(path.read_text().splitlines(), 1):
                self.assertEqual(line.rstrip(" \t"), line, f"{path}:{number}")


class AdditionalSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()

    def test_rejects_both_short_description_length_extremes(self) -> None:
        for text in ("Too short", "x" * 65):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                skill = write_skill(root, "length-skill", disable_model_invocation=False, allow_implicit_invocation=True)
                metadata = skill / "agents" / "openai.yaml"
                metadata.write_text(metadata.read_text().replace("Validate a focused test skill", text))
                codes = {i.code for i in self.validator.validate_repository(root)}
                self.assertIn("invalid-openai-short-description-length", codes)

    def test_rejects_empty_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "empty-skill", disable_model_invocation=False, allow_implicit_invocation=True, body="")
            self.assertIn("empty-skill-body", {i.code for i in self.validator.validate_repository(root)})

    def test_rejects_reference_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "escape-skill", disable_model_invocation=False, allow_implicit_invocation=True,
                        body="Read [outside](../../outside.md).")
            (root / "outside.md").write_text("not a skill resource")
            self.assertIn("relative-link-escapes-skill", {i.code for i in self.validator.validate_repository(root)})

    def test_rejects_duplicate_frontmatter_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = write_skill(root, "duplicate-skill", disable_model_invocation=False, allow_implicit_invocation=True)
            path = skill / "SKILL.md"
            path.write_text(path.read_text().replace("name: duplicate-skill", "name: duplicate-skill\nname: duplicate-skill"))
            self.assertIn("duplicate-frontmatter-key", {i.code for i in self.validator.validate_repository(root)})


if __name__ == "__main__":
    unittest.main()
