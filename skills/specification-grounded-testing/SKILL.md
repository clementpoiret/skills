---
name: specification-grounded-testing
description: Design or strengthen executable tests, conformance suites, regression oracles, or hidden verifiers from authoritative requirements rather than the current implementation. Use when the primary deliverable is test evidence for existing behavior. Do not use for production implementation or bug repair, merely running tests, read-only change review, test deletion/simplification, or performance benchmarking whose oracle is a measured workload.
compatibility: Intended for Codex and Claude Code sessions that can inspect authoritative requirements, repository tests and interfaces, edit test artifacts, and execute the project test runner or an equivalent verifier when available.
metadata:
  assurance-validation-status: "unvalidated-candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
user-invocable: true
disable-model-invocation: false
---

# Specification-Grounded Testing

Create an independent executable oracle from authoritative behavior. The current implementation and existing tests are
candidate evidence, not the source of truth.

## Applicability

Use this as the primary procedure when the user asks to add or strengthen tests, build a conformance suite, create a
hidden verifier, encode accepted requirements as executable checks, or assess test sensitivity by producing test
artifacts.

The primary deliverable must be tests or another executable verification artifact. This procedure may compose with:

- `jujutsu` for VCS mechanics when `jj root` succeeds;
- an explicitly invoked `change-contract`, whose accepted `AC-*` and `INV-*` items remain authoritative;
- an explicitly invoked `cross-agent`, which may challenge the oracle but does not define it.

Use at most one primary task-family skill. Do not also apply `grounded-implementation`,
`reproduction-first-debugging`, `precision-review`, or `profile-guided-optimization` unless the task changes family.

## Do not use when

- The user asks to implement or change production behavior. Use `grounded-implementation`.
- A reported defect must be reproduced and repaired. Use `reproduction-first-debugging`; its regression test is part of
  that repair procedure.
- The task is a read-only review of a diff, revision, or existing tests. Use `precision-review`, or explicit
  `change-contract` audit when an accepted contract exists.
- The task is only to run an existing suite or report its output; no test design is requested.
- The goal is to delete, merge, or reduce green tests. Use explicit `simplify-tests-after-green`.
- The primary oracle is latency, throughput, memory, allocation, I/O, or another measured workload. Use
  `profile-guided-optimization` for benchmark and performance-guardrail work.
- No authoritative behavior, trustworthy reference, or independently expressible invariant can be established. Report
  the oracle gap instead of freezing the current implementation as the specification.

## Invariants

Maintain these throughout the task:

- Authoritative requirements, not implementation details, define expected behavior.
- Production code remains unchanged unless the user explicitly changes the task scope.
- Every added assertion maps to a material obligation or a named failure class.
- A test that passes only the current implementation is not accepted as an independent oracle.
- Correct implementations must pass; plausible incorrect implementations should fail for the intended reason.
- Tests remain deterministic, isolated, diagnosable, and no broader than needed to expose the target behavior.
- Test count and coverage percentage are diagnostics, not acceptance criteria.

## 1. Freeze the behavioral oracle

Before editing tests, identify the strongest available authority in this order:

1. current user-approved specification or task;
2. accepted `AC-*` and `INV-*` contract;
3. public protocol, schema, interface, or versioned standard applicable to the repository;
4. independently validated reference implementation or golden data;
5. repository policy and documented compatibility commitments.

Treat source code, existing tests, examples, comments, and historical behavior as evidence that may reveal ambiguity or
compatibility constraints. Do not silently promote them above the approved requirement.

Build a compact obligation matrix:

```text
TEST-1: <authoritative requirement and source>
Valid class: <representative inputs or state>
Boundary/invalid class: <material edge or failure path>
Observable oracle: <result, exception, state transition, side effect, or invariant>
Plausible wrong behavior: <implementation defect this test should reject>
Cheapest test boundary: <unit, integration, contract, property, fuzz, runtime>
```

If two authoritative sources conflict, record the conflict. Do not encode one interpretation as a test unless the user or
repository policy resolves it. If ambiguity is itself important, write a characterization or pending test only when the
repository has an established convention for that state and label it non-normative.

