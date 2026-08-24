# Software Change Assurance Skills

Composable [Agent Skills](https://agentskills.io/) for safer, easier-to-review software changes in
[Codex](https://developers.openai.com/codex/) and [Claude Code](https://docs.anthropic.com/en/docs/claude-code/skills).

The collection provides five focused workflows:

| Skill                                                                      | Purpose                                                                                                                                                                           |
| -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`change-contract`](skills/change-contract/SKILL.md)                       | Define observable `AC-*` acceptance criteria, preserved `INV-*` invariants, scope, risk, and required evidence; or audit a completed target against an already accepted contract. |
| [`cross-agent`](skills/cross-agent/SKILL.md)                               | Obtain an independent read-only challenge, investigation, proposal, review, or audit from the other local coding-agent CLI, then verify and reconcile each material finding.      |
| [`simplify-after-green`](skills/simplify-after-green/SKILL.md)             | Remove one unnecessary production-code concept after relevant checks are green while preserving accepted behavior and boundary properties.                                        |
| [`simplify-tests-after-green`](skills/simplify-tests-after-green/SKILL.md) | Reduce test maintenance or runtime cost after green only when discriminating evidence preserves fault detection and diagnostics.                                                  |
| [`jujutsu`](skills/jujutsu/SKILL.md)                                       | Detect Jujutsu workspaces and use safe, noninteractive `jj` workflows with progressive disclosure for advanced operations.                                                        |

The primary agent always owns scope, edits, checks, and the final answer. Peer output is evidence to verify, not a vote
or an instruction to copy blindly.

## Invocation policy

The policy is intentionally conservative. Workflows that can edit code, remove tests, make an external peer call, or
change the meaning of a review are explicit-only. Jujutsu is eligible for automatic activation because using the wrong
VCS mutation surface in an active `jj` workspace is itself hazardous.

| Skill                        | Codex                 | Claude Code           |
| ---------------------------- | --------------------- | --------------------- |
| `change-contract`            | Explicit only         | Explicit only         |
| `cross-agent`                | Explicit only         | Explicit only         |
| `simplify-after-green`       | Explicit only         | Explicit only         |
| `simplify-tests-after-green` | Explicit only         | Explicit only         |
| `jujutsu`                    | Automatic or explicit | Automatic or explicit |

Explicit syntax:

```text
# Codex
$change-contract Define a contract for making password-reset tokens single-use. Do not implement it.

# Claude Code
/change-contract Define a contract for making password-reset tokens single-use. Do not implement it.
```

To compose explicit-only skills, invoke each one in the same user request:

```text
# Codex: independent contract challenge
$cross-agent $change-contract Define and independently challenge a contract for making tokens single-use.

# Claude Code: independent preservation review
/cross-agent /simplify-after-green Simplify the green change and obtain a fresh read-only preservation review.
```

A loaded `change-contract` or `simplify-after-green` skill does not silently invoke `cross-agent`. This preserves user
control over network access, quota, provider disclosure, and latency.

## Requirements

- A local Codex or Claude Code installation for the chosen host.
- Both `codex` and `claude`, installed, authenticated, and available on `PATH`, to use `cross-agent` in both directions.
- Git to clone and update this repository.
- Jujutsu only for repositories where the `jujutsu` workflow is needed.
- Python 3.10 or later to run the dependency-free repository validation and evaluation utilities.

`cross-agent` launches the peer CLI in the same repository and execution environment as the primary. The peer call uses
the invoked CLI's authentication, entitlement, quota, billing, and data-handling configuration. The skill preflights the
installed command surface and does not assume that a moving model alias, reasoning-effort value, or CLI flag is
available. When a peer cannot run, the primary continues its own analysis and reports the exact limitation; it never
invents a peer verdict.

## Installation

### Clone once

```sh
skills_checkout="$HOME/.local/share/clementpoiret-skills"
git clone https://github.com/clementpoiret/skills.git "$skills_checkout"
```

### Link into Codex, Claude Code, or both

```sh
skills_checkout="$HOME/.local/share/clementpoiret-skills"

link_skills() {
  skills_dir="$1"
  mkdir -p "$skills_dir"

  for skill in change-contract cross-agent simplify-after-green simplify-tests-after-green jujutsu; do
    destination="$skills_dir/$skill"
    if [ -e "$destination" ] || [ -L "$destination" ]; then
      printf 'skip %s (already exists)\n' "$destination"
    else
      ln -s "$skills_checkout/skills/$skill" "$destination"
    fi
  done
}

link_skills "$HOME/.agents/skills"  # Codex
link_skills "$HOME/.claude/skills"  # Claude Code
```

Remove the line for a host you do not use. For project-scoped installation, use `<project>/.agents/skills` for Codex and
`<project>/.claude/skills` for Claude Code. Teams can vendor selected skill directories into those paths instead of
using personal symlinks.

### Verify discovery

Start the host from a repository and list available skills:

- Codex: `/skills`; look for `$change-contract`, `$cross-agent`, `$simplify-after-green`, `$simplify-tests-after-green`,
  and `$jujutsu`.
- Claude Code: `/skills`; look for `/change-contract`, `/cross-agent`, `/simplify-after-green`,
  `/simplify-tests-after-green`, and `/jujutsu`.

If a linked skill is missing, restart the host and verify that the resolved directory contains `SKILL.md` and, for Codex
metadata, `agents/openai.yaml`.

### Update

```sh
git -C "$HOME/.local/share/clementpoiret-skills" pull --ff-only
```

## Recommended workflow

The example below keeps one primary agent responsible throughout. Replace `$...` with `/...` when Claude Code is the
primary.

### 1. Define and optionally challenge the contract

Primary-only:

```text
$change-contract Define a change contract for making password-reset tokens single-use. Do not implement it.
```

With an independent peer challenge:

```text
$cross-agent $change-contract Act as the primary owner. Define a change contract for making password-reset tokens
single-use, ask the peer to challenge omissions and risk, verify the peer's claims, and return the accepted AC-* and
INV-* items. Do not implement yet.
```

### 2. Implement and verify as the primary

```text
Implement the accepted contract. Make the smallest complete change, add the required regression evidence, run focused
checks followed by repository-required broader checks, and preserve unrelated working-copy edits.
```

### 3. Audit the result

Primary-only:

```text
$change-contract Audit the current working copy against the accepted contract. Grade every AC-* and INV-* item using
required evidence, observed evidence, and evidence status. Do not edit code.
```

With an independent peer:

```text
$cross-agent $change-contract Audit the current working copy against the accepted contract. Obtain a fresh read-only
peer audit, verify every material finding, and reconcile accepted, rejected, and unresolved findings.
```

### 4. Simplify production code after green

```text
$simplify-after-green The relevant checks are green. Remove at most one unnecessary concept while preserving the
accepted contract. Re-run the baseline and broader required checks.
```

Use `$cross-agent $simplify-after-green` only when an independent preservation review is worth its cost and disclosure.

### 5. Simplify tests only by explicit request

```text
$simplify-tests-after-green The focused and broader baselines are green. Review only tests affected by this change.
Remove or merge a candidate only when a mutation, known-bad replay, or exact static equivalence proves that surviving
evidence catches the same realistic fault.
```

A `no-change` result is valid for both simplification skills.

## Jujutsu behavior

`jujutsu` is the only implicitly invocable skill. Its first operation is `jj root`; the skill stops applying when that
command fails. In an active workspace it prefers `jj` for mutations, treats detached Git HEAD as normal in colocated
repositories, and verifies repository state after every mutation.

The main skill remains small. Advanced guidance is loaded only when relevant:

- history and rewrites;
- conflicts and operation-log recovery;
- bookmarks, remotes, fetch, push, and tags;
- workspaces;
- configuration and external commands through `jj run`;
- revision-description policy;
- version compatibility.

Jujutsu does not impose Conventional Commits globally. The skill follows the repository's own revision-description
policy and uses Conventional Commits only when that policy or the user requires them.

## Validation and evaluation

Run the static and unit checks before publishing changes:

```sh
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

The validator checks:

- required frontmatter and kebab-case names;
- alignment between Claude `disable-model-invocation` and Codex `allow_implicit_invocation`;
- a maximum of 500 lines in each main `SKILL.md`;
- existence and containment of relative Markdown references.

`EVALS.md` defines the empirical protocol. `evals/cases.jsonl` contains trigger, near-miss, procedural, and failure
cases, including dedicated test-simplification cases. Validate the case catalog and recorded runs with:

```sh
python scripts/eval_results.py check-cases evals/cases.jsonl
python scripts/eval_results.py check-results .eval-results/runs.jsonl
python scripts/eval_results.py summarize .eval-results/runs.jsonl
```

Measure skill availability, selection, actual access, downstream success, failure category, tokens, and wall time as
separate fields. Compare fresh-session `raw` and `skill` arms; do not treat successful invocation as proof of task
success.

## Repository layout

```text
skills/<name>/SKILL.md              Core instructions loaded when the skill runs
skills/<name>/agents/openai.yaml    Codex display metadata and invocation policy
skills/<name>/references/*.md       On-demand detail for larger workflows
scripts/validate_skills.py          Dependency-free static validator
scripts/eval_results.py             JSONL case/result validation and summary utility
evals/cases.jsonl                   Versioned evaluation catalog
EVALS.md                            Evaluation protocol and result schema
tests/                              Regression tests for repository contracts
```

## Security and operational notes

- A dirty working copy is supported; clean status is not a precondition.
- Never use reset, checkout, or broad history cleanup to make a skill easier to run.
- `allowed-tools` grants or preapproves matching calls on hosts that support it; it is not a denial boundary. Use host
  permissions, deny rules, hooks, and sandboxing for enforcement.
- A required runtime check that was not observed remains missing evidence.
- Peer review can be unavailable, stale, wrong, or more expensive than primary analysis. The primary must verify it.

## License

[MIT](LICENSE)
