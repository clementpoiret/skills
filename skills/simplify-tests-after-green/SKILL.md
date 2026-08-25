---
name: simplify-tests-after-green
description: Simplify a green test suite with duplicate, overlapping, slow, brittle, implementation-coupled, or low-value tests only when fault-detection evidence is preserved. Use after stable implementation by explicit invocation. Do not use while behavior is failing, to add or strengthen tests, delete flaky regressions, weaken coverage, simplify production code, or optimize product performance.
metadata:
  assurance-validation-status: "candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
user-invocable: true
disable-model-invocation: true
---

# Simplify Tests After Green

Optimize **fault-detection signal per unit of maintenance and runtime cost**. Fewer tests are valuable only when
realistic regressions remain at least as detectable and failures remain diagnosable.

Invoke this at a stable green checkpoint, normally after feature or debugging work and before final validation—not
inside a failing RED/GREEN iteration.

## Do not use when

- Relevant behavior, fixtures, or baselines are failing, flaky, or not reproducible.
- The goal is to delete an inconvenient regression, weaken fault detection, or optimize test count or coverage percentage.
- The task is production-code simplification. Use `simplify-after-green`.
- The user asks to add or strengthen tests rather than remove proven redundancy. Use
  `specification-grounded-testing`.
- The primary objective is a product or build benchmark, or runtime optimization. Use
  `profile-guided-optimization`.
- No safe discriminator can establish equivalent fault detection within the pass budget; retain the test or return
  `no-change`.

## Preconditions

Before editing tests:

1. Fix the behavioral basis. Prefer accepted `AC-*` and `INV-*` items; otherwise state the observable behaviors and
   boundaries the suite must protect.
1. Bound the target to tests created or affected by the current work and their nearest related suite. Preserve unrelated
   edits; do not require a clean tree, branch, commit, or remote.
1. Run the exact focused baseline and record the command, observed result, test count, and duration when available. Run
   a broader baseline when shared fixtures, runner configuration, or integration coverage may be affected.
1. Require a relevant green baseline. Return `blocked` when failures, unresolved flakiness, or an invalid fixture make
   regression detection unreliable.
1. Keep production behavior, public contracts, dependencies, and build policy unchanged. A functional repair is a
   separate task.

## Bound the pass

Unless the user explicitly requests broader work:

- inspect at most three removal or merge candidates;
- apply at most one conceptual batch before re-establishing the full baseline;
- stop after the first discriminator that proves the surviving evidence catches the named fault;
- use at most three narrowly scoped mutants for one candidate;
- retain the test rather than exhaust the budget when equivalence remains uncertain.

For noisy runtime claims, use the same command and environment for three to five runs and report the median plus raw
observations. Stop measuring when the claimed benefit is too small to distinguish from noise.

## Map tests to obligations

For every candidate, identify:

- the observable contract or invariant it protects;
- a realistic production change that should make it fail;
- the boundary it exercises: unit, component, integration, end-to-end, protocol, persistence, or operational;
- unique inputs, assertions, side effects, timing, cleanup, or failure diagnostics;
- its maintenance and runtime cost.

Tests at different boundaries are not duplicates merely because they cover the same feature. If no surviving test
protects an obligation, retain the candidate.

## Good candidates

Prefer bounded changes such as:

- remove exact semantic duplicates;
- merge same-path cases into a readable table with stable case names and literal, independently derived expectations;
- extract repeated setup only when important inputs and intent remain visible at each test;
- replace broad snapshots, source-text checks, mirror assertions, or mock-interaction checks with narrower observable
  behavior checks;
- consolidate repeated expensive setup only when isolation, cleanup, and order independence remain intact;
- remove a slower duplicate only when a cheaper test catches the same fault and the higher-level boundary remains
  covered;
- remove obsolete expectations only when the accepted contract proves they are no longer obligations.

Do not optimize for line count, test count, or coverage percentage. Do not create giant parameterized tests, opaque
helper DSLs, shared mutable fixtures, or failures that no longer identify the broken case.

## Reject common shortcuts

