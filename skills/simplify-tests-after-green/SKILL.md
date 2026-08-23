---
name: simplify-tests-after-green
description: Use when a green test suite has accumulated duplicate, overlapping, slow, brittle, implementation-coupled, or low-value tests after TDD, debugging, or repeated feature work. Do not use while relevant behavior is failing or when the goal is to weaken regression coverage.
user-invocable: true
disable-model-invocation: true
---
# Simplify Tests After Green

Optimize **fault-detection signal per unit of maintenance and runtime cost**. Fewer tests are valuable only when realistic
regressions remain at least as detectable and failures remain diagnosable.

Invoke this at a stable green checkpoint, normally after feature or debugging work and before final validation—not inside
a failing RED/GREEN iteration.

## Preconditions

Before editing tests:

1. Fix the behavioral basis. Prefer accepted `AC-*` and `INV-*` items; otherwise state the observable behaviors and
   boundaries the suite must protect.
2. Bound the target to the tests created or affected by the current work and their nearest related suite. Preserve
   unrelated edits; do not require a clean tree, branch, commit, or remote.
3. Run the exact focused baseline and record the command, observed result, test count, and duration when available. Run a
   broader baseline when the proposed change could affect shared fixtures, runner configuration, or integration coverage.
4. Require a relevant green baseline. Return `blocked` when failures, unresolved flakiness, or an invalid fixture make
   regression detection unreliable.
5. Keep production behavior, public contracts, dependencies, and build policy unchanged. A functional repair is a
   separate task.

## Map tests to obligations

For every removal or merge candidate, identify:

- the observable contract or invariant it protects;
- a realistic production change that should make it fail;
- the boundary it exercises: unit, component, integration, end-to-end, protocol, persistence, or operational;
- unique inputs, assertions, side effects, timing, cleanup, or failure diagnostics;
- its maintenance and runtime cost.

Tests at different boundaries are not duplicates merely because they cover the same feature. If no surviving test protects
an obligation, retain the candidate.

## Good candidates

Prefer bounded changes such as:

- remove exact semantic duplicates;
- merge same-path cases into a readable table with stable case names and literal, independently derived expectations;
- extract repeated setup only when important inputs and intent remain visible at each test;
- replace broad snapshots, source-text checks, mirror assertions, or mock-interaction checks with narrower observable
  behavior checks;
- consolidate repeated expensive setup only when isolation, cleanup, and order independence remain intact;
- remove a slower duplicate only when a cheaper test catches the same fault and the higher-level boundary remains covered;
- remove obsolete expectations only when the accepted contract proves they are no longer obligations.

Do not optimize for line count, test count, or coverage percentage. Do not create giant parameterized tests, opaque helper
DSLs, shared mutable fixtures, or failures that no longer identify the broken case.

## Quick reference

| Candidate | Required evidence | Safe outcome |
| --- | --- | --- |
| Same path, different literal inputs | Same obligation and boundary; independent expected values | Readable parameterized cases |
| Repeated setup | Inputs stay visible; no shared state or order dependency | Narrow fixture/helper extraction |
| Unit and integration tests for one feature | Distinct boundary faults accounted for | Usually retain both |
| Broad snapshot or mock assertions | Observable contract replacement catches the same fault | Narrower behavioral assertion |
| Slow duplicate | Cheaper survivor catches the fault; high-level boundary still covered | Remove or reduce slower case |
| Flaky regression test | Reliable replacement evidence | Otherwise block and debug separately |

Example: four unit tests for empty, blank, malformed, and overlong values may become a named table with literal expected
errors. Keep a separate HTTP authorization-denial test because it can catch routing, middleware, serialization, and
policy-wiring failures that the validation table cannot.

## Common rationalizations

| Claim | Required response |
| --- | --- |
| “Coverage is unchanged.” | Coverage does not prove assertion or fault-class equivalence. Run a discriminator. |
| “They test the same feature.” | Compare boundaries and realistic mutations, not feature labels. |
| “The flaky test makes CI unreliable.” | Flakiness creates a debugging task; it is not deletion evidence. |
| “Parameterization is always cleaner.” | Retain separate cases when setup, obligation, or diagnostics materially differ. |
| “Fewer tests must be faster.” | Measure the same command; runner and fixture costs may dominate. |

## Proof gate for deletion or merging

Before applying each conceptual batch:

1. Name the surviving test or evidence for every protected obligation.
2. Show that the candidate contributes no unique boundary, fault class, fixture condition, assertion, or diagnostic value.
3. Obtain discriminating evidence using the strongest safe option:
   - existing mutation-testing results;
   - a temporary, narrowly scoped mutation that disables the protected production behavior and makes the surviving test
     fail for the expected reason;
   - replay of the original regression or a known-bad fixture;
   - static equivalence only for genuinely identical execution, inputs, assertions, runner metadata, and isolation.
4. Restore every temporary mutation with an inverse edit, never a reset or checkout, and verify the working-copy diff
   matches the pre-mutation baseline.
5. Run the focused suite and inspect the actual output.

Unchanged coverage is not proof of unchanged test strength. If a discriminating check cannot be performed safely around
unrelated edits, retain the test or return `blocked` for that candidate.

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

1. Make one reversible test concept change at a time.
2. Preserve case-level diagnostics and independently derived expected values.
3. Run the smallest relevant checks after each batch; revert or revise when fault detection or clarity becomes uncertain.
4. When claiming runtime improvement, compare the same command and environment. Use repeated runs and a median when noise
   is material; report raw observations rather than an unsupported percentage.
5. Inspect the final diff, then rerun every baseline command and the broader repository-required checks appropriate to the
   affected fixtures and boundaries.
6. Do not invoke another skill or peer automatically. Additional review is a separate explicit choice.

A `no-change` result is valid when the existing suite is already the clearest, fastest justified representation or when
redundancy cannot be proven safely.

## Final report

```text
Status: optimized | no-change | blocked
Scope: <test paths, behaviors, and boundaries reviewed>
Behavioral obligations: <AC/INV items or concise equivalent>
Baseline: <commands, observed results, count, duration, and flakiness evidence>
Changes:
- <tests merged, removed, narrowed, or fixtures simplified and why>
Fault-detection preservation:
- <surviving test plus mutation, regression replay, static proof, or other discriminator>
Runtime and maintenance impact: <measured observations; test count is secondary>
Final validation: <commands and observed results>
Residual risk or unverified areas: <none or exact limitation>
```

Never claim the suite is stronger, equivalent, or faster without observed evidence supporting that exact claim.
