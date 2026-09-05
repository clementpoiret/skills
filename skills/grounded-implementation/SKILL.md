---
name: grounded-implementation
description: Implement a nontrivial feature, behavior change, or refactor in an existing repository by grounding requirements in local contracts, locating the change surface before editing, making the smallest coherent patch, and verifying every obligation. Use for implementation work whose primary task is not diagnosing a reported failure. Do not use for bug debugging, read-only review, test-only verification, optimization of already-correct behavior, contract-only planning, trivial mechanical edits, or post-green simplification.
compatibility: Intended for Codex and Claude Code sessions with repository read/search/edit tools and executable project checks when available.
metadata:
  assurance-validation-status: "unvalidated-candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
  assurance-target-models: "gpt-6-astra, claude-fable-5-1"
user-invocable: true
disable-model-invocation: false
---

# Grounded Implementation

Implement from authoritative requirements and repository-local truth. Treat code, tests, remembered framework behavior,
and generated assumptions as evidence to inspect, not as the requirement oracle.

Follow explicit user instructions over procedural defaults within host permissions. Reuse existing authorization,
complete the requested scope, and identify the specific instruction and missing decision if this skill blocks work.

## Applicability

Use this as the primary procedure when the user asks to add or change nontrivial behavior, perform a behavior-preserving
refactor with a defined objective, or implement an accepted contract in an existing repository.

This procedure may compose with:

- `jujutsu` for VCS mechanics when `jj root` succeeds;
- an explicitly invoked `change-contract`, whose accepted `AC-*` and `INV-*` items remain authoritative;
- an explicitly invoked `cross-agent`, which supplies independent evidence but does not own the patch.

Use at most one primary task-family skill. Do not also apply `reproduction-first-debugging`, `precision-review`,
`specification-grounded-testing`, or `profile-guided-optimization` unless the task actually changes family.

## Do not use when

- The primary objective is to reproduce and fix a reported failure, failing test, exception, regression, or flaky
  behavior. Use `reproduction-first-debugging`.
- The user requests a read-only review of a diff, commit, pull request, or working copy. Use `precision-review`, or
  explicit `change-contract` audit when an accepted contract exists.
- The user asks only to define or audit requirements, not to implement them. Use explicit `change-contract`.
- The primary deliverable is tests, a conformance suite, or an independent verifier without production behavior
  changes. Use `specification-grounded-testing`.
- The primary objective is to optimize measured performance or resource use of behavior already accepted as correct.
  Use `profile-guided-optimization`. A new feature with a performance constraint remains an implementation task.
- The requested edit is purely mechanical and has no meaningful behavioral, interface, dependency, build, or generated
  artifact consequence.
- The change is already correct and green and the objective is optional simplification. Use the relevant explicit
  simplification skill.
- Required repository evidence or execution tools are unavailable and no safe implementation decision can be made.
  State the blocker and proceed without this procedure rather than invent local facts.

## Invariants

Maintain these throughout the task:

- The original approved requirement remains the oracle; the implementation does not redefine it.
- Unrelated working-copy changes remain intact.
- Every consequential assumption is supported by repository evidence, an authoritative specification, or an explicitly
  labeled unresolved assumption.
- The patch remains the smallest coherent change that satisfies the obligations.
- No speculative abstraction, dependency, cleanup, or compatibility break is bundled into the behavior change.
- Completion requires observed verification evidence, not confidence or plausible code shape.

## 1. Fix the behavioral basis

Before significant editing, extract a compact obligation ledger from the current approved task, accepted contract, and
applicable repository policy.

Record, as applicable:

- required behavior and explicit non-goals;
- preconditions, postconditions, and preserved invariants;
- error, invalid-input, cleanup, retry, and partial-failure behavior;
- public interface, persistence, protocol, deployment, and backward-compatibility constraints;
- security, concurrency, performance, and resource constraints only when the task crosses those boundaries;
- an observable acceptance check for every material obligation.

Use this traceability form:

