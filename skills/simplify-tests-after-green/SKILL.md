---
name: simplify-tests-after-green
description: "Explicitly requested simplification of a green test suite, preserving distinct behavioral obligations, fault sensitivity, isolation, and useful diagnostics."
---

# Simplify tests after green

Reduce test maintenance cost without losing meaningful defect detection. This workflow is explicit-only; it is
not permission to delete failing tests or change production behavior.

## Establish scope and evidence

Honor the user's named scope and budget. With no narrower scope, review the repository test suite, not just
newly changed tests. Complete the agreed scope and all justified work within the budget rather than stopping
after one easy deletion.

Require a credible green baseline for the affected suite. Reuse existing checks for the exact relevant state
instead of rerunning them mechanically. Keep production code unchanged, apart from temporary mutation in a
safe disposable copy when needed as evidence.

For affected tests, identify the contract, input distinctions, realistic faults detected, execution boundary,
side effects or cleanup, timing constraints, and diagnostic value. Similar names, feature coverage, or
overlapping lines do not establish redundancy. Unit and integration tests are presumed to protect different
boundaries until evidence shows otherwise.

## Simplify with preserved obligations

Prefer clearer setup, focused helpers, and readable parameterization when they reduce maintenance without
hiding cases. Preserve isolation, deterministic behavior, lifecycle semantics, and individually identifiable
failures. Avoid abstractions that make tests harder to understand.

Before deleting tests, merging assertions, replacing snapshots, or collapsing execution boundaries, read [the
preservation checks](references/preservation.md). Name the surviving evidence for every material obligation
being removed. Historical regressions and security, concurrency, compatibility, or integration checks require
correspondingly strong evidence.

Evaluate candidates independently. Retain an unproven candidate and continue useful work elsewhere. Do not
remove a flaky test merely because it is inconvenient; flakiness needs diagnosis, not loss of its behavioral
obligation. Never substitute coverage percentages for fault-sensitivity evidence.

## Verify and conclude

Run relevant tests and any needed sensitivity checks after changes that can affect them. Reuse valid evidence
for unchanged assertions and state. A green suite alone does not establish that a deletion preserved defect
detection.

Claim a runtime improvement only from comparable measurements; otherwise describe the structural benefit
without a speed claim. If a simplification loses an obligation or diagnostic boundary, restore your own
changes or add equivalent evidence within scope.

Report the audited scope, simplifications, surviving obligations and sensitivity evidence, and consequential
retained candidates. Stop after the agreed scope is complete. No change is a valid result when no material
simplification can be justified.
