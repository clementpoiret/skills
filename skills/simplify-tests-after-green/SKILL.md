---
name: simplify-tests-after-green
description: Simplify a green test suite by removing obsolete or redundant tests, reducing brittle implementation coupling, consolidating unnecessary setup and infrastructure, and improving fault-detection signal relative to maintenance and runtime cost. Audit the whole repository test suite unless the user specifies a narrower test scope. Use only after relevant behavior is stable and green and by explicit invocation. Do not use to fix failing behavior, weaken regression protection, simplify production code, or optimize product performance.
metadata:
  assurance-validation-status: "candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
  assurance-target-models: "gpt-6-astra, claude-fable-5-1"
user-invocable: true
disable-model-invocation: true
---

# Simplify Tests After Green

Improve the maintainability, clarity, diagnostic quality, and efficiency of an already-green test suite while preserving
the behavioral obligations it protects.

Optimize **fault-detection value relative to maintenance, brittleness, and runtime cost**.

Fewer tests are not inherently better. A smaller or simpler suite is valuable only when meaningful regression detection
and useful diagnostics are preserved.

**Do not optimize for the easiest or safest test to delete.**

Proof difficulty, semantic risk, and ease of mutation are acceptance constraints. They are not the candidate-selection
objective. Prefer the highest-value test-suite improvement that can be justified and verified.

Follow explicit user instructions over procedural defaults within host permissions. Reuse existing authorization,
complete the requested scope, and identify the specific instruction and missing decision if this skill blocks work.

## Do not use when

- Relevant product behavior, fixtures, or baselines are failing, flaky, or not reproducible.
- The goal is to delete inconvenient regressions or weaken fault detection.
- The task is production-code simplification. Use `simplify-after-green`.
- The user asks primarily to add or strengthen missing tests. Use `specification-grounded-testing`.
- The primary objective is product or build performance optimization rather than test-suite quality.
- The requested test scope cannot be identified reliably.

## Scope

The user's requested scope is authoritative.

- If the user names test files, directories, packages, modules, components, behaviors, or suites, audit that entire
  scope.
- If the user does not specify a narrower scope, audit the repository's test suite.
- Do not restrict the audit to tests created or changed by the current work.
- Do not restrict the audit to the nearest related suite merely because that is where recent edits occurred.
- Preserve unrelated working-copy changes, but do not treat the current diff as the universe of eligible simplification.
- Keep production behavior and production code unchanged except for temporary, safely reversible discriminating
  mutations used to prove fault detection.

For a large suite, inspect it systematically by package, subsystem, boundary, fixture family, or test layer. Do not stop
because one easy duplicate has already been found.

## Preconditions

Before editing tests:

1. Establish the behavioral basis.

   - Prefer accepted `AC-*` and `INV-*` items.
   - Otherwise state the observable behaviors, boundaries, and invariants that the requested suite must protect.

1. Identify the requested test scope and current working-copy state.

   - A clean tree, branch, commit, or remote is not required.
   - Preserve unrelated edits.

1. Run the appropriate focused baseline and record:

   - command;
   - observed result;
   - test count when available;
   - duration when relevant;
   - any observed flakiness.

1. Run a broader baseline when shared fixtures, runner configuration, generated artifacts, integration coverage, or test
   infrastructure may be affected.

1. Require a relevant green baseline.

1. Keep production behavior, public contracts, dependencies, and build policy unchanged. Functional repair is a separate
   task.

Return `blocked` when failures, unresolved flakiness, invalid fixtures, or insufficient regression evidence make the
requested audit unreliable.

## What to optimize

Search for material test-suite maintenance and quality improvements, including:

- obsolete tests protecting behavior that is no longer part of the accepted contract;
- semantic duplicates that protect the same obligation, boundary, fault class, inputs, and diagnostic information;
- large groups of overlapping cases whose distinct intent can be expressed more clearly and cheaply;
- broad snapshots whose maintenance burden materially exceeds their useful fault-detection value;
- source-text tests, mirror assertions, or implementation-coupled assertions that unnecessarily encode internal
  structure;
