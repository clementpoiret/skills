from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "eval_results.py"


def load_module():
    spec = importlib.util.spec_from_file_location("eval_results", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def result_record(**overrides):
    record = {
        "case_id": "jj-status-implicit",
        "skill": "jujutsu",
        "host": "codex",
        "model": "model",
        "arm": "skill",
        "trial": 1,
        "available": True,
        "selected": True,
        "selected_skill": "jujutsu",
        "accessed": True,
        "procedure_adherent": True,
        "verifier_passed": True,
        "success": True,
        "failure_category": None,
        "input_tokens": 100,
        "output_tokens": 50,
        "skill_tokens": 20,
        "tool_calls": 3,
        "test_invocations": 1,
        "trajectory_turns": 2,
        "wall_seconds": 1.2,
        "notes": "",
    }
    record.update(overrides)
    return record


class EvalResultsUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_case_validation_rejects_duplicate_ids(self) -> None:
        records = [
            {
                "id": "duplicate",
                "skill": "jujutsu",
                "kind": "trigger",
                "prompt": "Show status.",
                "expected_invocation": "implicit",
                "expected": ["uses jj"],
            },
            {
                "id": "duplicate",
                "skill": "jujutsu",
                "kind": "near-miss",
                "prompt": "Explain the word jujutsu.",
                "expected_invocation": "none",
                "expected": ["does not invoke the skill"],
            },
        ]
        errors = self.module.validate_cases(records)
        self.assertTrue(any("duplicate case id" in error for error in errors), errors)

    def test_confusable_case_requires_a_known_neighbor(self) -> None:
        record = {
            "id": "confusable",
            "skill": "precision-review",
            "kind": "confusable",
            "prompt": "Review this.",
            "expected_invocation": "implicit",
            "expected": ["routes correctly"],
        }
        errors = self.module.validate_cases([record])
        self.assertTrue(any("confusable cases require confusable_with" in error for error in errors), errors)

    def test_result_validation_requires_adherence_verifier_and_resource_fields(self) -> None:
        self.assertEqual([], self.module.validate_result(result_record()))
        incomplete = result_record()
        incomplete.pop("procedure_adherent")
        errors = self.module.validate_result(incomplete)
        self.assertTrue(any("procedure_adherent" in error for error in errors), errors)

    def test_wrong_skill_arm_requires_a_different_selected_skill(self) -> None:
        invalid = result_record(
            arm="wrong-skill",
            available=False,
            selected=False,
            accessed=False,
            selected_skill="jujutsu",
        )
        errors = self.module.validate_result(invalid)
        self.assertTrue(any("different selected_skill" in error for error in errors), errors)

        valid = result_record(
            skill="precision-review",
            arm="wrong-skill",
            available=False,
            selected=False,
            accessed=False,
            selected_skill="change-contract",
            procedure_adherent=False,
            verifier_passed=False,
            success=False,
            failure_category="wrong-skill",
        )
        self.assertEqual([], self.module.validate_result(valid))

    def test_no_skill_arm_cannot_access_or_consume_skill_tokens(self) -> None:
        invalid = result_record(
            arm="no-skill",
            available=False,
            selected=False,
            selected_skill=None,
            accessed=True,
            skill_tokens=10,
        )
        errors = self.module.validate_result(invalid)
        self.assertTrue(any("cannot access" in error for error in errors), errors)
        self.assertTrue(any("zero or null skill_tokens" in error for error in errors), errors)

    def test_summary_keeps_metrics_separate_and_uses_only_matched_pairs(self) -> None:
        baseline = {
            "arm": "no-skill",
            "available": False,
            "selected": False,
            "selected_skill": None,
            "accessed": False,
            "procedure_adherent": False,
            "verifier_passed": False,
            "success": False,
            "failure_category": "algorithmic",
            "skill_tokens": 0,
            "output_tokens": 40,
            "tool_calls": 2,
            "test_invocations": 0,
            "trajectory_turns": 1,
            "wall_seconds": 1.0,
        }
        records = [
            result_record(trial=1, input_tokens=80, **baseline),
            result_record(trial=2, input_tokens=90, **baseline),
            result_record(trial=1),
            result_record(
                trial=2,
                selected=True,
                accessed=False,
                procedure_adherent=False,
                verifier_passed=False,
                success=False,
                failure_category="skill-ignored",
            ),
            result_record(
                trial=3,
                selected=False,
                selected_skill=None,
                accessed=False,
                procedure_adherent=True,
                verifier_passed=True,
                success=True,
            ),
        ]
        summary = self.module.summarize(records)
        self.assertEqual(2, len(summary))
        skill_row = next(row for row in summary if row["arm"] == "skill")
        self.assertEqual(3, skill_row["trials"])
        self.assertAlmostEqual(2 / 3, skill_row["selection_rate"])
        self.assertAlmostEqual(1 / 3, skill_row["access_rate"])
        self.assertAlmostEqual(2 / 3, skill_row["procedure_adherence_rate"])
        self.assertAlmostEqual(2 / 3, skill_row["verifier_pass_rate"])
        self.assertAlmostEqual(2 / 3, skill_row["success_rate"])
        self.assertEqual(2, skill_row["matched_pairs_vs_no_skill"])
        self.assertAlmostEqual(0.5, skill_row["paired_delta_success_vs_no_skill"])
        self.assertAlmostEqual(0.5, skill_row["paired_delta_adherence_vs_no_skill"])
        self.assertAlmostEqual(15.0, skill_row["paired_delta_input_tokens_vs_no_skill"])
        self.assertEqual(300, skill_row["input_tokens"])
        self.assertEqual(150, skill_row["output_tokens"])
        self.assertAlmostEqual(100.0, skill_row["mean_input_tokens"])


    def test_catalog_linkage_rejects_unknown_case_skill_mismatch_and_wrong_neighbor(self) -> None:
        cases = self.module.load_case_index()
        errors = self.module.validate_results(
            [result_record(case_id="missing-case")],
            cases=cases,
        )
        self.assertTrue(any("unknown case_id" in error for error in errors), errors)

        errors = self.module.validate_results(
            [result_record(case_id="pr-diff-trigger")],
            cases=cases,
        )
        self.assertTrue(any("does not match case skill" in error for error in errors), errors)

        wrong = result_record(
            case_id="pr-contract-audit-confusable",
            skill="precision-review",
            arm="wrong-skill",
            available=False,
            selected=False,
            accessed=False,
            selected_skill="reproduction-first-debugging",
            procedure_adherent=False,
            verifier_passed=False,
            success=False,
            failure_category="wrong-skill",
        )
        errors = self.module.validate_results([wrong], cases=cases)
        self.assertTrue(any("confusable skills" in error for error in errors), errors)

    def test_success_requires_observed_verifier_pass(self) -> None:
        errors = self.module.validate_result(
            result_record(verifier_passed=None, success=True)
        )
        self.assertTrue(any("requires an independently observed verifier pass" in error for error in errors), errors)

    def test_repository_case_catalog_is_valid_and_covers_new_skills(self) -> None:
        records = self.module.read_jsonl(REPO_ROOT / "evals" / "cases.jsonl")
        self.assertGreaterEqual(len(records), 90)
        self.assertEqual([], self.module.validate_cases(records))
        self.assertEqual(self.module.SKILLS, {record["skill"] for record in records})
        required_kinds = {
            "trigger",
            "near-miss",
            "confusable",
            "procedure",
            "failure",
            "escape",
            "counterfactual",
        }
        self.assertTrue(
            required_kinds <= {record["kind"] for record in records}
        )

        for skill, fixture in (
            ("grounded-implementation", "grounded-implementation-single-use-token"),
            ("reproduction-first-debugging", "reproduction-first-config-flag"),
            ("precision-review", "precision-review-tenant-cache"),
            (
                "specification-grounded-testing",
                "specification-grounded-testing-resource-id",
            ),
            (
                "profile-guided-optimization",
                "profile-guided-optimization-first-match",
            ),
        ):
            cases = [record for record in records if record["skill"] == skill]
            kinds = {record["kind"] for record in cases}
            self.assertTrue(required_kinds <= kinds)
            self.assertIn(fixture, {record.get("fixture") for record in cases})

    def test_cli_check_results_rejects_invalid_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.jsonl"
            path.write_text(json.dumps({"case_id": "missing-fields"}) + "\n", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self.module.main(["check-results", str(path)])
            self.assertEqual(1, exit_code)
            self.assertIn("missing fields", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
