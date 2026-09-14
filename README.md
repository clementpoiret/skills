# Focused coding skills for GPT-6 Astra

Ten instruction-only skills and a compact global coding policy. The canonical files target Codex with GPT-6 Astra. Model selection, reasoning effort, credentials, and runtime permissions belong in the host, not in a skill description.

The rewrite removes repeated workflow scaffolding while retaining the library's contracts, independent oracles, scope boundaries, and verification standards. Structural validation is not evidence of better model performance; see [EVALS.md](EVALS.md) for comparative trials and [AUDIT.md](AUDIT.md) for this revision's measured changes and validation limits.

## Skill selection

| Skill | Deliverable | Invocation |
| --- | --- | --- |
| `grounded-implementation` | Nontrivial requested feature or refactor, implemented and checked. | Automatic or explicit |
| `reproduction-first-debugging` | Evidence-led diagnosis and repair of a reported failure. | Automatic or explicit |
| `precision-review` | Read-only, actionable defect assessment. | Automatic or explicit |
| `specification-grounded-testing` | Tests or verifiers based on independent requirements. | Automatic or explicit |
| `profile-guided-optimization` | Measured, behavior-preserving improvement or a supported no-change result. | Automatic or explicit |
| `jujutsu` | Scoped VCS work in a confirmed Jujutsu workspace. | Automatic or explicit |
| `change-contract` | Defined acceptance criteria/invariants or an accepted-contract audit. | Explicit only |
| `cross-agent` | Independent external peer assessment; writes require separate scope. | Explicit only |
| `simplify-after-green` | Verified simplification of correct production code. | Explicit only |
| `simplify-tests-after-green` | Green-suite simplification preserving fault detection. | Explicit only |

Examples: `$precision-review` for an assessment, `$change-contract define` for a contract, or `$simplify-tests-after-green` for a test-maintenance pass. Ordinary implementation does not automatically start these optional workflows. Both simplification skills retain the original repository-wide default when the user supplies no narrower scope; name a directory or change budget when that is the intended limit.

## Install for Codex

Keep the extracted repository in a stable location. Install or symlink each directory under `skills/` into `~/.agents/skills/`, or into a project's `.agents/skills/` for project-scoped use. Codex supports symlinked skill folders. Do not install a second copy with the same skill names in another discovery location: duplicate names are not merged. See the official [skill discovery documentation](https://learn.chatgpt.com/docs/build-skills).

For an existing installation, first back up the matching ten skill directories or identify their symlink targets. Replace those copies with this revision; preserve unrelated installed skills. When symlinks already point to a maintained checkout, update that checkout rather than adding duplicate links. No installation or changes to your real configuration were performed by this package.

Back up the existing global policy, then copy `global/AGENTS.md` to `$CODEX_HOME/AGENTS.md`, normally `~/.codex/AGENTS.md`. A nonempty `AGENTS.override.md` at that level takes precedence, and project instructions can override broader guidance. Start a new session and inspect its loaded instruction sources. See the official [AGENTS.md discovery rules](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Do not paste every skill into the global file. Keep project commands, environment facts, and trusted local-test permissions in the relevant project's instructions. This global policy deliberately does not assert that every repository's tests are disposable or lack production access.

## Optional Claude Code copy

The canonical `SKILL.md` frontmatter contains only `name` and `description`. Codex invocation policy lives in `agents/openai.yaml`; it is not a substitute for Claude's host-specific controls. Generate a separate copy for Claude:

```sh
python scripts/export_claude_skills.py /tmp/skills-astra-claude
```

The destination must not exist and must be outside this repository. The exporter preserves the bodies and resources, sets `user-invocable: true`, and derives `disable-model-invocation` from each Codex invocation policy. It does not install anything or edit the source. Install the exported skill folders under your Claude skills location, preserving unrelated skills. Regenerate into a fresh destination after canonical updates.

The old `allowed-tools: Bash(jj *)` preapproval is intentionally not exported: a broad `jj` prefix is not a read-only restriction. Use reviewed host permissions instead. Claude's invocation and tool-grant semantics are documented [here](https://code.claude.com/docs/en/skills). Export compatibility is structurally tested; live host behavior still requires a runtime smoke test.

## Maintain and validate

The repository scripts use the Python standard library. Run:

```sh
python scripts/validate_skills.py
python scripts/eval_results.py check-cases evals/cases.jsonl
python scripts/eval_fixtures.py check
python -m unittest discover -s tests -v
```

Fixture checks execute bundled code; use a disposable development environment. Candidate verifiers additionally require explicit acknowledgment of untrusted-code execution; see [EVALS.md](EVALS.md).

Keep task-specific details in a skill and conditional references one level below its root. Keep maintainer reports here, not inside skill folders. The validator checks this library's lightweight metadata format, names, policies, links, scripts, and length constraints. It is not a general YAML parser or a model-quality evaluator. Run OpenAI's `skill-creator` validation when available and test actual trigger behavior after substantive changes.

License: [MIT](LICENSE), retained from the supplied repository.
