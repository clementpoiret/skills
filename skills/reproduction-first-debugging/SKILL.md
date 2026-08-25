---
name: reproduction-first-debugging
description: Use when diagnosing and fixing a reported bug, failing test, runtime exception, regression, flaky behavior, or incorrect output: reproduce before editing, test competing hypotheses with discriminating experiments, patch the root cause minimally, and prove the fix. Do not use for greenfield feature implementation, read-only review, known mechanical edits, test-only verification, or general optimization of already-correct behavior.
compatibility: Intended for Codex and Claude Code sessions that can inspect the repository and run at least the failing or nearest relevant command when available.
metadata:
  assurance-validation-status: "unvalidated-candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
user-invocable: true
disable-model-invocation: false
---

# Reproduction-First Debugging

Convert a failure report into observations before changing production code. Debug through falsifiable hypotheses, not a
sequence of plausible patches.

## Applicability

Use this as the primary procedure for a failing test, exception, crash, wrong result, regression, intermittent failure,
production symptom with obtainable evidence, or a measurable performance regression.

This procedure may compose with `jujutsu` for VCS mechanics. An explicitly invoked `change-contract` may supply the
accepted behavioral basis, and an explicitly invoked `cross-agent` may supply an independent hypothesis. The primary
agent still reproduces, discriminates, patches, and verifies.

## Do not use when

- The task is to add new behavior or refactor a working system without a reported failure. Use
  `grounded-implementation`.
- The task is a read-only review of a diff or revision. Use `precision-review`.
- The primary deliverable is a test suite or independent verifier rather than a product repair. Use
  `specification-grounded-testing`.
- The requested change and exact location are mechanically specified and no diagnosis is required.
- The user asks to improve the measured performance of behavior already accepted as correct, without a reported
  regression. Use `profile-guided-optimization`. This debugging procedure still owns a reproducible slowdown or
  performance regression.
- The environment cannot expose the failure or any useful proxy and the cause cannot be established from authoritative
  evidence. Return an investigation limitation instead of guessing.

## Invariants

- Preserve the original failure command, input, environment, and output as the regression oracle.
- Change one causal variable at a time during diagnosis.
- Distinguish observations from hypotheses and predictions.
- Reject a hypothesis when it stops explaining the evidence; do not keep patching around it.
- Patch the root cause at the narrowest responsible boundary and preserve unrelated behavior and working-copy edits.
- Completion requires the original reproduction to pass plus relevant regression evidence.

## 1. Capture the failure state

Before editing, record:

- exact failing command, request, input, seed, timestamp, or user sequence;
- complete assertion, exception, log, stack, exit status, or measured regression;
- repository revision and working-copy scope, including unrelated edits;
- runtime, dependency, configuration, environment, and service state relevant to the symptom;
- expected behavior and its authority: approved task, accepted contract, interface, protocol, or repository policy.

Do not summarize away the discriminating details. Preserve a small artifact, command transcript, failing test, or fixture
that can be rerun.

## 2. Reproduce before modifying

Run the original failure under the closest available environment. Confirm that it fails for the reported reason, not a
setup error or unrelated baseline failure.

Apply observation-dependent branches:

- **Reproduction succeeds** → preserve the exact result and continue.
- **Reproduction fails differently** → fix or isolate the environment mismatch before diagnosing production code.
- **Reproduction does not fail** → compare versions, configuration, data, timing, seed, locale, timezone, concurrency,
  and external state; add narrowly scoped instrumentation or a deterministic probe.
- **Failure is intermittent** → preserve seeds and timing, run bounded repeated trials, and compare good versus bad
  executions; do not treat one passing rerun as a fix.
- **Production-only symptom** → create the safest local or staging proxy and identify what remains unlike production.

If no useful reproduction or proxy can be established, switch to investigation-only: report observed evidence,
instrumentation needed, and uncertainty. Do not make a speculative behavior patch.

## 3. Minimize and localize

Minimize only when it increases diagnostic precision. Reduce the input, command, test scope, service topology, or event
sequence while preserving the same failure mechanism.

Build a compact evidence map:

- first failing boundary and last known-good boundary;
- relevant definitions, callers, consumers, interfaces, and tests;
- recent or adjacent changes when available;
- resolved dependency/runtime versions when behavior may be version-specific;
- state transitions, side effects, persistence, retries, cleanup, and external calls;
- for nondeterminism, shared state, ownership, ordering, synchronization, cancellation, and lifecycle.

Use progressive retrieval. Stop once the next experiment can discriminate among candidate causes.

## 4. Form competing hypotheses

Unless one cause is already deterministic from direct evidence, write at least two plausible hypotheses. For each, state:

```text
H1: <candidate mechanism>
Explains: <observations accounted for>
Predicts: <new observation if true>
Falsified by: <specific contrary evidence>
Cheapest experiment: <read-only probe or reversible change>
```

Rank hypotheses by explanatory power and experiment cost, not by familiarity. A source line that looks suspicious is not
itself a causal explanation.

## 5. Run the cheapest discriminating experiment

Prefer read-only probes, focused tests, logging, tracing, debugger inspection, state capture, or configuration comparison.
Use a temporary code change only when it is reversible and isolates one variable.

After each experiment:

