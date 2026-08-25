---
name: precision-review
description: Perform a read-only, high-precision review of a diff, pull request, commit, revision, or working copy by recovering change intent, tracing affected contracts and consumers, validating concrete failure mechanisms, and suppressing unsupported findings. Use when asked to find actionable defects without an accepted AC/INV audit contract. Do not use to implement fixes, debug a known failure, create test artifacts, optimize code, or audit against an accepted change-contract.
compatibility: Intended for Codex and Claude Code sessions with repository and diff inspection; executable checks improve finding confidence but are not always required.
metadata:
  assurance-validation-status: "unvalidated-candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
user-invocable: true
disable-model-invocation: false
---

# Precision Review

Review for defects that can be explained and supported. A valid no-findings result is better than speculative commentary.
Remain read-only unless the user separately asks to implement accepted fixes.

## Applicability

Use this as the primary procedure when the user asks to review a pull request, diff, commit, revision range, named files,
or the current working copy for correctness, regressions, security, performance, concurrency, or maintainability defects.

This procedure may compose with `jujutsu` for read-only VCS inspection. An explicitly invoked `cross-agent` may provide a
fresh peer review, but the primary validates each finding. Use explicit `change-contract` instead when the user supplies
an accepted `AC-*`/`INV-*` contract and requests a compliance verdict.

## Do not use when

- The task is to implement or modify code. Use `grounded-implementation` or `reproduction-first-debugging` according to
  the primary objective.
- A specific failure must be reproduced and repaired. Use `reproduction-first-debugging`.
- The user asks to create or strengthen executable tests or a hidden verifier. Use
  `specification-grounded-testing`.
- The user asks to change already-correct code to improve a measured performance outcome. Use
  `profile-guided-optimization`.
- The user requests a formal audit against an accepted change contract. Use explicit `change-contract` audit mode.
- The request is an unbounded repository-wide security scan, architecture assessment, or dependency audit rather than a
  change review.
- No review target can be established and no relevant changed artifact is available. Report the missing target rather
  than reviewing arbitrary code.

## Invariants

- Keep the review target and comparison basis fixed.
- Recover intent from authoritative task/specification evidence before using implementation behavior as the oracle.
- Inspect affected context beyond the diff when contracts or consumers cross file boundaries.
- Report only findings with a concrete failure mechanism, trigger, consequence, and supporting evidence.
- Separate correctness defects from optional design preferences and unrelated pre-existing issues.
- Do not edit the target, weaken tests, or generate findings to fill a quota.

## 1. Fix the target and intent

Identify the exact target: current working copy, supplied patch, pull request, commit, revision range, or named paths. State
the actual comparison base. Include relevant untracked files and preserve unrelated dirty changes in scope accounting.

Recover change intent in this order:

1. current user-approved request or authoritative issue/specification;
2. accepted design or contract artifacts and repository policy;
3. public interfaces, schemas, compatibility promises, and tests;
4. change description and commit history as supporting context;
5. implementation behavior only as evidence of the current system.

If intent is materially ambiguous, state the narrowest review assumption. Do not invent requirements from the patch.

## 2. Inspect the diff before broad context

Read the complete diff and classify each changed region by behavioral effect:

- contract or interface change;
- state transition, error path, cleanup, or side effect;
- dependency, configuration, generated artifact, or build change;
- security, concurrency, persistence, deployment, or performance boundary;
- test/oracle change;
- mechanical or documentation-only change.

Inspect surrounding code only as needed to determine semantics. Whole-file or repository dumps are not a substitute for
focused context.

## 3. Build the affected-evidence map

For each behavior-changing region, inspect the narrowest relevant set:

- definitions, interfaces, types, and invariants;
- direct callers, consumers, implementers, and overridden behavior;
- sibling implementations and repository conventions;
- tests that should fail if the changed behavior is wrong;
- manifests, lockfiles, resolved versions, local types, or vendored source for dependency/API claims;
- generated-code sources and regeneration commands;
- data, protocol, deployment, trust, concurrency, and performance boundaries reached by the patch.

Apply these observation-dependent rules:

- **Public API, schema, or persisted representation changed** → inventory consumers, mixed old/new behavior, migration,
  rollback, and compatibility evidence.
- **Dependency or tool behavior assumed** → establish the actual resolved version before judging API validity.
- **Authentication, authorization, secrets, tenant data, untrusted input, parser/protocol, or privilege changed** → state
  the security property and inspect all paths crossing the trust boundary.
- **Shared state, async lifecycle, locking, cancellation, or retries changed** → inspect ownership, ordering, atomicity,
  cleanup, and schedule-dependent failure paths.
- **Hot path or resource behavior changed** → require a plausible workload and mechanism; do not report performance
  regressions from intuition alone.
- **Generated output changed** → confirm the source and reproducible regeneration path rather than reviewing the artifact
  in isolation.

Stop retrieving when each suspected issue can be validated or rejected.

## 4. Recover changed contracts and invariants

State what the patch changes and what must remain true. Pay particular attention to:

- preconditions, postconditions, errors, and invalid inputs;
- boundary values, empty states, partial failure, retry, and cleanup;
- compatibility with direct and indirect consumers;
- authorization-before-effect, tenant isolation, secrecy, and input constraints;
- ownership, ordering, atomicity, cancellation, and resource lifetime;
- persisted data, idempotency, migration, and rollback;
- performance or resource budgets only when specified or evidenced.

Do not treat a new test as authoritative if it merely repeats the patch's mistaken interpretation. Trace tests back to the
approved behavior or independent invariant.

## 5. Validate suspected defects

For each suspicion, write the causal claim before deciding whether to report it:

```text
Location: <changed line or smallest affected region>
Mechanism: <how the code reaches an invalid state or result>
Trigger: <specific input, state, ordering, version, or consumer>
Consequence: <observable incorrect behavior or risk>
Evidence: <source, contract, caller, test, command, or direct execution>
Falsifier: <observation that would make this not a defect>
```

Then obtain the cheapest useful validation:

- inspect a caller, interface, or versioned local source;
- run a focused existing test or static/type/build check;
- construct a safe minimal reproduction;
- compare old/new behavior against the authoritative requirement;
- trace the state transition or schedule;
- reject the finding when its trigger is impossible under established invariants.

Do not report:

- style, naming, or personal design preference without a concrete maintenance or correctness consequence;
- a theoretical possibility with no reachable trigger;
- missing tests as a defect unless a material behavior is unverified and the review request includes test adequacy;
- a pre-existing issue unrelated to the target, except as clearly separated context when it blocks review;
- a claim contradicted by repository version, type, caller, or execution evidence;
- duplicate manifestations of one root cause as several findings.

## 6. Review verification and patch quality

Inspect whether the patch's evidence actually distinguishes correct from incorrect behavior:

- requirements or invariants map to tests or other checks;
- material negative, error, compatibility, security, concurrency, or migration paths are covered when triggered;
- assertions observe behavior rather than implementation trivia;
- tests were not weakened, skipped, over-mocked, or changed to accept the bug;
- compile/type/lint/build/package results are observed when relevant;
- visible tests are not the sole basis for a broad correctness claim.

Also inspect patch scope:

- smallest coherent change for the intent;
- no unrelated cleanup or speculative abstraction;
- no unjustified dependency or accidental public surface;
- established architecture and generated-code boundaries preserved;
- unusual complexity or coupling has a requirement-backed reason.

## 7. Calibrate and report

Rank only supported findings. Use severity based on consequence and reach, not rhetorical urgency:

- `critical`: likely severe security, data-loss, safety, or broad availability failure;
- `high`: deterministic correctness or compatibility failure in a material supported path;
- `medium`: bounded but real failure requiring a specific trigger;
- `low`: real maintainability or diagnostic defect with a concrete future-change cost.

Every finding must include:

- concise title and severity;
- exact affected location;
- failure mechanism;
- trigger/precondition;
- consequence;
- supporting evidence;
- a verification or reproduction path when feasible;
- uncertainty that materially limits confidence.

Order findings by severity, then confidence. Do not add a summary finding that duplicates detailed findings. If no
supported findings remain, say so and list the evidence inspected and any unverified area.

## Failure signatures and diagnostic actions

- **A finding depends on an unknown framework version** → inspect manifest, lockfile, local types, or resolved source;
  suppress it if the version cannot be established.
- **The diff looks wrong but callers enforce the precondition** → verify all relevant callers and public reachability;
  reject the finding when the invariant is complete.
- **A test passes but mirrors the implementation** → recover the independent requirement or invariant before crediting
  the test.
- **Many findings share one mechanism** → collapse them into one root-cause finding with affected locations.
- **Review context keeps expanding without a concrete claim** → return to changed contracts and stop unrelated codebase
  exploration.
- **A suspected security/performance/concurrency issue lacks a trigger** → run the relevant branch-specific check or
  suppress the claim.
- **The target contains unrelated dirty changes** → isolate the requested region and report scope limitations; do not
  attribute unrelated defects to the patch.

## Escape conditions

Return `blocked` or a limited review rather than speculative findings when:

- the comparison base or changed target cannot be established;
- authoritative intent is missing and different plausible interpretations reverse the verdict;
- generated or dependency artifacts cannot be tied to their source/version;
- required environment, data, or permissions make a material suspicion unverifiable;
- the request is actually a contract audit, implementation, debugging task, or repository-wide specialist assessment.

State what was inspected, what could not be established, and the next evidence needed.

## Report

```text
Target: <diff/revision/working copy and comparison basis>
Intent basis: <task/specification/repository contract>
Findings:
- [severity] <title>
  Location: <path:line or changed region>
  Mechanism: <exact failure mechanism>
  Trigger: <precondition/input/state/version/order>
  Consequence: <observable effect>
  Evidence: <source or execution evidence>
  Verification: <reproduction/check or not feasible>
  Uncertainty: <none or exact limitation>
Evidence inspected: <diff, contracts, callers, tests, versions, checks>
No-finding statement: <when applicable>
Unverified areas: <none or exact limitation>
```