## 2. Establish repository and test baselines

Before adding tests:

1. Determine repository root, active VCS, working-copy scope, and unrelated edits.
2. Locate the repository-native test runner, fixture conventions, test boundaries, generated tests, and required
   compile/type/lint commands.
3. Inspect manifests, lockfiles, and resolved versions when test APIs, protocol behavior, or framework fixtures are
   version-dependent.
4. Run the narrow existing suite and preserve the command and observed result. Distinguish existing product failures,
   flaky tests, collection failures, and environment failures.
5. Record which files are allowed to change. Default to test artifacts only.

A currently failing implementation does not authorize a production patch. If the requested test correctly exposes a
product defect, preserve that evidence and report the failing obligation unless the user explicitly broadens the task.

## 3. Inventory existing evidence and seams

Retrieve progressively:

- current tests, fixtures, helpers, and runner metadata;
- public interfaces, types, schemas, and observable side effects;
- error, cleanup, retry, persistence, compatibility, and state-transition behavior;
- callers or consumers when they define a public contract;
- known-bad revisions, historical regressions, or accepted bug fixtures;
- generated-code boundaries and test data provenance;
- trust, concurrency, protocol, or high-dimensional input boundaries when triggered.

For each obligation, classify existing evidence as:

- **protected**: a test demonstrably distinguishes correct from relevant wrong behavior;
- **executed but weak**: code runs, but assertions do not detect the target defect;
- **implementation-coupled**: the expected result mirrors internal code or mocks the behavior being tested;
- **unprotected**: no useful executable check exists;
- **unverifiable**: no trustworthy oracle or controllable environment exists.

Stop retrieval when the next test-design decision is supported. Do not read the entire repository or duplicate current
suite structure without a reason.

## 4. Select checks by failure mechanism

Choose the cheapest test form that can detect the named wrong behavior:

- **Explicit examples** → known inputs, outputs, errors, and state transitions.
- **Boundary and negative cases** → invalid input, exact limits, cleanup, partial failure, and no-effect guarantees.
- **Integration or contract tests** → serialization, persistence, filesystem, network, configuration, or component
  boundaries whose defect cannot exist in one unit.
- **Properties** → round trips, idempotence, monotonicity, conservation, ordering, equivalence, or state-machine
  invariants derived from the specification.
- **Fuzzing** → parsers, protocols, decoders, and hostile or high-dimensional input only after defining crash, rejection,
  semantic, or invariant oracles.
- **Race, sanitizer, or runtime checks** → defects requiring execution schedules, memory behavior, or runtime state.
- **Known-bad replay or mutation** → test-sensitivity validation for changed or high-risk logic.

Do not add every available test type. Escalate only when a cheaper check cannot distinguish the relevant failure.

## 5. Write the smallest discriminating tests

Implement one obligation or failure mechanism at a time:

1. Name the requirement and plausible wrong behavior the test targets.
2. Use public behavior or the narrowest stable seam. Assert internals only when the internal contract itself is
   authoritative.
3. Derive expected values independently. Do not compute the expected result by invoking the same algorithm, parser,
   serializer, or decision logic under test.
4. Preserve test isolation, cleanup, order independence, and stable case-level diagnostics.
5. Avoid timing sleeps, unrestricted randomness, live external services, mutable global fixtures, and snapshots broader
   than the obligation.
6. Run the focused test immediately and inspect why it passed or failed.

When several cases share one obligation and boundary, use a readable named table. Keep materially different boundaries or
failure mechanisms separate even when they concern the same feature.

## 6. Validate the oracle independently

A green current implementation is necessary when it is expected to be correct, but it is not sufficient. Obtain the
strongest safe discriminator available:

1. replay a known-bad revision, minimized historical defect, or accepted invalid fixture;
2. run the suite against an independently supplied incorrect implementation;
3. apply a narrowly targeted mutation in an isolated copy and restore it exactly;
4. compare with a separately validated reference implementation or golden corpus;
5. demonstrate that a property or contract check rejects a constructed counterexample.

