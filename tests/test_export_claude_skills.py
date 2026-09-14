from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from export_claude_skills import export_skills
from validate_skills import parse_frontmatter, parse_openai_metadata, skill_body


class ClaudeExportTests(unittest.TestCase):
    def test_export_preserves_content_and_invocation_policy_without_tool_grants(self) -> None:
        before = {p: p.read_bytes() for p in (ROOT / "skills").rglob("*") if p.is_file()}
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "export"
            self.assertEqual(10, export_skills(ROOT, destination))
            for skill in (ROOT / "skills").iterdir():
                if not skill.is_dir():
                    continue
                exported = destination / skill.name / "SKILL.md"
                fields, issues = parse_frontmatter(exported)
                self.assertEqual([], issues)
                metadata, _ = parse_openai_metadata(skill / "agents" / "openai.yaml")
                self.assertEqual("true", fields["user-invocable"])
                self.assertEqual(str(not metadata["allow_implicit_invocation"]).lower(), fields["disable-model-invocation"])
                self.assertNotIn("allowed-tools", fields)
                self.assertEqual(skill_body(skill / "SKILL.md"), skill_body(exported))
                for path in skill.rglob("*"):
                    if path.is_file() and path.name != "SKILL.md":
                        self.assertEqual(path.read_bytes(), (destination / path.relative_to(ROOT / "skills")).read_bytes())
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_refuses_existing_destination_without_touching_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "existing"
            destination.mkdir()
            sentinel = destination / "keep.txt"
            sentinel.write_text("user work")
            with self.assertRaisesRegex(ValueError, "already exists"):
                export_skills(ROOT, destination)
            self.assertEqual("user work", sentinel.read_text())

    def test_refuses_destination_inside_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside"):
            export_skills(ROOT, ROOT / "unwanted-export")
        self.assertFalse((ROOT / "unwanted-export").exists())

    def test_refuses_invalid_source_before_creating_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "invalid"
            root.mkdir()
            destination = Path(tmp) / "export"
            with self.assertRaisesRegex(ValueError, "invalid source"):
                export_skills(root, destination)
            self.assertFalse(destination.exists())

    def test_refuses_dangling_destination_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "link"
            destination.symlink_to(Path(tmp) / "missing", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "already exists"):
                export_skills(ROOT, destination)
            self.assertTrue(destination.is_symlink())


if __name__ == "__main__":
    unittest.main()
