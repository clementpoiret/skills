# Focused coding skills

Ten reusable skills for coding agents, covering implementation, debugging, review, testing, optimization, and code maintenance. Each skill defines when to use it, how to approach the work, and what evidence is needed to call the task complete.

**These skills currently target GPT-6 and Fable 5.1.** The source format is for Codex, with an exporter for Claude Code. Select the model, reasoning effort, and permissions in your agent's configuration.

The library emphasizes understanding the existing code, keeping changes within scope, and verifying observable behavior. Skills are Markdown instructions with supporting references; the repository also includes validation scripts and evaluation fixtures.

## Available skills

| Skill | Use it to | Invocation |
| --- | --- | --- |
| [grounded-implementation](skills/grounded-implementation/SKILL.md) | Implement a nontrivial feature, behavior change, or refactor from requirements. | Automatic or explicit |
| [reproduction-first-debugging](skills/reproduction-first-debugging/SKILL.md) | Reproduce a reported failure, identify its cause, and verify the repair. | Automatic or explicit |
| [precision-review](skills/precision-review/SKILL.md) | Review code for concrete, actionable defects without editing it. | Automatic or explicit |
| [specification-grounded-testing](skills/specification-grounded-testing/SKILL.md) | Build tests and verifiers from independent requirements. | Automatic or explicit |
| [profile-guided-optimization](skills/profile-guided-optimization/SKILL.md) | Measure a bottleneck and improve performance while preserving behavior. | Automatic or explicit |
| [jujutsu](skills/jujutsu/SKILL.md) | Perform scoped version-control work in a confirmed Jujutsu workspace. | Automatic or explicit |
| [change-contract](skills/change-contract/SKILL.md) | Define acceptance criteria and invariants, or audit an accepted contract. | Explicit only |
| [cross-agent](skills/cross-agent/SKILL.md) | Request an independent Codex or Claude peer assessment, or a separately authorized peer edit. | Explicit only |
| [simplify-after-green](skills/simplify-after-green/SKILL.md) | Simplify correct production code while preserving verified behavior. | Explicit only |
| [simplify-tests-after-green](skills/simplify-tests-after-green/SKILL.md) | Simplify a passing test suite while preserving its ability to detect faults. | Explicit only |

Automatic skills can be selected by the agent when a task matches their description. Explicit-only skills require a direct request.

## Installation

Clone or download this repository to a stable location. Install only the skills you want, keeping each skill's complete directory and supporting files together. Back up any existing copies before replacing them, and preserve unrelated skills.

### Codex

Copy or symlink individual directories from `skills/` into `~/.agents/skills/` for personal use, or into your project's `.agents/skills/` for project use. Avoid duplicate installations with the same skill names. See the official [Codex skill discovery documentation](https://learn.chatgpt.com/docs/build-skills).

For example, run this from the repository root to install `precision-review` as a personal symlink, provided that destination does not already exist:

```sh
mkdir -p "$HOME/.agents/skills"
ln -s "$PWD/skills/precision-review" "$HOME/.agents/skills/precision-review"
```

A symlink uses the files in your checkout, so updates to that checkout also update the installed skill.

### Claude Code

Generate a Claude-compatible copy from the repository root:

```sh
python scripts/export_claude_skills.py /tmp/coding-skills-claude
```

The destination must be a new directory outside this repository. The exporter copies all ten skills and their resources, translating the Codex invocation policies into Claude frontmatter. It leaves the source files unchanged and does not install anything.

Copy the desired exported skill directories into `~/.claude/skills/` for personal use or your project's `.claude/skills/` for project use. See the official [Claude Code skills documentation](https://code.claude.com/docs/en/skills). After source updates, regenerate the export into a fresh directory and replace your installed copies.

## Usage

Give the agent a concrete task and a scope. In Codex, for example:

```text
$precision-review Review the current diff for actionable defects.

$change-contract define Define acceptance criteria for adding cursor pagination to the search endpoint.

$simplify-tests-after-green Simplify tests in tests/auth/ while preserving coverage of distinct behaviors.
```

In Claude Code, invoke the corresponding skill with `/precision-review`, `/change-contract`, or `/simplify-tests-after-green`.

The two simplification skills default to repository-wide scope when no narrower scope is supplied. Name a directory or component when you want a focused pass. The `cross-agent` skill requires an available, configured peer tool; the `jujutsu` skill requires an active Jujutsu workspace.

## Validation and evaluation

The repository's maintenance scripts use the Python standard library. Run these commands from the repository root:

```sh
python scripts/validate_skills.py
python scripts/eval_results.py check-cases evals/cases.jsonl
python scripts/eval_fixtures.py check
python -m unittest discover -s tests -v
```

The checks cover skill structure, invocation metadata, local links, evaluation cases, fixtures, and repository tooling. Fixture checks execute bundled code; run them in a disposable development environment.

These checks do not establish model performance. See [EVALS.md](EVALS.md) for the evaluation protocol, executable fixtures, and instructions for comparing skill-assisted runs with a no-skill baseline. Verify actual invocation behavior in your host after substantive skill changes.

## License

[MIT](LICENSE) © 2026 Clément Poiret.