```text
REQ-1: <authoritative obligation>
Implementation implication: <constraint on the change, not a chosen design unless required>
Verification: <observable check and expected result>
```

If an accepted `AC-*`/`INV-*` contract exists, use it unchanged and map directly to it. If sources conflict, prefer the
current user-approved requirement and applicable repository policy, record the conflict, and do not silently use current
implementation behavior as the tie-breaker.

Reuse decisions and authorization already established by the user. If an unresolved choice could materially
change public behavior, compatibility, security, data, or verification, pause only the dependent work and report the
decision needed after completing independent obligations. Otherwise choose the narrowest reversible interpretation.

## 2. Establish the repository baseline

Inspect before editing:

1. Determine repository root, active VCS, working-copy scope, and unrelated edits.
2. Find the repository-native build, test, lint, type, package, and generated-code commands relevant to the target.
3. Run the cheapest useful baseline when practical. Distinguish pre-existing failures from failures caused by the task.
4. Preserve exact command, environment, and output for any baseline used later as evidence.

A missing or failing broad suite does not automatically block a narrow change. It does require isolating the relevant
baseline and explicitly limiting the final claim.

## 3. Build a compact local-truth map

Retrieve progressively. Start with the named behavior or likely symbol, then inspect only evidence needed for the next
decision:

- definitions and direct callers or consumers;
- interfaces, types, schemas, and public contracts;
- nearest tests and fixtures, including negative and compatibility cases;
- sibling implementations and established repository patterns;
- build/configuration files and generated-code boundaries;
- dependency manifests, lockfiles, resolved versions, local types, or vendored source when external behavior matters;
- persistence, deployment, trust, concurrency, or performance boundaries when the change reaches them.

Apply these observation-dependent rules:

- **Version-dependent API or behavior** → inspect manifest and resolved/locked version first; inspect local usage, types,
  or source next; consult upstream documentation only for that established version when local evidence is insufficient.
- **Generated file** → locate and edit the generator or source definition; regenerate with the repository command.
- **Public interface, schema, or persisted data** → inventory consumers and compatibility/migration constraints before
  changing the producer.
- **Dynamic registration, reflection, configuration loading, or plugins** → do not use text search alone as proof of
  reachability or non-use.
- **Security boundary** → state the property to preserve, such as authorization before effect, tenant isolation, secret
  non-disclosure, or safe parsing; inspect every path that can violate it.
- **Concurrency boundary** → state ownership, ordering, atomicity, cancellation, and lifecycle invariants before editing.

Stop retrieving when the evidence supports the next implementation decision. Do not dump whole files or repository
history merely because they are available.

Batch independent file reads and searches when the host supports it. Resolve missing paths and versions before commands
that depend on them; serialize edits and checks that share mutable state.

## 4. Choose the smallest coherent design

Map each obligation to the narrowest change surface and verification method. Prefer existing architecture, naming,
error models, and dependency patterns. Introduce a new abstraction or dependency only when the obligation cannot be met
more simply and repository evidence supports the choice.

Before editing, reject a plan that:

- changes behavior outside the obligation ledger;
- breaks a consumer without an accepted migration or compatibility plan;
- edits generated output directly;
- duplicates an existing mechanism without evidence that reuse is unsafe;
- expands the patch primarily to clean up unrelated code;
- makes the verification oracle depend on the same unverified implementation assumption.

If the required change surface grows materially beyond the evidence map, stop, inspect the newly affected boundary, and
revise the plan. Do not continue by accretion.

## 5. Implement transactionally

1. Make one coherent conceptual batch at a time, using targeted edits when most of a file stays unchanged.
2. Inspect the diff immediately after each batch and remove accidental scope.
3. Run the cheapest discriminating check after each meaningful edit: parser/formatter, compile/type check, focused test,
   or a direct runtime probe appropriate to the failure mode.
4. When a check contradicts the design assumption, revert or revise that assumption before adding another patch.
5. Preserve repository-native error handling, observability, and cleanup behavior unless the requirement changes them.

