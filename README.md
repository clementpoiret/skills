# Verified Software Engineering Skills

A compact library of [Agent Skills](https://agentskills.io/) for improving verified software-engineering outcomes in
Codex and Claude Code. The library encodes narrow execution policies rather than general coding advice.

Every skill must be able to abstain. Generated or edited skills remain candidates until paired evaluation demonstrates
positive marginal value over the no-skill baseline.

## GPT-6 Astra and Claude Fable 5.1

These skills target GPT-6 Astra in Codex and Claude Fable 5.1 in Claude Code. The shared procedures keep requirements,
evidence, scope, and completion explicit. Model selection belongs to the host; loading a skill does not switch models.
`cross-agent` names both peer targets and checks their availability before use.

The prompt updates address unnecessary approval pauses, excessive verification, and instruction conflicts described in
[OpenAI's GPT-6 guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices). They also
address task completion, independent tool batching, and targeted file edits described in
[Anthropic's Fable 5.1 guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1).
Sources reviewed on 2026-09-04; this is a design basis, not measured proof of improvement.

- Carry out authorized work through the requested deliverable; a blocked obligation should not stop independent work.
- Preserve the user's scope and output preferences. Report decisive evidence without reproducing every internal ledger.
- Reuse verification evidence for unchanged state and add checks for a concrete obligation or unresolved risk.
- Use the host's available tools and permissions. Batch independent reads; keep dependent mutations and measurements
  ordered. Cross-provider peer work still requires explicit `cross-agent` invocation.
- During long tasks, give brief progress updates. At a compaction boundary, preserve scope, decisions, exact targets,
  observed checks, unresolved obligations, and the next action in the host's supported continuation summary.

Use existing host effort settings as a baseline. Sweep effort independently for each model; equal labels are not equal
compute. See [EVALS.md](EVALS.md) for the target matrix and model-specific checks. No paired model trials are included.

## Library

| Skill                                                                              | Primary job                                                                                                                                                              | Invocation            |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| [`grounded-implementation`](skills/grounded-implementation/SKILL.md)               | Implement a nontrivial feature, behavior change, or refactor from authoritative requirements and repository-local truth; finish through an observable verification gate. | Automatic or explicit |
| [`reproduction-first-debugging`](skills/reproduction-first-debugging/SKILL.md)     | Reproduce a reported failure, test competing hypotheses, patch the root cause minimally, add regression evidence, and rerun the original failure.                        | Automatic or explicit |
| [`precision-review`](skills/precision-review/SKILL.md)                             | Perform a read-only, high-precision change review and report only defects with a reachable trigger and supporting evidence.                                              | Automatic or explicit |
| [`specification-grounded-testing`](skills/specification-grounded-testing/SKILL.md) | Build tests or executable verifiers from authoritative requirements and validate both sensitivity and false-positive risk independently of the current implementation.   | Automatic or explicit |
| [`profile-guided-optimization`](skills/profile-guided-optimization/SKILL.md)       | Improve measured performance or resource use from a representative baseline, profile evidence, one bottleneck change, and keep-or-revert verification.                   | Automatic or explicit |
| [`change-contract`](skills/change-contract/SKILL.md)                               | Explicitly define observable `AC-*` acceptance criteria and `INV-*` invariants, or audit a target against an already accepted contract.                                  | Explicit only         |
| [`simplify-after-green`](skills/simplify-after-green/SKILL.md)                     | Audit the requested green production scope and apply justified simplifications while preserving accepted behavior.                                                        | Explicit only         |
| [`simplify-tests-after-green`](skills/simplify-tests-after-green/SKILL.md)         | Reduce green-suite maintenance or runtime cost only when discriminating evidence preserves fault detection and diagnostics.                                              | Explicit only         |
| [`cross-agent`](skills/cross-agent/SKILL.md)                                       | Obtain one independent Claude/Codex peer analysis, then verify and reconcile every material finding.                                                                     | Explicit only         |
| [`jujutsu`](skills/jujutsu/SKILL.md)                                               | Detect active Jujutsu workspaces and use safe, noninteractive, version-aware `jj` workflows.                                                                             | Automatic or explicit |

Five primary task-family skills cover implementation, debugging, review, test-oracle construction, and measured
optimization. Explicit procedures cover contracts, simplification, and independent peers; Jujutsu handles VCS mechanics.

## Routing and composition

Use zero skills when none changes the execution policy usefully. For ordinary software changes, select at most one
primary task-family skill:

1. **Read-only diff, commit, pull-request, or working-copy review** → `precision-review`.
1. **Known failure to diagnose or repair, including a regression** → `reproduction-first-debugging`.
1. **Tests, conformance suite, or executable verifier as the primary deliverable** → `specification-grounded-testing`.
1. **Measured optimization of behavior already accepted as correct** → `profile-guided-optimization`.
1. **Otherwise, nontrivial requested implementation or refactor** → `grounded-implementation`.

The explicit skills do not compete for automatic routing:

- `change-contract` defines requirements before implementation or grades an accepted contract after implementation.
- `simplify-after-green` and `simplify-tests-after-green` run only at a credible green checkpoint.
- `cross-agent` runs only when the user authorizes another provider and independent peer cost.

`jujutsu` is orthogonal. It may compose with one primary skill solely for VCS mechanics when `jj root` succeeds.

There is intentionally no separately routed “repository exploration,” “dependency safety,” or “final verification”
skill. Local-truth discovery, resolved-version checks, and completion gates remain phases inside the primary procedures.
Property/fuzz testing is part of specification-grounded testing when tests are the deliverable and remains a triggered
branch elsewhere. Performance regressions remain debugging; profile-guided optimization is only for accepted-correct
behavior. This avoids making a normal bug fix activate a stack of semantically similar skills.

## Invocation policy

| Skill                            | Codex                 | Claude Code           |
| -------------------------------- | --------------------- | --------------------- |
| `grounded-implementation`        | Automatic or explicit | Automatic or explicit |
| `reproduction-first-debugging`   | Automatic or explicit | Automatic or explicit |
| `precision-review`               | Automatic or explicit | Automatic or explicit |
| `specification-grounded-testing` | Automatic or explicit | Automatic or explicit |
| `profile-guided-optimization`    | Automatic or explicit | Automatic or explicit |
| `change-contract`                | Explicit only         | Explicit only         |
| `cross-agent`                    | Explicit only         | Explicit only         |
| `simplify-after-green`           | Explicit only         | Explicit only         |
| `simplify-tests-after-green`     | Explicit only         | Explicit only         |
| `jujutsu`                        | Automatic or explicit | Automatic or explicit |

Explicit syntax:

```text
# Codex
$change-contract Define a contract for making password-reset tokens single-use. Do not implement it.
$grounded-implementation Implement the accepted contract and verify every AC-* and INV-* item.
$specification-grounded-testing Add a conformance suite for the accepted contract. Do not edit production code.
$profile-guided-optimization Optimize the accepted implementation against the supplied benchmark and guardrails.

# Claude Code
/change-contract Define a contract for making password-reset tokens single-use. Do not implement it.
/grounded-implementation Implement the accepted contract and verify every AC-* and INV-* item.
/specification-grounded-testing Add a conformance suite for the accepted contract. Do not edit production code.
/profile-guided-optimization Optimize the accepted implementation against the supplied benchmark and guardrails.
```

Explicit composition remains user-controlled:

```text
# Codex
$cross-agent $precision-review Review the current diff and independently challenge only material findings.

# Claude Code
/cross-agent /simplify-after-green Simplify the green change and obtain a fresh preservation review.
```

No skill silently invokes `cross-agent`.

## Requirements

- Codex or Claude Code for the chosen host.
- Repository read/search/edit tools and project-native checks for the five primary skills; representative benchmark or
  deterministic cost tooling for profile-guided optimization.
- Both `codex` and `claude`, installed and authenticated, only when using `cross-agent` in both directions.
- Jujutsu only for repositories where `jujutsu` applies.
- Python 3.10 or later for dependency-free repository validation and evaluation utilities.

`cross-agent` uses the peer CLI's configured authentication, billing, quota, and data-handling policy. It preflights the
installed command surface and does not assume moving model aliases or CLI flags.

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

  for skill in \
    grounded-implementation \
    reproduction-first-debugging \
    precision-review \
    specification-grounded-testing \
    profile-guided-optimization \
    change-contract \
    cross-agent \
    simplify-after-green \
    simplify-tests-after-green \
    jujutsu
  do
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

For project-scoped installation, use `<project>/.agents/skills` for Codex and `<project>/.claude/skills` for Claude
Code.

### Verify discovery

In Codex, run `/skills` or type `$` to select a skill. In Claude Code, type `/` followed by the skill name. If a skill
is missing, verify the resolved directory contains `SKILL.md`; this repository also requires `agents/openai.yaml` for
Codex UI and invocation metadata.

### Update

```sh
git -C "$HOME/.local/share/clementpoiret-skills" pull --ff-only
```

## Representative workflows

### Implement a nontrivial change

```text
Implement tenant-aware caching while preserving the existing expiry contract and public API. Run focused checks and the
relevant regression suite.
```

`grounded-implementation` should establish the requirements, inspect consumers and repository versions, make the
smallest coherent patch, and independently re-check the original task against actual execution evidence.

For high-risk work, define the contract explicitly first:

```text
$change-contract Define AC-* and INV-* items for the tenant-cache change. Do not implement it.
$grounded-implementation Implement the accepted contract and report evidence for every item.
```

### Debug a failure

```text
This test started failing after the configuration change. Reproduce it, compare competing causes, fix the root cause,
add a regression test, and rerun the original command.
```

`reproduction-first-debugging` must not begin with a speculative patch. When the failure cannot be reproduced or
proxied, an investigation-only result is valid.

### Review a change

```text
Review the current diff for concrete regressions. Do not edit it and suppress findings that cannot be tied to a reachable
trigger.
```

`precision-review` recovers intent, traces affected contracts and consumers, and treats no findings as valid. Use
`$change-contract` or `/change-contract` instead for a formal accepted-contract audit.

### Build an independent test oracle

```text
Add a conformance suite for the accepted resource-identifier specification. Do not modify production code. Show which
plausible wrong behaviors the tests reject and which obligations remain unverified.
```

`specification-grounded-testing` freezes the authoritative requirement, maps obligations to discriminating checks, and
requires known-valid behavior to pass plus known-bad, mutated, or independently wrong behavior to fail. A
`defect-exposed` result is valid when a correct test reveals a production defect outside the requested scope.

### Optimize measured behavior

```text
The implementation is correct and green. Reduce batch lookup cost for the supplied workload, preserve first-match
semantics, and keep the change only if the same benchmark and correctness checks pass.
```

`profile-guided-optimization` fixes the workload and guardrails, records a baseline, profiles or uses deterministic cost
evidence, changes one bottleneck, and explicitly keeps or reverts the candidate. A `no-change` or `measurement-only`
result is valid when the improvement is noisy, unrepresentative, or not worth the complexity.

### Simplify after green

```text
$simplify-after-green The accepted behavior and relevant checks are green. Remove at most one unnecessary production
concept and rerun the baseline.
```

```text
$simplify-tests-after-green The suite is green. Remove or merge a test only when a mutation, known-bad replay, or exact
static equivalence proves that surviving evidence catches the same realistic fault.
```

A `no-change` result is valid.

## Jujutsu behavior

`jujutsu` is eligible for automatic activation because using Git mutation commands in an active colocated Jujutsu
workspace can target the wrong state model. Its first operation is `jj root`; it stops when that command fails.
Installed `jj` help is authoritative when the repository's reviewed 0.44 guidance differs from the local version.

Advanced material remains progressively disclosed under `skills/jujutsu/references/`.

## Validation and evaluation

Run the complete local gate:

```sh
python scripts/validate_skills.py
python scripts/eval_results.py check-cases evals/cases.jsonl
python scripts/eval_fixtures.py check
python -m unittest discover -s tests -v
```

The validator checks Agent Skills limits, discriminative positive and negative discovery metadata, cross-host invocation
alignment, Codex UI metadata, provenance fields, anti-applicability sections, script permissions, relative links, and
the initial description budget.

The evaluation catalog contains positive, negative, confusable, procedural, failure/escape, and counterfactual cases.
Five deterministic fixtures provide independent verifiers for grounded implementation, root-cause debugging,
high-precision review, specification-grounded test sensitivity, and semantics-preserving optimization. See
[`EVALS.md`](EVALS.md) for paired no-skill, skill, workflow-memory, and wrong-skill trials.

Static checks and fixture self-tests do **not** establish skill lift. Do not promote metadata from `candidate` to a
stronger status until frozen-model, frozen-harness A/B trials show positive verified marginal value without unacceptable
routing, resource, or regression cost.

## License

[MIT](LICENSE)