- mock-interaction tests that protect incidental call shape rather than observable behavior;
- duplicated or overly elaborate fixture construction;
- expensive repeated setup that can be consolidated without compromising isolation;
- obsolete helpers, fixtures, factories, builders, DSLs, fake services, or other test infrastructure;
- unnecessary indirection in test helpers that obscures important inputs or expected behavior;
- historical test scaffolding left behind after migrations or architectural transitions;
- redundant high-level tests whose unique boundary behavior is already protected elsewhere;
- unnecessarily slow duplicate tests when cheaper surviving evidence detects the same realistic faults;
- brittle parameterization or abstraction that makes failures harder to interpret;
- fragmented test organization that obscures which obligations are actually protected.

A test refactor may add or rewrite assertions when necessary to replace brittle or redundant evidence with clearer
behavioral evidence. The goal is preservation or improvement of useful fault detection, not preservation of the existing
test implementation.

Do not optimize for:

- line count;
- raw test count;
- coverage percentage;
- ease of deletion;
- ease of proving a trivial duplicate.

Do not create:

- giant parameterized tests with unrelated cases;
- opaque helper DSLs;
- shared mutable fixtures;
- abstractions that hide the inputs responsible for behavior;
- failure output that no longer identifies the broken case.

## Audit and candidate selection

Audit the requested scope before deciding the pass is complete.

Identify material test-suite liabilities throughout that scope. Do not impose an arbitrary maximum number of candidates
and do not stop after the first test whose removal is easy to prove.

Rank candidates primarily by expected test-suite quality benefit:

1. obsolete test obligations or infrastructure removed;
1. maintenance burden reduced;
1. brittle implementation coupling eliminated;
1. semantic duplication removed;
1. fixture and setup complexity reduced;
1. expensive redundant execution removed;
1. diagnostics or readability improved;
1. ownership of behavioral obligations clarified.

Then determine whether each candidate preserves sufficient fault-detection evidence.

Proof difficulty, mutation convenience, semantic risk, and blast radius are **verification constraints**, not the
primary ranking criteria.

Do not delete an insignificant exact duplicate and stop merely because it is easy to prove redundant when a materially
more valuable simplification elsewhere in the requested scope can also be justified.

When candidates provide comparable maintenance value, prefer stronger evidence, lower semantic risk, and clearer
diagnostics.

A candidate that cannot be proven redundant or safely refactored should be retained or reported. Continue auditing the
rest of the requested scope.

## Map tests to obligations

For every material removal, merge, replacement, or infrastructure candidate, identify as applicable:

- the observable contract or invariant it protects;
- a realistic production defect that should make the evidence fail;
- the boundary exercised:
  - unit;
  - component;
  - integration;
  - end-to-end;
  - protocol;
  - persistence;
  - operational;
- unique inputs;
- unique assertions;
- side effects;
- timing behavior;
- cleanup behavior;
- fixture conditions;
- failure diagnostics;
- maintenance cost;
- runtime cost when relevant.

Tests covering the same feature are not duplicates merely because their names or assertions overlap.

Tests at different boundaries are presumptively distinct until the fault classes they contribute have been accounted
for.

If removing or merging a candidate would leave an accepted obligation without surviving evidence, retain it or replace
the evidence before removal.

## High-value candidate patterns

Useful transformations include:

- delete proven obsolete tests and their now-unused fixtures or helpers;
- remove exact semantic duplicates;
- merge genuinely same-path cases into readable named parameterization with independently derived expectations;
- consolidate repeated setup when important inputs remain visible and isolation remains intact;
- simplify or eliminate test helpers that obscure rather than clarify intent;
- remove unused fixtures, builders, factories, test utilities, and compatibility scaffolding;
- replace broad snapshots with focused observable-behavior assertions when the narrower assertions preserve the relevant
  fault classes;
