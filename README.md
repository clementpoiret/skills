# Software Change Assurance Skills

Composable [Agent Skills](https://agentskills.io/) for safer, easier-to-review software changes in
[Codex](https://developers.openai.com/codex/) and [Claude Code](https://code.claude.com/docs/en/overview).

This collection helps one primary agent define what must change, consult the other coding agent as an independent
read-only peer, implement and verify the change, and remove unnecessary complexity from production code and tests only
after the checks are green. It also includes a comprehensive Jujutsu workflow that activates automatically in `jj`
repositories.

The primary agent always owns the task, edits, verification, and final answer. A peer finding is evidence to check, not
a vote or an instruction to copy blindly.

## Included skills

| Skill                                                                      | Purpose                                                                                                                                                                                              | Typical prompt                                                                                                             |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| [`change-contract`](skills/change-contract/SKILL.md)                       | Define observable `AC-*` acceptance criteria, preserved `INV-*` invariants, scope, risk, and verification evidence before implementation; or audit a completed change against the accepted contract. | “Define a change contract for this bug. Do not implement it yet.”                                                          |
| [`cross-agent`](skills/cross-agent/SKILL.md)                               | Ask Claude from Codex, or Codex from Claude, for an independent challenge, investigation, proposal, review, or audit; then verify and reconcile every material finding.                              | “Ask Claude to audit the current working copy, then reconcile its findings.”                                               |
| [`simplify-after-green`](skills/simplify-after-green/SKILL.md)             | Remove unnecessary concepts from an already-correct change while preserving behavior, interfaces, security, compatibility, concurrency, performance, and test strength.                              | “The relevant checks are green. Simplify this change without altering its contract.”                                       |
| [`simplify-tests-after-green`](skills/simplify-tests-after-green/SKILL.md) | Reduce duplicate, brittle, slow, implementation-coupled, or low-value tests after green while preserving fault detection, behavioral boundaries, isolation, and useful diagnostics.                  | “The focused suite is green. Use simplify-tests-after-green on the tests affected by this change; preserve fault detection.” |
| [`jujutsu`](skills/jujutsu/SKILL.md)                                       | Detect Jujutsu automatically and use safe, noninteractive `jj` workflows for working copies, revisions, bookmarks, tags, remotes, conflicts, workspaces, and recovery.                               | “Show the current status and move this work onto trunk.”                                                                   |

The first four skills are VCS-agnostic and work with dirty Git or Jujutsu working copies. They do not require a clean
tree, branch, commit, or pushed remote. In a Jujutsu repository, `jujutsu` supplies the VCS mechanics automatically; in
a Git-only repository, the host continues with its normal Git workflow.

## Requirements

- A local Codex or Claude Code installation for whichever host you use.
- Both the `codex` and `claude` CLIs, installed, authenticated, and available on `PATH`, to use `cross-agent` in both
  directions.
- Git to clone and update this repository.
- Jujutsu only if you want to use the `jujutsu` skill in `jj` repositories.

`cross-agent` launches the peer CLI in the same repository and execution environment as the primary. Local-only peer
runs therefore require both CLIs on that machine or container. A cloud agent that cannot access the other CLI will
report the peer as unavailable and continue with primary analysis; it must not invent a peer verdict.

Peer calls use the authentication, model access, quota, and billing configuration of the invoked CLI. Review your
repository's data-handling rules before allowing either provider to inspect sensitive code. By default, peer calls use
frontier models at `xhigh` effort, which can consume more quota and take longer than configured host defaults.

## Installation

### 1. Clone the source once

```sh
skills_checkout="$HOME/.local/share/clementpoiret-skills"
git clone https://github.com/clementpoiret/skills.git "$skills_checkout"
```

The following commands link that checkout rather than copying it, so one update refreshes every installed skill. They
skip existing destinations instead of overwriting another installation.

### 2. Install for Codex, Claude Code, or both

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

Remove the corresponding `link_skills` line for a host you do not use. Codex loads personal skills from
`~/.agents/skills`; Claude Code loads them from `~/.claude/skills`. Both support symlinked skill directories.

For a project-scoped installation, use `<project>/.agents/skills` for Codex and `<project>/.claude/skills` for Claude
Code instead. Local symlinks are convenient for one machine; if a team needs the skills automatically in every clone,
vendor the selected skill directories into those project paths and commit them.

Official host documentation:

- [Where Codex loads local skills](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
- [Where Claude Code skills live](https://code.claude.com/docs/en/slash-commands#where-skills-live)

### 3. Verify discovery

Start the host from a repository and list its skills:

- Codex: run `/skills` and look for `$change-contract`, `$cross-agent`, `$simplify-after-green`,
  `$simplify-tests-after-green`, and `$jujutsu`.
- Claude Code: run `/skills` and look for `/change-contract`, `/cross-agent`, `/simplify-after-green`,
  `/simplify-tests-after-green`, and `/jujutsu`.

Both hosts can select an eligible skill automatically from its description. `simplify-tests-after-green` is
explicit-invocation only so an agent does not remove tests without a direct request. You can invoke a skill explicitly:

```text
# Codex
$change-contract Define a contract for making password-reset tokens single-use. Do not implement it.

# Claude Code
/change-contract Define a contract for making password-reset tokens single-use. Do not implement it.
```

If a newly created top-level skill directory does not appear, restart the host and check that each installed path
resolves to a directory containing `SKILL.md`.

### Update

```sh
git -C "$HOME/.local/share/clementpoiret-skills" pull --ff-only
```

The symlinks continue to point at the updated checkout. Restart a host only if it does not detect the change.

## End-to-end workflow: Codex primary, Claude peer

Suppose you want to make password-reset tokens single-use. Keep one Codex session as the primary owner so the accepted
contract and observed evidence remain in context.

```text
Claude contract proposal
    -> Codex verification and accepted contract
    -> Codex implementation
    -> focused and broad checks
    -> Claude audit
    -> Codex reconciliation and fixes
    -> checks again
    -> Codex simplification after green
    -> Codex test simplification after green, when requested
    -> final checks
```

### 1. Ask Claude to propose the contract

Tell Codex:

```text
Act as the primary owner. Ask Claude to define a change contract for making
password-reset tokens single-use. Keep the peer read-only. Then inspect the
repository yourself, verify and reconcile the proposal, and return the accepted
AC-* and INV-* items. Do not implement yet.
```

This activates `cross-agent` for the peer call and `change-contract` for the contract semantics. Codex remains
responsible for checking the proposal against the repository and resolving unsupported assumptions. `cross-agent`
defaults the Claude peer to the `opus` alias—currently Claude Opus 5—at `xhigh` effort.

`opus` is Claude Code's moving alias for the latest available Opus model. Name a full model ID when you need to pin an
exact model version instead of following that alias.

### 2. Implement with Codex

After accepting the contract, tell Codex:

```text
Implement the accepted contract as the primary agent. Make only the smallest
complete change, add the required regression evidence, and run the focused
checks first followed by the repository-required broader checks. Keep unrelated
working-copy changes out of scope.
```

### 3. Audit with Claude

Once the implementation checks are green, tell Codex:

```text
Ask Claude to audit the current working copy against the accepted contract. Keep
the audit read-only. Verify each finding yourself, accept or reject it with
evidence, apply any accepted fixes, and rerun the affected checks.
```

The peer inspects the live working copy; you do not need to create a commit or branch first. Codex should report what it
accepted, rejected, or could not resolve rather than forwarding Claude's answer unchanged.

### 4. Simplify with Codex

After the implementation and audit fixes are green, tell Codex:

```text
The relevant checks are green. Use simplify-after-green on the current change.
Preserve every accepted AC-* and INV-* item, public interface, and test strength.
Remove only complete unnecessary concepts, then rerun the baseline and final
repository checks. A no-change result is valid.
```

For a high-risk or nontrivial simplification, optionally request a fresh peer review focused on lost invariants, hidden
consumers, weakened tests, or complexity that was moved instead of removed.

### 5. Simplify affected tests with Codex

When the focused suite is stable and green, explicitly ask Codex to review only the tests created or affected by the
current work and their nearest related suite:

```text
The focused suite is green. Use simplify-tests-after-green on the tests created
or affected by this change. Preserve every behavioral obligation and boundary.
Remove or merge a test only with discriminating evidence that the surviving
suite catches the same realistic regression, then rerun the baseline checks.
```

The skill maps tests to behavioral obligations and boundary-specific faults before changing them. Equal coverage or two
tests exercising the same feature is not sufficient evidence of duplication: unit, integration, protocol, persistence,
and end-to-end checks can protect different failure modes. It records a green baseline, requires a surviving test or
other discriminator for every removal or merge, preserves case-level diagnostics and isolation, and reruns the baseline
afterward. A `no-change` or candidate-level `blocked` result is valid when redundancy cannot be demonstrated safely.

The same workflow works in reverse with Claude Code as primary: ask it to call Codex for the contract proposal and
audit, while Claude owns implementation, reconciliation, and simplification.

## Can the primary choose the peer model and effort?

Yes. `cross-agent` now makes the selection explicit on every peer invocation and defaults to:

| Direction      | Default peer model              | Default effort |
| -------------- | ------------------------------- | -------------- |
| Codex → Claude | `opus`, currently Claude Opus 5 | `xhigh`        |
| Claude → Codex | `gpt-5.6-sol`                   | `xhigh`        |

You can request a different model or effort in ordinary language. An explicit selection overrides these defaults for
that peer run, subject to repository policy and availability in the peer CLI.

Under the hood, the model selection maps to the peer CLI:

```sh
# Codex primary -> Claude peer
claude -p --model opus --effort xhigh ...

# Claude primary -> Codex peer
codex exec --model gpt-5.6-sol \
  -c 'model_reasoning_effort="xhigh"' ...
```

The skill adds its read-only, ephemeral, and repository-scoping flags around these options. Use a moving alias such as
`opus` when you want the newest model available under that alias; use the provider's exact model ID when reproducibility
matters.

Important limitations:

- A native Codex subagent cannot become a Claude model, and a native Claude subagent cannot become a Codex model merely
  by changing a model name. Cross-provider review works here because `cross-agent` launches the other CLI.
- The model must be available to the invoked CLI under the active account, plan, organization policy, and provider.
- Effort levels are model-dependent. An unsupported level may be rejected or reduced by the host, so inspect the peer
  result and CLI output rather than assuming the request took effect.
- The skill must report the requested and effective selection, or the exact limitation when the effective selection is
  not observable. It must not silently downgrade or claim an unverified model.
- Model and effort overrides apply to that peer run. They do not silently change the primary agent's model.

Codex also supports model and effort defaults or explicit overrides for its own native subagents; see the
[Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference). Claude Code exposes
`--model` and `--effort` for a session; see its [CLI reference](https://code.claude.com/docs/en/cli-reference) and
[model configuration guide](https://code.claude.com/docs/en/model-config#adjust-effort-level).

## Design and safety rules

- One primary owns edits and the final decision. The peer is independent and read-only by default.
- One peer run has one clear role: challenge, investigate, propose, review, or audit.
- Peer runs are synchronous. The primary does not edit the same working copy while the peer is inspecting it.
- The default target is the current working copy, including relevant uncommitted and untracked changes.
- A peer never recursively invokes `cross-agent`, another subagent, or an agent team.
- Every material peer finding is independently verified against source, callers, tests, and observed command output.
- Agreement between models is not proof. Repository policy and reproducible evidence remain authoritative.
- Existing unrelated edits are preserved. The skills do not clean, stash, reset, commit, rewrite history, push, deploy,
  or perform another external write unless the user separately requests and authorizes it.
- A writable peer is exceptional: the user must explicitly request it, the scope must be bounded and non-overlapping,
  and the primary must inspect and verify every resulting change.

## More usage examples

```text
Define a change contract for this API change before editing code.

Ask Claude to challenge the draft contract for missing compatibility and rollback
criteria. Verify its concerns and update only the accepted items.

Have Codex independently investigate this race condition and propose
discriminating checks. Do not edit the working copy.

Audit the current working copy against this accepted contract. Grade every AC-*
and INV-* item with observed evidence.

The focused and broad checks are green. Simplify this change without changing
its behavior, then ask the other model for a behavior-preservation review.

The focused suite is green. Use simplify-tests-after-green on the tests affected
by this change. Preserve fault detection and boundary coverage.

Show the current repository status and move this work onto trunk.
```

In the final example, an agent inside a Jujutsu repository should activate `jujutsu` automatically and use `jj`; the
user should not need to name the VCS or skill.

## Evaluation and development

The skills are instruction-only: no helper program, request file, branch, or remote service is required. Behavioral
evaluation cases live in [`EVALS.md`](EVALS.md). Run the relevant cases in both Codex and Claude Code when changing
skill descriptions, trigger rules, delegation semantics, review targets, safety boundaries, or Jujutsu commands.

Issues and pull requests are welcome at [`github.com/clementpoiret/skills`](https://github.com/clementpoiret/skills).
Please keep changes small, preserve the cross-host Agent Skills format, and include an eval case for material behavioral
changes.

## License

[MIT](LICENSE) © 2026 Clément Poiret.
