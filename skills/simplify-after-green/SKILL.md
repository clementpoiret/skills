---
name: simplify-after-green
description: Simplify green production code by removing dead or legacy code, redundant abstractions, duplication, unnecessary indirection, obsolete compatibility machinery, and other maintenance burden while preserving accepted behavior, interfaces, security, compatibility, concurrency, performance, and operational properties. Audit the whole repository unless the user specifies a narrower production-code scope. Use only after relevant checks are green and by explicit invocation. Do not use to fix failures, add behavior, redesign the system, simplify tests, or pursue measured performance optimization.
metadata:
  assurance-validation-status: "candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
  assurance-target-models: "gpt-6-astra, claude-fable-5-1"
user-invocable: true
disable-model-invocation: true
---

# Simplify After Green

Improve the quality and maintainability of an already-correct production-code scope without changing its accepted
behavior.

The objective is to remove unnecessary concepts, legacy surface, duplication, indirection, and accidental complexity so
that the codebase is easier to understand, modify, and maintain.

**Do not optimize for the smallest, easiest, or safest possible edit.**

Semantic risk, blast radius, and regression evidence are acceptance and verification constraints. They are not the
primary candidate-selection objective. Prefer the highest-value maintainability improvement that can be justified and
verified.

Follow explicit user instructions over procedural defaults within host permissions. Reuse existing authorization,
complete the requested scope, and identify the specific instruction and missing decision if this skill blocks work.

## Do not use when

- Relevant behavior or checks are failing, flaky, unobserved, or lack a credible baseline.
- The task is to add behavior, repair a defect, redesign architecture, or change an accepted contract.
- The target is test-suite simplification rather than production-code simplification. Use `simplify-tests-after-green`.
- The primary objective is measured performance or resource improvement. Use `profile-guided-optimization`.
- The requested scope cannot be identified well enough to distinguish target code from unrelated work.

## Scope

The user's requested scope is authoritative.

- If the user names files, directories, packages, modules, components, symbols, or another production-code region, audit
  that entire scope.
- If the user does not specify a narrower scope, audit the repository's production code.
- Do not restrict the audit to files touched by the current change, current diff, recent commits, or nearby code unless
  the user explicitly requests such a scope.
- The working copy matters for preserving unrelated edits, not for deciding which existing code is eligible for
  simplification.
- Do not simplify tests under this skill except where a production-code refactor requires mechanically updating tests
  while preserving their meaning and strength.

For a large scope, inspect it systematically by subsystem or component. Do not stop merely because an easy candidate has
already been found.

## Preconditions

Before editing:

1. Establish the behavioral basis.

   - Prefer accepted `AC-*` and `INV-*` items.
   - For low-risk work, a concise behavior basis inferred from the approved task and authoritative repository policy is
     acceptable when stated explicitly.
   - For changes involving sensitive contracts, compatibility, security, persistence, concurrency, or externally
     consumed interfaces, require sufficiently explicit evidence rather than inferring a convenient contract from the
     implementation.

1. Identify the working-copy state and unrelated edits.

   - A clean tree, branch, commit, or remote is not required.
   - Preserve unrelated modifications.
   - In a Jujutsu workspace, use the `jujutsu` skill for VCS mechanics when appropriate.

1. Run or confirm the most focused relevant checks and record their observed results.

1. Add broader baseline checks when shared interfaces, fixtures, generated artifacts, persistence, integration
   boundaries, or other cross-cutting behavior may be affected.

1. Require a baseline green enough to detect regressions in the areas that may be changed.

Return `blocked` rather than hide a functional repair inside simplification when intended behavior is ambiguous, a
relevant baseline is failing, or meaningful regression detection is unavailable.

## What to optimize

Search for material reductions in ongoing maintenance and conceptual burden.

High-value opportunities include:

- proven dead code, dead state, unreachable branches, abandoned modules, or unused configuration;
- legacy implementations, obsolete compatibility paths, expired migration machinery, stale feature flags, or
  transitional code whose supported lifetime has ended;
- forwarding layers that add no policy, validation, compatibility, observability, lifecycle management, ownership, or
  useful test seam;
- speculative interfaces, factories, strategies, adapters, wrappers, registries, or configuration with no supported
  need;
- duplicate control flow, duplicated domain rules, repeated transformations, or redundant representations of the same
  state;
