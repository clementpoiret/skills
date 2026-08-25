from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "eval_fixtures.py"


def load_module():
    spec = importlib.util.spec_from_file_location("eval_fixtures", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GROUND_GOOD = '''\
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TokenRecord:
    user_id: str
    expires_at: float
    consumed: bool = False


class TokenStore:
    def __init__(self) -> None:
        self._records: dict[str, TokenRecord] = {}

    def issue(self, token: str, user_id: str, expires_at: float) -> None:
        self._records[token] = TokenRecord(
            user_id=user_id,
            expires_at=expires_at,
        )

    def verify(self, token: str, now: float) -> str | None:
        record = self._records.get(token)
        if record is None or record.consumed or now >= record.expires_at:
            return None
        return record.user_id

    def consume(self, token: str, now: float) -> str | None:
        record = self._records.get(token)
        if record is None or record.consumed or now >= record.expires_at:
            return None
        record.consumed = True
        return record.user_id
'''

DEBUG_GOOD = '''\
from __future__ import annotations


TRUE_VALUES = frozenset({"true", "1", "yes", "on"})
FALSE_VALUES = frozenset({"false", "0", "no", "off"})


def parse_bool(raw: str | None, *, default: bool = False) -> bool:
    """Parse a repository boolean setting."""
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"invalid boolean value: {raw!r}")
'''



TESTING_GOOD = r'''
from __future__ import annotations

import unittest

from src.resource_ids import canonicalize_resource_id


class ResourceIdContractTests(unittest.TestCase):
    def test_canonicalizes_ascii_letters_and_preserves_allowed_characters(self) -> None:
        cases = {
            "Item-7": "item-7",
            "A_B-09": "a_b-09",
            "  Mixed_Case-1\t": "mixed_case-1",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(expected, canonicalize_resource_id(raw))

    def test_length_is_checked_after_ascii_space_and_tab_trim(self) -> None:
        self.assertEqual("abcdefghij", canonicalize_resource_id("  ABCDEFGHIJ  "))
        self.assertEqual("abcdefghijkl", canonicalize_resource_id("ABCDEFGHIJKL"))
        with self.assertRaises(ValueError):
            canonicalize_resource_id("ABCDEFGHIJKLM")
        for raw in ("", "   ", "\t\t"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    canonicalize_resource_id(raw)

    def test_only_ascii_space_and_tab_are_trimmed(self) -> None:
        for raw in ("\nabc\n", "\rabc", "abc\v"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    canonicalize_resource_id(raw)

    def test_rejects_internal_whitespace_and_punctuation(self) -> None:
        for raw in ("a b", "a\tb", "a/b", "a.b"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    canonicalize_resource_id(raw)

    def test_rejects_non_ascii_characters(self) -> None:
        for raw in ("café", "Å", "１２"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    canonicalize_resource_id(raw)

    def test_rejects_non_strings_with_type_error(self) -> None:
        for raw in (123, None, b"abc"):
            with self.subTest(raw=raw):
                with self.assertRaises(TypeError):
                    canonicalize_resource_id(raw)
'''

OPTIMIZATION_GOOD = '''\
from __future__ import annotations

from collections.abc import Hashable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entry:
    key: Hashable
    value: int


def resolve_first(
    entries: Sequence[Entry],
    queries: Sequence[Hashable],
) -> list[int | None]:
    index: dict[Hashable, int] = {}
    for entry in entries:
        if entry.key not in index:
            index[entry.key] = entry.value
    return [index.get(query) for query in queries]
'''

OPTIMIZATION_LAST_WINS = '''\
from __future__ import annotations

from collections.abc import Hashable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Entry:
    key: Hashable
    value: int


def resolve_first(
    entries: Sequence[Entry],
    queries: Sequence[Hashable],
) -> list[int | None]:
    index = {entry.key: entry.value for entry in entries}
    return [index.get(query) for query in queries]
'''



class EvalFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_fixture_structure_and_self_checks_pass(self) -> None:
        self.assertEqual([], self.module.validate_all())
        self.assertEqual([], self.module.self_check())
        self.assertEqual(5, len(self.module.discover_manifests()))

    def test_grounded_fixture_rejects_baseline_and_accepts_complete_behavior(self) -> None:
        fixture_dir, manifest = self.module.get_fixture("grounded-implementation-single-use-token")
        baseline = self.module.run_verifier(fixture_dir, manifest, fixture_dir / "workspace")
        self.assertNotEqual(0, baseline.returncode)
        self.assertIn("consume", baseline.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "candidate"
            shutil.copytree(fixture_dir / "workspace", candidate)
            (candidate / "src" / "session_tokens.py").write_text(GROUND_GOOD, encoding="utf-8")
            result = self.module.run_verifier(fixture_dir, manifest, candidate)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_debug_fixture_rejects_caller_workaround_and_accepts_parser_root_cause(self) -> None:
        fixture_dir, manifest = self.module.get_fixture("reproduction-first-config-flag")
        with tempfile.TemporaryDirectory() as tmp:
            workaround = Path(tmp) / "workaround"
            shutil.copytree(fixture_dir / "workspace", workaround)
            service = workaround / "src" / "service.py"
            service.write_text(
                service.read_text(encoding="utf-8").replace(
                    'return parse_bool(environment.get("FEATURE_X"), default=False)',
                    'return environment.get("FEATURE_X") != "false"',
                ),
                encoding="utf-8",
            )
            result = self.module.run_verifier(fixture_dir, manifest, workaround)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("root cause", result.stderr)

            good = Path(tmp) / "good"
            shutil.copytree(fixture_dir / "workspace", good)
            (good / "src" / "config_flags.py").write_text(DEBUG_GOOD, encoding="utf-8")
            result = self.module.run_verifier(fixture_dir, manifest, good)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_review_fixture_rewards_precision_and_rejects_speculation(self) -> None:
        fixture_dir, manifest = self.module.get_fixture("precision-review-tenant-cache")
        accepted = self.module.run_verifier(fixture_dir, manifest, fixture_dir / manifest["accepted_sample"])
        rejected = self.module.run_verifier(fixture_dir, manifest, fixture_dir / manifest["rejected_sample"])
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("missed", rejected.stderr)
        self.assertIn("unsupported", rejected.stderr)

    def test_testing_fixture_requires_an_independent_behavioral_oracle(self) -> None:
        fixture_dir, manifest = self.module.get_fixture(
            "specification-grounded-testing-resource-id"
        )
        baseline = self.module.run_verifier(
            fixture_dir,
            manifest,
            fixture_dir / "workspace",
        )
        self.assertNotEqual(0, baseline.returncode)
        self.assertIn("did not reject", baseline.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "candidate"
            shutil.copytree(fixture_dir / "workspace", candidate)
            (candidate / "tests" / "test_resource_ids.py").write_text(
                TESTING_GOOD,
                encoding="utf-8",
            )
            result = self.module.run_verifier(fixture_dir, manifest, candidate)
            self.assertEqual(0, result.returncode, result.stderr)

            production_edit = Path(tmp) / "production-edit"
            shutil.copytree(candidate, production_edit)
            source = production_edit / "src" / "resource_ids.py"
            source.write_text(
                source.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            result = self.module.run_verifier(
                fixture_dir,
                manifest,
                production_edit,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("test-only task", result.stderr)

    def test_optimization_fixture_requires_speed_and_semantic_preservation(self) -> None:
        fixture_dir, manifest = self.module.get_fixture(
            "profile-guided-optimization-first-match"
        )
        baseline = self.module.run_verifier(
            fixture_dir,
            manifest,
            fixture_dir / "workspace",
        )
        self.assertNotEqual(0, baseline.returncode)
        self.assertIn("operation budget", baseline.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            last_wins = Path(tmp) / "last-wins"
            shutil.copytree(fixture_dir / "workspace", last_wins)
            (last_wins / "src" / "batch_lookup.py").write_text(
                OPTIMIZATION_LAST_WINS,
                encoding="utf-8",
            )
            result = self.module.run_verifier(fixture_dir, manifest, last_wins)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("first-match", result.stderr)

            good = Path(tmp) / "good"
            shutil.copytree(fixture_dir / "workspace", good)
            (good / "src" / "batch_lookup.py").write_text(
                OPTIMIZATION_GOOD,
                encoding="utf-8",
            )
            result = self.module.run_verifier(fixture_dir, manifest, good)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_materialization_excludes_verifier_and_includes_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "trial"
            self.module.materialize("grounded-implementation-single-use-token", destination)
            self.assertTrue((destination / "TASK.md").is_file())
            self.assertTrue((destination / ".eval-fixture.json").is_file())
            self.assertFalse((destination / "verify.py").exists())
            self.assertTrue((destination / "src" / "session_tokens.py").is_file())
            (destination / "src" / "session_tokens.py").write_text(
                GROUND_GOOD,
                encoding="utf-8",
            )
            fixture_dir, manifest = self.module.get_fixture(
                "grounded-implementation-single-use-token"
            )
            result = self.module.run_verifier(fixture_dir, manifest, destination)
            self.assertEqual(0, result.returncode, result.stderr)


    def test_validation_does_not_skip_invalid_or_duplicate_manifest_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / "skills" / "grounded-implementation"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# fixture test\n", encoding="utf-8")
            fixtures = repo / "evals" / "fixtures"
            for name, fixture_id in (("one", "duplicate"), ("two", "duplicate")):
                fixture = fixtures / name
                (fixture / "workspace").mkdir(parents=True)
                (fixture / "task.md").write_text("task\n", encoding="utf-8")
                (fixture / "verify.py").write_text("pass\n", encoding="utf-8")
                (fixture / "manifest.json").write_text(
                    __import__("json").dumps(
                        {
                            "id": fixture_id,
                            "skill": "grounded-implementation",
                            "mode": "workspace",
                            "task": "task.md",
                            "workspace": "workspace",
                            "verifier": "verify.py",
                            "baseline_expected": "fail",
                        }
                    ),
                    encoding="utf-8",
                )
            errors = self.module.validate_all(fixtures)
            self.assertTrue(any("duplicate fixture id" in error for error in errors), errors)
            self.assertTrue(any("must match directory name" in error for error in errors), errors)

    def test_artifact_sample_paths_cannot_escape_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / "skills" / "precision-review"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# fixture test\n", encoding="utf-8")
            fixture = repo / "evals" / "fixtures" / "review"
            (fixture / "workspace").mkdir(parents=True)
            (fixture / "task.md").write_text("task\n", encoding="utf-8")
            (fixture / "verify.py").write_text("pass\n", encoding="utf-8")
            (fixture / "rejected.json").write_text("{}\n", encoding="utf-8")
            (fixture.parent / "outside.json").write_text("{}\n", encoding="utf-8")
            manifest = {
                "id": "review",
                "skill": "precision-review",
                "mode": "artifact",
                "task": "task.md",
                "workspace": "workspace",
                "verifier": "verify.py",
                "accepted_sample": "../outside.json",
                "rejected_sample": "rejected.json",
            }
            (fixture / "manifest.json").write_text(
                __import__("json").dumps(manifest),
                encoding="utf-8",
            )
            errors = self.module.validate_all(fixture.parent)
            self.assertTrue(any("accepted_sample escapes" in error for error in errors), errors)


    def test_workspace_cli_verification_fails_closed_without_sandbox_acknowledgement(self) -> None:
        fixture_dir, _ = self.module.get_fixture(
            "grounded-implementation-single-use-token"
        )
        result = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "verify",
                "grounded-implementation-single-use-token",
                str(fixture_dir / "workspace"),
            ],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("disposable sandbox", result.stderr)

    def test_materialization_refuses_to_expose_hidden_verifier_siblings(self) -> None:
        fixture_dir, _ = self.module.get_fixture(
            "grounded-implementation-single-use-token"
        )
        destination = fixture_dir / "workspace" / "nested-trial"
        with self.assertRaisesRegex(ValueError, "hidden verifier"):
            self.module.materialize(
                "grounded-implementation-single-use-token",
                destination,
            )

    def test_cli_check_command_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "check"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("5 fixture", result.stdout)


if __name__ == "__main__":
    unittest.main()