Add tests from the authoritative obligation ledger, not by copying the implementation. Prefer the cheapest test level
that can reproduce the behavior and fail for the intended reason. Add negative or boundary cases when omission would
leave a material requirement unverified.

Extend suitable existing tests. Keep temporary exploration probes out of the committed suite unless they protect a
required behavior or satisfy repository conventions. Do not add adjacent features or fix unrelated baseline defects.

## 6. Run the completion gate

Separate final verification from generation. Re-read the original task or accepted contract, then inspect the final diff
and actual execution evidence without relying on the implementation narrative.

Require, as applicable:

1. Every `REQ-*` or accepted `AC-*`/`INV-*` item has an observed result or is explicitly unverified.
2. The requested behavior is exercised by a focused check, including material error or edge paths.
3. Relevant compile, type, lint, static, generated-artifact, package, or build checks pass.
4. Relevant regression tests pass, with breadth increased for shared interfaces, persistence, security, concurrency,
   deployment, or high change radius.
5. Dependency and version claims match the actual resolved repository state.
6. The final diff is coherent, contains no unrelated cleanup, and preserves unrelated working-copy edits.
7. No visible-test workaround, weakened assertion, disabled check, or implementation-derived oracle substitutes for the
   requirement.

Use the cheapest discriminating checks during iteration. Run broader acceptance and regression checks once the patch is
stable. Do not mechanically run every tool when it cannot distinguish a relevant failure.

Reuse observed results for the same final code and environment. Once the required gates pass, repeat or broaden checks
only for a new edit, failure, or concrete unresolved risk; then finish the requested deliverable.

Success requires observable evidence. When a required check cannot run, report `partial` or `blocked`; do not say the
implementation is complete merely because the code appears correct.

## Failure signatures and diagnostic actions

- **A test passes but no obligation maps to it** → return to the obligation ledger; identify the missing oracle.
- **An external API is remembered but the repository version is unknown** → inspect manifest, lockfile, local types, or
  installed source before using it.
- **A symbol appears unused but registration may be dynamic** → inspect configuration, registries, generated indexes, and
  runtime wiring; retain it if reachability remains unresolved.
- **The same check fails after two patches or the diff keeps growing** → stop patching, revert speculative edits, and
  re-localize the contract and change surface.
- **A baseline failure is unrelated** → isolate the relevant check and record the limitation; do not repair unrelated
  failures inside this task.
- **A generated artifact changes unexpectedly** → identify the generator inputs and regeneration command before
  accepting the diff.
- **A new dependency seems convenient** → prove existing mechanisms are insufficient, establish compatible resolved
  versions, and include package/build verification; otherwise do not add it.

## Escape conditions

Abandon or narrow this procedure when:

- new evidence shows the task is primarily a bug diagnosis, test-oracle task, review, migration rehearsal, or
  optimization of already-correct behavior;
- the authoritative requirement cannot be established well enough to define acceptance;
- environment or permissions prevent inspecting the relevant source or running the minimum useful verifier;
- local evidence contradicts the assumed framework, version, architecture, or generated-code model;
- the patch cannot remain coherent without an unapproved compatibility, data, security, or scope decision.

Leaving this procedure does not cancel the task. Complete all independent authorized work, then report the evidence
obtained and the exact blocked obligation. Do not force a nominal implementation result.

## Final report

Use the fields below as an evidence checklist. Match the user's requested format and summarize only relevant fields;
retain exact checks, material limitations, and any required per-criterion grades. Give brief progress updates during
long work, and make the final response understandable without reading tool output.

```text
Status: complete | partial | blocked
Behavioral basis: <REQ/AC/INV items and authority>
Repository evidence: <symbols, callers, contracts, tests, versions, and boundaries inspected>
Change: <smallest coherent implementation summary>
Traceability:
- REQ-1: <implementation implication> -> <observed verification>
Checks:
- <exact command or verifier and observed result>
Diff review: <scope, unrelated edits preserved, generated/dependency effects>
Unverified or residual risk: <none or exact limitation>
```
