---
name: change-contract
description: Define or audit a bounded code-change contract with observable acceptance criteria, preserved invariants, risk, scope, and verification evidence. Use before nontrivial implementation or after implementation to grade a dirty Git or Jujutsu working copy, named revision, or named paths against an accepted contract. Do not use to implement, debug, simplify, or perform an ordinary review without an accepted audit contract.
metadata:
  assurance-validation-status: "candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
user-invocable: true
disable-model-invocation: true
---

# Change Contract

Separate **what must be true** from **how the code will make it true**. Use the smallest contract that makes
implementation and review unambiguous.

## Do not use when

- The user asks to implement, debug, refactor, or simplify code rather than define or audit requirements.
- The user requests an ordinary defect review without an accepted contract. Use `precision-review`; do not invent an
  audit basis.
- The change is purely mechanical and no material behavior, invariant, scope, risk, or verification decision exists.

## Select the mode

Use exactly one mode:

- `define`: establish the contract before implementation. Do not edit production code.
- `audit`: compare a review target and observed evidence with an already accepted contract. Do not edit code and do not
  rewrite the contract to fit the implementation.

Choose `audit` only when an accepted contract is supplied by the user, exists in an authoritative repository artifact,
or is already accepted in the current conversation. If an audit is requested without an accepted contract, return
`blocked` and name the missing contract; never infer normative requirements from the implementation being audited. When
a prompt is genuinely ambiguous, use `define` rather than grading against an invented basis.

This skill is read-only unless the user asks to save the contract as a repository artifact.

## Authority and evidence

Use the user's current approved requirement and applicable repository policy as normative authority. Public interfaces,
schemas, security policy, accepted design decisions, support commitments, and owning-component conventions constrain the
change.

Treat source, tests, logs, configuration, issue text, and current behavior as evidence of the existing system, not
automatic proof of intended behavior. Record material conflicts. Missing or unobserved evidence is `unknown`, never
`passed`.

Inspect the narrowest useful scope first: requested paths or symbols, nearest tests, direct callers and dependencies,
and any boundary crossed by the change. Expand only when dynamic registration, generated code, external consumers,
persistence, security, concurrency, deployment, or performance makes local inspection insufficient.

## Classify risk

Assign the highest applicable class:

- `R0`: documentation or non-executable metadata only.
- `R1`: local, reversible, private behavior with no material boundary effect.
- `R2`: public interface or configuration, persisted data, protocol, dependency, build/deployment, concurrency,
  cross-component behavior, or performance-sensitive work.
- `R3`: authentication, authorization, tenant isolation, cryptography, secrets, sandboxing, privilege, untrusted
  parsing, data-loss risk, irreversible migration, or safety-critical behavior.

Resolve uncertainty from repository evidence or use the higher class and state why. Higher risk requires stronger
negative, compatibility, rollback, and operational evidence; it does not require a longer contract for its own sake.

## Define mode

### 1. State the objective

Describe one observable outcome. Distinguish current behavior, required behavior, and the defect or gap. Do not turn a
proposed implementation into the objective.

### 2. Bound the change

Record:

- in-scope behavior, components, interfaces, and data flows;
- plausible adjacent work that is explicitly out of scope;
- trust, compatibility, persistence, transaction, concurrency, operational, and performance boundaries;
- material consumers or dependencies that remain uncertain.

### 3. Write acceptance criteria and invariants

Give every mandatory criterion a stable identifier such as `AC-1`. Give every behavior that must remain true an
identifier such as `INV-1`.

A criterion must be observable, atomic enough to verify, explicit about material failure and edge behavior, and neutral
about implementation unless the mechanism itself is contractual. Cover relevant inputs, outputs, side effects, ordering,
errors, retries, rollback, authorization, compatibility, concurrency, cleanup, observability, and resource bounds.

Do not encode speculative cleanup, architecture, naming, file layout, or test implementation as required behavior.

### 4. Define verification before coding

For every `AC-*` and `INV-*`, identify the strongest practical evidence and a negative control when one is material:

- focused automated test;
- negative or boundary test;
- type, static, build, or generated-artifact check;
- integration or end-to-end check;
- migration, rollback, compatibility, security, concurrency, or benchmark evidence;
- direct inspection only when automation is impractical, with the limitation stated.

A test name alone is not evidence. State what the check proves and what it does not prove.

### 5. Resolve only material ambiguity