- Unchanged coverage does not prove equivalent assertions or fault classes.
- Tests for the same feature are not duplicates when they exercise different boundaries.
- Flakiness creates a debugging task; it is not deletion evidence.
- Parameterization is not an improvement when setup, obligation, or diagnostics materially differ.
- Fewer tests are not necessarily faster because runner and fixture costs may dominate.

## Proof gate for deletion or merging

Before applying each conceptual batch:

1. Name the surviving test or evidence for every protected obligation.
1. Show that the candidate contributes no unique boundary, fault class, fixture condition, assertion, or diagnostic
   value.
1. Obtain discriminating evidence using the strongest safe option in this order:
   1. existing mutation-testing results;
   1. replay of the original regression, a known-bad revision, or a known-bad fixture;
   1. a temporary mutation in an isolated workspace or temporary copy;
   1. an inline inverse-edit mutation only when the target hunk has a known exact preimage, no unrelated edit overlaps
      it, and the complete working-copy diff is captured before and after;
   1. static equivalence only for genuinely identical execution, inputs, assertions, runner metadata, and isolation.
1. For a temporary mutation, disable only the named protected behavior, confirm that the surviving test fails for the
   expected reason, restore with the exact inverse edit, and verify that the full working-copy diff matches the
   pre-mutation snapshot. Never use reset or checkout to restore a dirty working copy.
1. Run the focused suite and inspect the actual output.

Unchanged coverage is not proof of unchanged test strength. If no discriminator can be performed safely or within the
pass budget, retain the test or return `blocked` for that candidate.

## Presumptively distinct evidence

Require especially strong proof before merging or deleting tests for:

- prior production regressions or incidents;
- authentication, authorization, tenant isolation, secrecy, adversarial input, or data-loss prevention;
- persistence, migration, rollback, cleanup, idempotency, or compatibility;
- concurrency, cancellation, ordering, timing, retry, or resource bounds;
- external protocols and integration boundaries.

Do not delete a flaky test because it is inconvenient. Diagnose or stabilize it under a separate debugging scope, or
report it as a blocker.

## Edit and validate

1. Make one reversible test-concept change at a time.
1. Preserve case-level diagnostics and independently derived expected values.
1. Run the smallest relevant checks after each batch; revert or revise when fault detection or clarity becomes
   uncertain.
1. When claiming runtime improvement, compare the same command and environment. Report measurements, not an unsupported
   percentage.
1. Inspect the final diff, then rerun every baseline command and broader repository-required checks appropriate to the
   affected fixtures and boundaries.
1. Do not invoke another skill or peer automatically. Additional review is a separate explicit choice.

A `no-change` result is valid when the existing suite is already the clearest, fastest justified representation or when
redundancy cannot be proven safely.

## Quick reference

| Candidate                                  | Required evidence                                                   | Safe outcome                         |
| ------------------------------------------ | ------------------------------------------------------------------- | ------------------------------------ |
| Same path, different literal inputs        | Same obligation and boundary; independently derived expected values | Readable named table                 |
| Repeated setup                             | Inputs stay visible; no shared state or order dependency            | Narrow fixture or helper             |
| Unit and integration tests for one feature | Distinct boundary faults accounted for                              | Usually retain both                  |
| Broad snapshot or mock assertions          | Behavioral replacement catches the named fault                      | Narrower assertion                   |
| Slow duplicate                             | Cheaper survivor catches the fault; boundary remains covered        | Remove or reduce slower case         |
| Flaky regression test                      | Reliable replacement evidence                                       | Otherwise block and debug separately |

## Final report

```text
Status: optimized | no-change | blocked
Scope: <test paths, behaviors, and boundaries reviewed>
Behavioral obligations: <AC/INV items or concise equivalent>
Baseline: <commands, observed results, count, duration, and flakiness evidence>
Candidates considered: <up to three, with proof status>
Changes:
- <tests merged, removed, narrowed, or fixtures simplified and why>
Fault-detection preservation:
- <surviving test plus mutation, regression replay, static proof, or other discriminator>
Runtime and maintenance impact: <measured observations; test count is secondary>
Final validation: <commands and observed results>
Residual risk or unverified areas: <none or exact limitation>
```

Never claim the suite is stronger, equivalent, or faster without observed evidence supporting that exact claim.
