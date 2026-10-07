# Repository notes

- Invocation policy is declared twice per skill and must agree (enforced by `scripts/validate_skills.py`):
  `policy.allow_implicit_invocation` in `agents/openai.yaml` (read only by Codex) and `disable-model-invocation`
  in `SKILL.md` (read by Claude Code and OpenCode). Codex ignores the extra frontmatter key. Only `jujutsu` is
  implicit; keep it that way unless the user decides otherwise.
- Live invocation check (run with codex-cli 0.160.1 and Claude Code 2.1.291): copy each skill into a temporary
  git repo as `.claude/skills/probe-<name>` and `.agents/skills/probe-<name>`, renaming the `name:` field. The
  rename stops installed global copies with the same names from shadowing the ones under test. Then ask
  `claude -p --model haiku` and `codex exec -s read-only` to list the visible `probe-*` skills, and confirm
  `/probe-<name>` or `$probe-<name>` still loads a hidden skill.
- Python is not on PATH on the maintainer's NixOS machine; `uv run --no-project python ...` runs the documented
  checks.
