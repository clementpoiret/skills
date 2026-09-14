---
name: specification-grounded-testing
description: "Create or strengthen tests or hidden verifiers from an independent specification; not merely running tests, fixing production code, or deleting redundant tests."
---

# Specification-grounded testing

Produce tests whose oracle comes from the required behavior, not from the implementation being tested. Keep
production changes outside this task unless separately authorized.

## Establish the oracle

Use an explicit specification, accepted requirements, documented contract, or an independently justified
reference. Freeze the relevant obligations before studying implementation details that could bias expected
results. Current output, snapshots, and coverage are not independent specifications.

Map each material obligation to valid and invalid inputs, expected observations, and a plausible wrong
implementation it should reject. Keep this mapping as small as the task allows. Cover externally meaningful
outputs, errors, state changes, and isolation or cleanup where specified; avoid asserting incidental internal
structure.

When a requirement is ambiguous, separate the unresolved obligation and request the needed decision. Continue
independent unambiguous tests. With no independent oracle, report the missing basis rather than canonizing
current behavior.

## Write discriminating tests

Use the project's runner and conventions. Derive expected results independently; do not call the same
production helper on both sides of an assertion. Prefer representative boundaries and realistic
counterexamples over many examples with identical fault sensitivity.

Use property-based or fuzz testing only with a stated invariant, meaningful input domain, and interpretable
failure. Keep randomness reproducible and reduce failures without losing their cause. For hidden verifiers,
check behavior rather than known filenames, superficial implementation patterns, or hardcoded visible examples
unless the contract explicitly requires them.

Establish that correct behavior passes and plausible incorrect behavior fails. Use an appropriate known-bad
case, independent reference, safe isolated mutation, or direct assertion-sensitivity argument; exhaustive
mutation is not mandatory. Never mutate the user's working implementation in place merely to test a test.
Reuse relevant existing sensitivity evidence for unchanged assertions.

## Classify the outcome

Distinguish a product defect, a faulty test, an ambiguous specification, and an environment failure. A correct
new test that exposes a production defect is a valid `defect-exposed` deliverable. Preserve that test and
report the defect; do not silently repair production code or weaken the oracle to obtain green.

Finish the requested test artifacts and independent obligations. Report their specification basis, meaningful
fault sensitivity, checks performed, and unresolved limits. Coverage alone is not evidence of correctness.
Stop when the requested obligations are tested with adequate evidence, not after maximizing test count.