- replace source-text or implementation-shape assertions with observable behavioral checks;
- replace mock-interaction assertions with behavioral evidence when interaction shape is not itself the contract;
- consolidate repeated expensive setup while preserving cleanup, isolation, and order independence;
- remove slower duplicate evidence when cheaper surviving tests catch the same realistic defect and the distinct
  higher-level boundary remains adequately covered;
- reorganize or refactor tests when doing so materially reduces maintenance cost and clarifies protected obligations.

Parameterization is beneficial only when cases actually share setup, obligation, and failure interpretation.

Do not preserve test infrastructure merely because tests currently depend on it. If the infrastructure itself is legacy
or unnecessary, consider the infrastructure and its consumers together as a simplification candidate.

## Common false evidence

Do not treat any of the following as sufficient proof by itself:

| Claim                                 | Required response                                                                      |
| ------------------------------------- | -------------------------------------------------------------------------------------- |
| Coverage is unchanged                 | Coverage does not prove assertion, boundary, or fault-class equivalence.               |
| They test the same feature            | Compare obligations, boundaries, and realistic faults rather than feature labels.      |
| The test is flaky                     | Flakiness is a debugging problem, not deletion evidence.                               |
| Parameterization is shorter           | Verify that setup, obligation, readability, and diagnostics remain coherent.           |
| Fewer tests must be faster            | Measure when runtime improvement is claimed; runner and fixture overhead may dominate. |
| This one is easiest to remove         | Ease of removal is not a quality criterion.                                            |
| The exact duplicate is obviously safe | Remove it if useful, but continue auditing for more material opportunities.            |

## Proof gate for deletion, merging, or replacement

Before applying each conceptual test change:

1. Name the surviving test or evidence for every protected obligation affected by the candidate.

1. Determine whether the candidate contributes unique:

   - boundary coverage;
   - fault class;
   - fixture condition;
   - input partition;
   - assertion;
   - side-effect observation;
   - timing behavior;
   - cleanup behavior;
   - diagnostic value.

1. Obtain discriminating evidence using the strongest safe option available:

   1. existing mutation-testing results;
   1. replay of the original regression, known-bad revision, or known-bad fixture;
   1. a temporary narrowly scoped production mutation in an isolated workspace or temporary copy;
   1. an inline inverse-edit mutation only when the exact target hunk and restoration are reliably controlled and
      unrelated edits are protected;
   1. static equivalence only for genuinely identical execution, inputs, assertions, runner metadata, isolation, and
      relevant boundary behavior.

1. For a temporary mutation:

   - disable only the named protected behavior;
   - verify that the intended surviving evidence fails for the expected reason;
   - restore the exact original state;
   - verify that the working-copy diff matches the pre-mutation state.

1. Run the focused suite and inspect the actual output after the test change.

Unchanged coverage is not proof of unchanged test strength.

If a candidate cannot be proved safely, retain that candidate or report it as unresolved. Do not terminate the whole
simplification pass unless the same evidence problem makes the remaining requested scope unreliable.

## Presumptively distinct evidence

Require especially strong proof before merging, replacing, or deleting evidence associated with:

- prior production regressions or incidents;
- authentication or authorization;
- tenant isolation;
- secrecy or adversarial input;
- data-loss prevention;
- persistence;
- migration or rollback;
- cleanup;
- idempotency;
- compatibility;
- concurrency;
- cancellation;
- ordering or timing;
- retry behavior;
- resource bounds;
- external protocols;
- integration boundaries.

Do not delete a flaky regression test merely because it is inconvenient.

Diagnose or stabilize flakiness under a separate debugging scope, or retain the test and report the issue.

## Change selection

Apply every material test-suite simplification in the requested scope that has adequate fault-detection evidence and
produces a clearer or cheaper justified suite, unless the user explicitly requests a narrower budget.

Do not constrain the pass to one removal or one conceptual batch.