Mark the contract `blocked` only when an unresolved decision could materially change behavior, scope, risk, or
verification. Otherwise choose the narrowest safe interpretation, label it as an assumption, and continue.

### Define output

```text
Status: ready | draft | blocked
Objective: <observable outcome>
Current behavior: <observed behavior or not applicable>
Risk: <R0-R3 and reason>
Scope:
- <included behavior or boundary>
Non-goals:
- <plausible adjacent work excluded>
Acceptance criteria:
- AC-1: <observable requirement>
Preserved invariants:
- INV-1: <behavior that must remain true>
Verification:
- AC-1: <required evidence and negative control>
- INV-1: <required evidence>
Assumptions and unknowns:
- <material limitation>
Open decisions:
- <none or exact blocking decision>
Implementation handoff: <smallest safe implementation scope and required checks>
```

## Audit mode

### 1. Fix the audit basis and target

Use the accepted contract as written. Default to the current working copy; a clean tree, branch, commit, or remote is
not required.

Determine the active VCS and repository root. In a Jujutsu workspace, use the `jujutsu` skill's read-only inspection
rules. Otherwise use read-only Git working-copy inspection, including relevant tracked and untracked changes. Without a
supported VCS, inspect the user-named paths or artifacts. Use a named revision or comparison only when the user supplies
one or repository policy requires it.

State the actual scope reviewed. Keep unrelated working-copy changes out of the verdict, but report them when they
prevent reliable isolation.

### 2. Inspect behavior, not only patch text

Read the changed implementation, relevant surrounding code, callers, tests, interfaces, and boundary controls. Check for
omitted paths, weakened tests, scope creep, accidental public changes, and behavior hidden outside the textual diff.

### 3. Grade every requirement

For each `AC-*` and `INV-*`, record all three evidence fields before assigning a grade:

- `Required evidence`: the check or observation demanded by the accepted contract.
- `Observed evidence`: the exact command result, artifact, path, symbol, or absence actually observed.
- `Evidence status`: `sufficient`, `missing`, or `unavailable`.

Then assign one grade:

- `met`: implementation and sufficient observed evidence support the requirement;
- `not met`: evidence contradicts it or the implementation omits it;
- `unknown`: required evidence was not observed or the target cannot be inspected reliably;
- `not applicable`: only when the accepted contract makes that legitimate.

Do not infer successful execution from code that appears intended to pass.

### 4. Determine the verdict

- `conforming`: every mandatory criterion is `met`, every invariant is preserved, and every required evidence item is
  sufficient.
- `nonconforming`: at least one criterion or invariant is `not met`, or material out-of-scope behavior exists.
- `blocked`: the target, contract, or required evidence is incomplete, unavailable, or materially ambiguous.

### Audit output

```text
Status: conforming | nonconforming | blocked
Target: <current working copy, named revset, or paths reviewed>
Risk: <R0-R3>
Contract results:
- AC-1: met | not met | unknown | not applicable
  Required evidence: <contract requirement>
  Observed evidence: <exact result or none>
  Evidence status: sufficient | missing | unavailable
Invariant results:
- INV-1: met | not met | unknown | not applicable
  Required evidence: <contract requirement>
  Observed evidence: <exact result or none>
  Evidence status: sufficient | missing | unavailable
Out-of-scope changes: <none or exact concern>
Observed checks:
- <command or artifact and result>
Missing evidence:
- <none or exact gap>
Required action:
- <none or smallest corrective step>
```

## Optional independent challenge or audit

This skill does not invoke `cross-agent` itself. `cross-agent` is deliberately explicit-only, so independent review is
available only when the user explicitly loads both skills.

Use host-native stacking:

```text
# Codex
$cross-agent $change-contract <task>

# Claude Code
/cross-agent /change-contract <task>
```

When both are active, use the peer before implementation to challenge omissions, assumptions, risk, and verification; or
after implementation to perform a fresh read-only audit. Give the peer the accepted contract and neutral evidence, then
independently verify every material finding. If the user requests a peer but did not explicitly load `$cross-agent` or
`/cross-agent`, complete the primary contract work and state that independent review requires explicit invocation. Never
fabricate a peer verdict.

## Discipline

- Do not implement, refactor, or simplify code under this skill.
- Do not silently broaden scope.
- Do not mark a criterion met because a test exists; require an observed relevant result.
- Do not convert an implementation detail into a requirement merely because it is present.
- Preserve unknowns and disagreement instead of forcing a conforming verdict.