- **Prediction observed** → strengthen the hypothesis and test the remaining causal link.
- **Prediction contradicted** → reject or revise the hypothesis; restore temporary changes.
- **Result non-discriminating** → choose a different experiment rather than interpreting ambiguity as support.
- **New boundary discovered** → re-localize before editing more code.

Do not change several plausible causes and rerun. Do not weaken the failing test, suppress the exception, add retries, or
increase timeouts unless evidence identifies that behavior as the root cause and the resulting semantics are required.

## 6. Use triggered diagnostic branches

Apply only the branch supported by the symptom:

- **Dependency or API behavior** → establish manifest and resolved version; inspect local usage, types, or source; consult
  upstream documentation only for that version when necessary.
- **Concurrency or lifecycle** → map ownership, ordering, atomicity, lock order, cancellation, and cleanup; use race,
  deadlock, or schedule tooling where the ecosystem supports it; a large number of passing runs is not proof.
- **Performance regression** → define the representative workload and metric, establish baseline and variance, profile,
  change one measured bottleneck, rerun the benchmark, verify correctness, and keep or revert based on observed effects.
- **Security-sensitive failure** → state the violated property and attacker-controlled precondition; preserve a safe
  reproducer, inspect every path crossing the trust boundary, and verify both exploit and legitimate behavior.
- **Parser, protocol, or high-dimensional input** → derive invariants or properties from the specification; minimize a
  useful counterexample and convert it into a regression test.

Do not expand a local bug fix into an unbounded concurrency, performance, or security audit.

## 7. Patch the root cause minimally

Patch only after evidence connects the responsible mechanism to the failure. Prefer the earliest boundary that can enforce
the required invariant without duplicating checks across callers.

Before accepting the patch, confirm:

- it explains why the original failure occurred;
- it does not merely hide the symptom or special-case the visible fixture;
- it preserves existing public, compatibility, cleanup, security, and concurrency behavior;
- it introduces no unrelated refactor, dependency, or broad defensive change;
- the diff remains small enough to attribute the observed result to the causal change.

If two production patches fail to improve the original reproduction, stop. Restore speculative edits, discard the current
hypothesis set, and re-localize from the preserved failure evidence.

## 8. Add or strengthen regression evidence

Create the cheapest stable check that fails on the original defect and passes on the fix. Derive its oracle from the
approved behavior, not from the patched implementation.

Prefer, in order of fit:

- the minimized failing test or input;
- a focused unit/component regression at the responsible boundary;
- an integration/contract test when the defect exists only across components;
- a property or minimized fuzz counterexample for invariant-rich input spaces;
- a race, sanitizer, benchmark, or runtime probe for schedule-, memory-, or performance-dependent defects.

Confirm the regression test fails on the defective state when safely feasible. Do not require destructive rollback in a
dirty working copy; use a temporary copy, isolated workspace, known-bad revision, or exact inverse edit.

## 9. Verify the repair

Run in this order:

1. the original reproduction with the same relevant environment and input;
2. the new or strengthened regression check;
3. focused tests for the responsible component and direct consumers;
4. relevant compile, type, lint, static, sanitizer, race, package, or benchmark checks;
5. broader regression checks proportional to interface reach and risk;
6. final diff inspection for scope, disabled checks, weakened assertions, and unrelated edits.

A passing new test is insufficient if the original reproduction was not rerun. A passing original case is insufficient if
adjacent valid behavior regressed.

## Failure signatures and diagnostic actions

- **Cannot reproduce the reported failure** → compare environment and state; add instrumentation; do not patch from the
  report alone.
- **Failure message changes after setup** → separate environment failure from product failure and re-establish baseline.
- **Hypothesis requires explaining away a contrary observation** → reject it and generate a competing mechanism.
- **Several files change before any experiment discriminates causes** → restore speculative edits and return to
  localization.
- **A timeout or retry makes the test green** → verify the timing or retry contract and root cause; otherwise treat it as
  symptom suppression.
- **Visible case passes but nearby boundary cases fail** → the patch is overfit; derive the invariant and repair the
  responsible boundary.
- **Repeated intermittent runs are all green** → report reduced evidence, not proof; preserve the seed/instrumentation and
  run the appropriate concurrency or stress tool.
- **Profile does not show the assumed bottleneck** → abandon the optimization hypothesis and re-profile.

## Escape conditions

Abandon or broaden the procedure when:

- the original symptom is shown to be expected behavior under the authoritative contract;
- the failure belongs to environment, infrastructure, corrupted fixture, or verifier logic rather than the product;
- local evidence contradicts the assumed dependency version or architecture;
- the minimized reproduction no longer exhibits the same mechanism;
- required production state cannot be obtained safely;
- fixing the root cause requires an unapproved compatibility, migration, security, or behavior decision.

Return the preserved reproduction, rejected hypotheses, remaining uncertainty, and the next discriminating observation
needed. Do not force a patch.

## Final report

```text
Status: fixed | investigation-only | blocked
Original reproduction: <exact command/input and observed failure>
Behavioral authority: <specification, contract, or interface>
Root cause: <mechanism and supporting evidence>
Rejected hypotheses: <candidate -> falsifying observation>
Patch: <smallest causal change>
Regression evidence: <pre-fix failure when observed and post-fix result>
Validation:
- <original reproduction and result>
- <targeted and broader checks and results>
Residual uncertainty: <none or exact limitation>
```