- unnecessary conversions or synchronization between representations that can have a single clear source of truth;
- unnecessary indirection, layering, polymorphism, callbacks, delegation, or abstraction that obscures ownership and
  control flow;
- custom mechanisms already covered adequately by an existing repository-native primitive;
- obsolete dependencies or internal dependency edges that become removable as part of a justified simplification;
- impossible states, defensive branches, or guards whose enabling invariant is explicit and enforced;
- fragmented responsibilities that can be made materially clearer without creating a broader architectural redesign;
- incidental complexity accumulated through repeated feature work.

A refactor does not need to delete code to be valuable. Consolidating ownership, replacing redundant representations,
clarifying control flow, or restructuring duplicated logic can be the correct simplification when it materially lowers
future maintenance cost.

Retain complexity that represents a real obligation or boundary, including:

- authorization and tenant isolation;
- canonicalization and validation;
- transactions and atomicity;
- idempotency;
- serialization and external schemas;
- supported compatibility;
- concurrency ownership and ordering;
- cancellation and cleanup;
- backpressure and resource bounds;
- side-effect isolation;
- platform separation;
- observability;
- nondeterministic test seams;
- measured performance or resource protections.

Reject changes that merely:

- reduce line count;
- compress syntax;
- move complexity somewhere else;
- replace explicit behavior with cleverness;
- introduce generalized machinery for hypothetical future use;
- trade understandable local code for unnecessary abstraction;
- perform unrelated formatting, dependency upgrades, or cleanup.

## Audit and candidate selection

Audit the requested scope before deciding that the work is complete.

Identify material simplification and refactoring opportunities throughout that scope. Do not use an arbitrary
candidate-count limit and do not stop after finding the first acceptable change.

Rank candidates primarily by expected codebase-quality benefit:

1. obsolete or unnecessary concepts removed;
1. ongoing maintenance burden eliminated;
1. legacy surface retired;
1. duplicated logic or representations consolidated;
1. coupling or unnecessary dependency edges reduced;
1. ownership, invariants, data flow, or control flow clarified;
1. future change cost reduced;
1. incidental complexity removed.

Then determine whether each candidate can be changed safely.

Semantic risk, blast radius, and regression evidence are **feasibility constraints**, not the optimization objective.
Use them to decide whether a valuable candidate can be justified and verified.

Do not prefer a low-value cleanup merely because it is easier to prove when a materially higher-value candidate in the
requested scope can also be verified.

When candidates have comparable maintenance value, prefer the one with stronger evidence and lower semantic risk.

For every material candidate, assess:

- why the code or concept is unnecessary or unnecessarily complex;
- the maintenance or conceptual burden it creates;
- the simplification expected from changing it;
- hidden consumers and dynamic reachability;
- affected contracts and invariants;
- regression-detection strength;
- semantic risk and blast radius;
- whether the change is behavior-preserving and independently useful.

Text search alone is not proof of non-use when reflection, registration, configuration, generated code, plugins,
serialization, dynamic loading, external consumers, or convention-based discovery are possible.

A candidate that cannot be justified should be retained or reported as unresolved. It should not cause the audit to stop
if other material candidates remain.

## Change selection

Apply every material simplification in the requested scope that is justified, behavior-preserving, and verifiable,
unless the user explicitly requested a smaller budget or a single change.

Prefer coherent conceptual changes over collections of cosmetic edits.

Do not artificially constrain the pass to one concept. When several independent simplifications are justified, perform
them sequentially and validate each one.

When candidates overlap, apply the most foundational justified change first, then reassess the remaining candidates
against the simplified code.

## Equivalence check

Before editing a candidate, compare the proposed before-and-after behavior across every relevant dimension:

- inputs, outputs, side effects, and ordering;
- error type, status, timing, retry, rollback, and cleanup;
- null, empty, boundary, malformed, and adversarial inputs;
- public interfaces, serialized data, configuration, and compatibility;
- authentication, authorization, secrecy, and auditing;
- concurrency, cancellation, atomicity, resource ownership, and bounds;
- logs, metrics, traces, and operator-visible behavior;
- latency, throughput, allocation, memory, I/O, and query count on sensitive paths;
- test assertions, negative controls, generated artifacts, and build outputs.

If equivalence depends on an unsupported assumption, obtain the missing evidence or retain that behavior.

