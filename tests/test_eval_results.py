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

    def test_result_validation_requires_distinct_activation_and_outcome_fields(self) -> None:
        record = {
            "case_id": "jj-trigger-status",
            "skill": "jujutsu",
            "host": "codex",
            "model": "example-model",
            "arm": "skill",
            "trial": 1,
            "available": True,
            "selected": True,
            "accessed": True,
            "success": True,
            "failure_category": None,
            "input_tokens": 100,
            "output_tokens": 50,
            "wall_seconds": 1.2,
            "notes": "",
        }
        self.assertEqual([], self.module.validate_result(record))

        incomplete = dict(record)
        incomplete.pop("accessed")
        errors = self.module.validate_result(incomplete)
        self.assertTrue(any("accessed" in error for error in errors), errors)

    def test_summary_keeps_activation_and_success_separate(self) -> None:
        base = {
            "case_id": "case",
            "skill": "jujutsu",
            "host": "codex",
            "model": "model",
            "arm": "skill",
            "available": True,
            "failure_category": None,
            "input_tokens": 100,
            "output_tokens": 50,
            "wall_seconds": 2.0,
            "notes": "",
        }
        records = [
            dict(base, trial=1, selected=True, accessed=True, success=True),
            dict(base, trial=2, selected=True, accessed=False, success=False),
            dict(base, trial=3, selected=False, accessed=False, success=False),
        ]
        summary = self.module.summarize(records)
        self.assertEqual(1, len(summary))
        row = summary[0]
        self.assertEqual(3, row["trials"])
        self.assertAlmostEqual(2 / 3, row["selection_rate"])
        self.assertAlmostEqual(1 / 3, row["access_rate"])
        self.assertAlmostEqual(1 / 3, row["success_rate"])
        self.assertEqual(300, row["input_tokens"])
        self.assertEqual(150, row["output_tokens"])

    def test_repository_case_catalog_is_valid(self) -> None:
        records = self.module.read_jsonl(REPO_ROOT / "evals" / "cases.jsonl")
        self.assertGreaterEqual(len(records), 25)
        self.assertEqual([], self.module.validate_cases(records))
        self.assertEqual(self.module.SKILLS, {record["skill"] for record in records})
        self.assertTrue(self.module.CASE_KINDS <= {record["kind"] for record in records})
        simplify_test_cases = [
            record for record in records if record["skill"] == "simplify-tests-after-green"
        ]
        self.assertGreaterEqual(len(simplify_test_cases), 8)
        jujutsu_cases = [record for record in records if record["skill"] == "jujutsu"]
        self.assertIn("trigger", {record["kind"] for record in jujutsu_cases})
        self.assertIn("near-miss", {record["kind"] for record in jujutsu_cases})

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
