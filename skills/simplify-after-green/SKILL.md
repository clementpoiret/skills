---
name: simplify-after-green
description: Simplify an already-correct code change after relevant checks are green. Remove unnecessary concepts while preserving accepted behavior, tests, interfaces, security, compatibility, concurrency, performance, and operational properties. Works with dirty Git or Jujutsu working copies; use after implementation and do not add features or redesign the system.
---

# Simplify After Green

Reduce conceptual surface only after the change has credible evidence of correctness. The goal is easier reasoning and
maintenance, not fewer lines.

## Preconditions

Before editing:

1. Identify the accepted change contract. Prefer explicit `AC-*` and `INV-*` items; otherwise state the observable
   behavior and preserved constraints you infer from the task and repository.
1. Identify the current working-copy scope. A clean tree, branch, commit, or remote is not required. Determine the
   active VCS; when a Jujutsu workspace is detected, activate the `jujutsu` skill automatically. Keep unrelated edits
   out of scope.
1. Run or confirm the most focused relevant checks and record their observed results.
1. Ensure the baseline is green enough to detect regressions in the candidate area.

Return `blocked` rather than simplify when the intended behavior is ambiguous, the baseline is failing for a relevant
reason, or meaningful regression detection is unavailable. Do not hide a functional repair inside simplification.

## What to optimize

Prefer removal of a complete unnecessary concept:

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

Reject changes that merely compress syntax, move complexity, introduce cleverness, generalize for hypothetical use, or
trade explicit behavior for convention.

## Candidate selection

Build a short list, normally no more than three candidates. For each candidate, assess:

- evidence that the concept is unnecessary;
- conceptual reduction achieved;
- strength of regression detection;
- semantic risk;
- blast radius and hidden consumers.

Prefer strong evidence and meaningful conceptual reduction with low semantic risk and blast radius. A simple text search
is not proof of non-use when reflection, registration, configuration, generated code, plugins, serialization, or
external consumers are possible.

Choose the smallest complete change. Do not combine unrelated cleanup, dependency upgrades, formatting churn, or
architectural redesign.

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

If equivalence depends on an unsupported assumption, retain the existing design or add the missing evidence before
simplifying.

## Edit and validate

1. Make one reversible conceptual change at a time.
1. Preserve public names, schemas, behavior, and test strength unless the accepted contract explicitly permits a change.
1. Run the most focused checks after each batch.
1. Inspect the current diff for accidental semantic or scope changes.
1. Revert or revise a batch immediately when equivalence is uncertain or a check regresses.
1. After all batches, rerun every baseline command and the broader repository-required checks appropriate to the risk.
1. For security, concurrency, compatibility, migration, or hot-path behavior, rerun the relevant specialized checks; do
   not infer safety or performance from code shape.

For a nontrivial or high-risk simplification, or when the user asks to use both models, invoke `cross-agent` for a fresh
read-only review. Give the peer the accepted contract, baseline evidence, and current working copy, but not a defense of
the simplification. Ask specifically for changed behavior, lost invariants, hidden consumers, weakened tests, and
complexity that was moved rather than removed. Verify every finding before acting.

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
Behavior contract: <AC/INV items or concise equivalent>
Baseline: <commands and observed results>
Simplifications:
- <concept removed and why it was unnecessary>
Behavior-preservation evidence:
- <tests, static evidence, contract checks, benchmark, or peer review>
Final validation: <commands and observed results>
Residual risk or unverified areas: <none or exact limitation>
```

Do not claim a check passed unless its result was observed. Do not use removed line count as the primary success
measure.
