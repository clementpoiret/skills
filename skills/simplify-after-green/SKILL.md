---
name: simplify-after-green
description: Simplify an already-correct code change after relevant checks are green. Remove unnecessary concepts while preserving accepted behavior, tests, interfaces, security, compatibility, concurrency, performance, and operational properties. Works with dirty Git or Jujutsu working copies; use after implementation and do not add features or redesign the system.
user-invocable: true
disable-model-invocation: true
---

# Simplify After Green

Reduce conceptual surface only after the change has credible evidence of correctness. The goal is easier reasoning and
maintenance, not fewer lines.

## Preconditions

Before editing:

1. Fix the behavioral basis. Prefer accepted `AC-*` and `INV-*` items. For `R0` or `R1`, a concise behavior basis
   inferred from the approved task and authoritative repository policy is acceptable when it is stated explicitly. For
   `R2` or `R3`, require an explicit accepted contract; otherwise return `blocked` rather than infer a convenient one
   from the implementation.
1. Identify the working-copy scope and unrelated edits. A clean tree, branch, commit, or remote is not required. In a
   Jujutsu workspace, use the `jujutsu` skill for VCS mechanics.
1. Run or confirm the most focused relevant checks and record their observed results. Add a broader baseline when shared
   fixtures, interfaces, generated artifacts, or integration boundaries may be affected.
1. Require a baseline green enough to detect regressions in the candidate area.

Return `blocked` rather than simplify when intended behavior is ambiguous, a relevant baseline is failing, the review
target cannot be isolated, or meaningful regression detection is unavailable. Do not hide a functional repair inside
simplification.

## What to optimize

Prefer removal of one complete unnecessary concept:

- proven dead code or state;
- a forwarding layer that adds no policy, validation, compatibility, observability, lifecycle, or test seam;
- speculative interfaces, factories, strategies, or configuration with no supported need;
- duplicate control flow or redundant representations;
- an avoidable dependency or custom mechanism already covered by a repository-native primitive;
- impossible states or guards whose enabling invariant is explicit and enforced.

Retain complexity that represents a real boundary or obligation, including authorization, tenant isolation,
canonicalization, transactions, idempotency, serialization, compatibility, concurrency ownership, cancellation, cleanup,
backpressure, side-effect isolation, platform separation, observability, nondeterministic test seams, or measured
resource protection.

Reject changes that merely compress syntax, relocate complexity, introduce cleverness, generalize for hypothetical use,
or trade explicit behavior for convention.

## Bound the search

Unless the user explicitly requests a broader pass:

1. inspect no more than three plausible candidates;
1. choose at most one conceptual removal for the pass;
1. stop exploring once one candidate has strong evidence, meaningful conceptual reduction, low semantic risk, and a
   bounded blast radius;
1. return `no-change` rather than spend unbounded time proving weak candidates.

For every candidate, assess evidence of non-necessity, conceptual reduction, regression-detection strength, semantic
risk, blast radius, and hidden consumers. Text search alone is not proof of non-use when reflection, registration,
configuration, generated code, plugins, serialization, or external consumers are possible.

Do not combine unrelated cleanup, dependency upgrades, formatting churn, or architectural redesign.

## Equivalence check

Before editing, compare the proposed before-and-after behavior across relevant dimensions:

- inputs, outputs, side effects, and ordering;
- error type, status, timing, retry, rollback, and cleanup;
- null, empty, boundary, malformed, and adversarial inputs;
- public interfaces, serialized data, configuration, and compatibility;
- authentication, authorization, secrecy, and auditing;
- concurrency, cancellation, atomicity, resource ownership, and bounds;
- logs, metrics, traces, and operator-visible behavior;
- latency, throughput, allocation, memory, I/O, and query count on sensitive paths;
- test assertions, negative controls, generated artifacts, and build outputs.

If equivalence depends on an unsupported assumption, retain the design or obtain the missing evidence before editing.

## Edit and validate

1. Make one reversible conceptual change at a time.
1. Preserve public names, schemas, behavior, and test strength unless the accepted contract explicitly permits change.
1. Run the smallest discriminating checks after the edit.
1. Inspect the current diff for accidental semantic or scope changes.
1. Revert or revise immediately when equivalence is uncertain or a check regresses.
1. Rerun every baseline command and the broader repository-required checks appropriate to the risk.
1. For security, concurrency, compatibility, migration, or hot-path behavior, rerun specialized checks; never infer
   safety or performance from code shape.

## Optional independent preservation review

This skill does not invoke `cross-agent` itself. `cross-agent` is deliberately explicit-only. For a nontrivial or
high-risk pass, or when the user wants both models, load both skills explicitly:

```text
# Codex
$cross-agent $simplify-after-green <task>

# Claude Code
/cross-agent /simplify-after-green <task>
```

When both are active, give the peer the accepted contract, baseline evidence, and current target without defending the
simplification. Ask for changed behavior, lost invariants, hidden consumers, weakened tests, and complexity that was
moved rather than removed. Verify every finding before acting. If the user asks for a peer without explicitly loading
`$cross-agent` or `/cross-agent`, continue the primary-only pass and report that no independent peer review was run.

## Stop conditions

Return `no-change` or `blocked` when:

- the only benefit is line count, novelty, or stylistic preference;
- dynamic or external reachability remains unresolved;
- the change crosses a boundary that cannot be verified;
- adequate tests or other regression evidence do not exist;
- simplification would add a dependency, broaden permissions, alter build policy, or introduce a feature;
- the candidate expands into an architectural redesign;
- the current implementation is already the clearest justified representation.

## Final report

```text
Status: simplified | no-change | blocked
Scope: <paths, symbols, or current diff reviewed>
Risk and contract basis: <R0-R3; AC/INV items or concise accepted basis>
Baseline: <commands and observed results>
Candidates considered: <up to three, with disposition>
Simplification:
- <concept removed and why it was unnecessary>
Behavior-preservation evidence:
- <tests, static evidence, contract checks, benchmark, or explicit peer review>
Final validation: <commands and observed results>
Residual risk or unverified areas: <none or exact limitation>
```

Do not claim a check passed unless its result was observed. Do not use removed line count as the primary success
measure.