Make changes sequentially so their effect remains attributable:

1. apply one coherent conceptual change;
1. validate it;
1. remove newly dead test infrastructure where justified;
1. reassess overlapping candidates;
1. continue through the requested scope.

Prefer coherent reductions of a maintenance liability over isolated cosmetic edits.

## Edit and validate

1. Make one reversible test-concept change at a time.
1. Preserve case-level diagnostics and independently derived expected values.
1. Keep important test inputs and protected behavior visible.
1. Run the smallest discriminating checks after each conceptual change.
1. Revert or revise when fault detection, isolation, behavior, or clarity becomes uncertain.
1. Remove test helpers or infrastructure made dead by a justified simplification when they have no other consumers.
1. Continue until no material justified simplification remains in the requested scope.
1. Inspect the final diff for unintended production or behavioral changes.
1. Rerun every baseline command and broader repository-required checks appropriate to affected fixtures and boundaries.
1. Do not invoke another skill or peer automatically. Additional review is a separate explicit choice.

When claiming runtime improvement, compare the same command and environment. For noisy measurements, use repeated
observations and report representative values rather than unsupported percentages.

## Completion and stop conditions

A successful pass ends when the requested scope has been audited and no additional **material, justified
simplification** remains.

Track inspected suites and candidate dispositions so a long session can resume without restarting the audit. Reuse
fault-detection evidence while its relevant code, tests, fixtures, and environment remain unchanged. Once the scope and
required final checks are covered, deliver the result; further mutation trials need a concrete unresolved fault class.

Return `no-change` when:

- the requested suite is already a clear and maintainable representation of its behavioral obligations;
- apparent duplication protects distinct boundaries or realistic fault classes;
- consolidation would materially harm diagnostics or readability;
- runtime or maintenance benefits are negligible;
- the only remaining opportunities optimize test count, line count, or aesthetics.

Retain or report an individual candidate when:

- equivalent fault detection cannot be established;
- a safe discriminator cannot be performed;
- the candidate protects a unique obligation or boundary;
- unrelated working-copy edits prevent safe mutation or restoration;
- simplification would require changing production behavior or an accepted contract.

An unresolved candidate does not terminate the full audit unless the underlying baseline or fixture problems invalidate
analysis of the remaining scope.

Return `blocked` when the audit as a whole cannot proceed reliably because the baseline, behavioral obligations,
fixtures, or regression-detection mechanisms are inadequate.

## Final report

Use the fields below as an evidence checklist. Match the user's requested format and summarize only relevant fields;
retain exact checks, material limitations, and any required per-criterion grades. Give brief progress updates during
long work, and make the final response understandable without reading tool output.

```text
Status: optimized | no-change | blocked
Scope requested: <repository test suite or user-specified scope>
Scope audited: <test paths, suites, behaviors, and boundaries inspected>
Behavioral obligations: <AC/INV items or concise equivalent>
Baseline: <commands, observed results, counts, duration, and flakiness evidence>

Material candidates:
- <candidate, expected maintenance/runtime benefit, and disposition>
- ...

Changes:
- <tests merged, removed, replaced, reorganized, or narrowed and why>
- <fixtures/helpers/infrastructure removed or simplified and why>
- ...

Fault-detection preservation:
- <surviving evidence plus mutation, regression replay, static proof, or other discriminator>
- ...

Runtime and maintenance impact:
- <observed evidence; test count is secondary>

Retained or unresolved opportunities:
- <candidate and exact reason it was retained, or none>

Final validation: <commands and observed results>
Residual risk or unverified areas: <none or exact limitation>
```

Never claim that the resulting suite is equivalent, stronger, clearer, or faster without evidence supporting the
relevant claim.

Do not use test count, ease of deletion, low semantic risk, or ease of proof as the primary success measure. The success
criterion is meaningful reduction of test-suite maintenance burden and unnecessary complexity across the requested scope
while preserving the behavioral evidence that matters.
