# Preservation checks for test reduction

Read when an edit can remove assertions, cases, snapshots, lifecycle coverage, or execution boundaries.
Ordinary readability edits need only the checks their actual effects warrant.

For every removed obligation, identify the specific surviving test or assertion and why it rejects the
relevant wrong behavior. Choose the smallest decisive evidence:

- a known-bad implementation or historical regression that the survivor rejects;
- a mutation in an isolated disposable copy, never the user's live working tree;
- an independently justified reference or direct assertion-sensitivity argument;
- exact static equivalence, including parametrization, fixtures, runner metadata, isolation, and lifecycle behavior when those can affect execution.

A passing baseline, shared feature name, or equal coverage percentage is not that evidence. An integration
test may exercise wiring, serialization, authorization, or cleanup that a unit test cannot replace. A large
snapshot may protect incidental content, but replacement assertions must retain every required behavior it
actually protects.

For parameterization, preserve distinct input boundaries, expected outcomes, and readable case identifiers.
For shared fixtures or helpers, preserve setup/teardown, failure isolation, state ownership, and relevant
timing. Never trade away a unique security or historical regression check merely to shorten the suite.

Run only the additional evidence needed for the changed obligations. If exact equivalence and valid checks
already establish preservation, do not invent mutations or repeat the same proof. If evidence cannot be
obtained safely, retain the candidate and continue independent work.