Do not downgrade a valuable candidate merely because proving it requires more investigation than proving a trivial
cleanup. Investigate enough to make a sound decision within the requested scope.

## Edit and validate

1. Make one reversible conceptual change at a time, with targeted edits to existing files where practical.
1. Preserve accepted behavior, public names, schemas, compatibility, security properties, operational properties, and
   test strength unless the accepted contract explicitly permits change.
1. Run the smallest discriminating checks after each conceptual change.
1. Inspect the resulting diff for accidental semantic or scope changes.
1. Revert or revise immediately when equivalence becomes uncertain or a relevant check regresses.
1. Reassess overlapping candidates after structural changes rather than mechanically applying a stale plan.
1. Continue auditing and simplifying until no material justified opportunity remains in the requested scope.
1. Rerun every baseline command and the broader repository-required checks appropriate to the resulting risk.
1. For security, concurrency, compatibility, migration, persistence, or hot-path behavior, rerun the relevant
   specialized checks. Never infer safety or performance from code shape alone.

## Optional independent preservation review

This skill does not invoke `cross-agent` automatically.

For a nontrivial or high-risk pass, or when the user explicitly wants both models, load both skills explicitly:

```text
# Codex
$cross-agent $simplify-after-green <task>

# Claude Code
/cross-agent /simplify-after-green <task>
```

When both are active, give the peer:

- the accepted behavior contract;
- baseline evidence;
- requested audit scope;
- current resulting diff.

Do not give the peer a defense of the chosen simplification.

Ask specifically for:

- changed behavior;
- lost invariants;
- hidden consumers;
- compatibility regressions;
- weakened tests;
- security or concurrency regressions;
- complexity that was moved rather than removed.

Verify every finding before acting.

## Completion and stop conditions

A successful pass ends when the requested scope has been audited and no additional **material, justified,
behavior-preserving simplification** remains.

Track which components and candidates have been inspected. Revisit them only when later edits or new evidence affect
their assessment. Reuse final-state verification results rather than repeating a completed pass, and honor any smaller
scope or budget the user supplied. Do not expand this pass into another subsystem after its requested scope is covered.

Return `no-change` when the scope was adequately audited but:

- the only opportunities are stylistic, cosmetic, or line-count reductions;
- existing complexity represents real obligations or useful boundaries;
- apparent duplication has distinct semantics or ownership;
- proposed refactors would merely relocate complexity;
- the current implementation is already a clear and maintainable justified representation.

Retain or report an individual candidate when:

- dynamic or external reachability remains unresolved;
- a required boundary cannot be verified;
- adequate regression evidence does not exist;
- the change would alter an unsupported public or compatibility contract;
- it would add a dependency, broaden permissions, change build policy, or introduce behavior;
- it expands into architectural redesign beyond behavior-preserving simplification.

An unresolved candidate does not terminate the entire pass unless it prevents reliable analysis or validation of the
remaining requested scope.

Return `blocked` when the audit as a whole cannot proceed safely because the behavioral basis, baseline, working-copy
isolation, or required regression detection is inadequate.

## Final report

Use the fields below as an evidence checklist. Match the user's requested format and summarize only relevant fields;
retain exact checks, material limitations, and any required per-criterion grades. Give brief progress updates during
long work, and make the final response understandable without reading tool output.

```text
Status: simplified | no-change | blocked
Scope requested: <repository or user-specified paths/modules/symbols>
Scope audited: <what was actually inspected>
Behavior contract: <AC/INV items or concise accepted basis>
Baseline: <commands and observed results>

Material candidates:
- <candidate, expected maintenance benefit, and disposition>
- ...

Simplifications:
- <concept/refactor and the maintenance or conceptual burden removed>
- ...

Behavior-preservation evidence:
- <tests, static evidence, contract checks, specialized validation, benchmark, or explicit peer review>
- ...

Retained or unresolved opportunities:
- <candidate and exact reason it was retained, or none>

Final validation: <commands and observed results>
Residual risk or unverified areas: <none or exact limitation>
```

Do not claim a check passed unless its result was observed.

Do not use removed line count, number of edits, small blast radius, or ease of proof as the primary measure of success.
The success criterion is meaningful reduction of maintenance and conceptual burden across the requested scope while
preserving accepted behavior.