Also require a known-valid implementation or reference artifact to pass when available. This protects against false
positive tests and implementation-shape assertions.

For every new failure, classify it before changing anything:

- **product defect** → test matches the frozen requirement; report the defect without repairing production code;
- **test defect** → oracle, setup, fixture, or isolation is wrong; repair the test;
- **specification ambiguity** → stop and identify the decision required;
- **environment failure** → repair or bound the environment before interpreting behavior;
- **non-discriminating test** → strengthen or remove the test rather than count it as coverage.

If no safe sensitivity discriminator is feasible, label the test evidence unvalidated. Do not claim that the suite would
catch plausible defects merely because it executes the target code.

## 7. Run the completion gate

Re-read the authoritative requirements, inspect the final test diff, and use actual execution evidence. Require, as
applicable:

1. Every material obligation is protected or explicitly listed as unverified.
2. The focused suite runs under the repository-native command.
3. Known-valid behavior passes.
4. Each claimed sensitivity result rejects the named wrong behavior for the intended reason.
5. Relevant compile, type, lint, fixture, package, generated-test, or broader regression checks pass.
6. Production code, dependencies, and unrelated working-copy changes remain untouched unless explicitly authorized.
7. No disabled assertion, unconditional skip, source-text fingerprint, current-output snapshot, or implementation-derived
   expected value substitutes for a behavioral oracle.
8. Residual false-positive, flakiness, environment, and oracle risks are stated precisely.

A valid outcome may be `tests-added`, `defect-exposed`, `partial`, or `blocked`. Do not force all tests green when the
explicit purpose is to expose a specification violation without changing production code.

## Failure signatures and diagnostic actions

- **Coverage rises but a targeted mutation survives** → strengthen the assertion or move to a boundary that exposes the
  behavior; do not add more similar cases.
- **The test reproduces current source logic** → replace the expected value with a requirement-derived literal, property,
  reference, or externally observable result.
- **A second correct implementation fails** → inspect implementation-shape assumptions, exact error text, ordering, or
  fixture coupling; narrow the assertion to the contract.
- **A new test fails only in the full suite** → investigate shared state, order dependence, fixture leakage, and cleanup.
- **A fuzz target generates cases but finds no semantic failures** → define a meaningful property or rejection oracle;
  input volume alone is not evidence.
- **A known-bad implementation passes** → identify the missing obligation or wrong test boundary before adding cases.
- **The current implementation fails a requirement-grounded test** → preserve the failure as a product defect; do not
  rewrite the oracle to make the implementation green.
- **Test setup dominates or requires many services** → look for a cheaper stable seam; retain the higher-level test only
  when the defect exists at that boundary.

## Escape conditions

Abandon or narrow this procedure when:

- authoritative behavior cannot be established independently of the implementation;
- the task becomes production implementation, active debugging, read-only review, or performance optimization;
- the required environment or external system cannot be controlled enough to produce reliable evidence;
- a generated or version-specific test API cannot be resolved from repository-local version evidence;
- a test would freeze an unresolved compatibility, security, data, or protocol decision;
- sensitivity validation would require unsafe mutation of a dirty working copy or destructive external state.

Return the obligations inspected, evidence obtained, exact oracle gap, and safest next action. Proceed without this skill
rather than manufacture certainty.

## Final report

```text
Status: tests-added | defect-exposed | partial | blocked
Authority: <specification, AC/INV contract, protocol, or validated reference>
Scope: <test files and allowed production scope>
Obligation matrix:
- TEST-1: <requirement> -> <test boundary and assertion> -> <sensitivity evidence>
Baseline: <commands and observed results>
Tests added or changed: <smallest discriminating set>
Oracle validation: <known-valid pass; known-bad/mutation/counterexample results>
Repository checks: <exact commands and observed results>
Production changes: none | <explicitly authorized scope>
Unverified obligations and residual false-positive/flakiness risk: <none or exact limitation>
```
