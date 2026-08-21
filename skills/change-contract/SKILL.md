---
name: change-contract
description: Define or audit a bounded code-change contract with observable acceptance criteria, preserved invariants, risk, scope, and verification evidence. Use before nontrivial implementation or after implementation to check a dirty Git or Jujutsu working copy, named revision, or named paths against an accepted contract. Do not use to implement or simplify code.
---

# Change Contract

Separate **what must be true** from **how the code will make it true**. Use the smallest contract that makes
implementation and review unambiguous.

## Modes

Infer the mode from the task:

- `define`: establish the contract before implementation. Do not edit production code.
- `audit`: compare the current review target and observed evidence with an accepted contract. Do not edit code or
  rewrite the contract to fit the implementation.

This skill is read-only unless the user asks to save the contract as a repository artifact.

## Authority and evidence

Use the user’s current approved requirement and applicable repository policy as normative authority. Public interfaces,
schemas, security policy, accepted design decisions, support commitments, and owning-component conventions constrain the
change.

Treat source, tests, logs, configuration, and current behavior as evidence of the existing system, not automatic proof
of intended behavior. Record material conflicts. A missing check or unobserved result is unknown, not passed.

Inspect the narrowest useful scope first: the requested paths or symbols, their nearest tests, direct callers and
dependencies, and any boundary the change crosses. Expand only when dynamic registration, generated code, external
consumers, persistence, security, concurrency, deployment, or performance makes local inspection insufficient.

## Risk

Assign the highest applicable class:

- `R0`: documentation or non-executable metadata only.
- `R1`: local, reversible, private behavior with no material boundary effect.
- `R2`: public interface or configuration, persisted data, protocol, dependency, build/deployment, concurrency,
  cross-component behavior, or performance-sensitive work.
- `R3`: authentication, authorization, tenant isolation, cryptography, secrets, sandboxing, privilege, untrusted
  parsing, data-loss risk, irreversible migration, or safety-critical behavior.

When uncertain, resolve the uncertainty from repository evidence or use the higher class and state why. Higher risk
requires stronger negative, compatibility, rollback, and operational evidence; it does not require a longer contract for
its own sake.

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

A good criterion is observable, atomic enough to verify, explicit about failure or edge behavior when material, and
neutral about implementation unless the implementation mechanism is itself a contract. Cover relevant inputs, outputs,
side effects, ordering, errors, retries, rollback, authorization, compatibility, concurrency, cleanup, observability,
and resource bounds.

Do not encode speculative cleanup, architecture, naming, file layout, or test implementation as required behavior.

### 4. Define verification before coding

For each `AC-*` and `INV-*`, identify the strongest practical evidence:

- focused automated test;
- negative or boundary test;
- type, static, build, or generated-artifact check;
- integration or end-to-end check;
- migration, rollback, compatibility, security, concurrency, or benchmark evidence;
- direct inspection only when automation is impractical, with the limitation stated.

A test name alone is not evidence. State what it proves and what it does not prove.

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
- AC-1: <evidence and negative control>
- INV-1: <evidence>
Assumptions and unknowns:
- <material limitation>
Open decisions:
- <none or exact blocking decision>
Implementation handoff: <smallest safe implementation scope and required checks>
```

## Audit mode

### 1. Fix the audit basis

Use the accepted contract as written. Default to the current working copy; a clean tree, branch, commit, or remote is
not required.

Determine the active VCS and repository root. If a Jujutsu workspace is detected, activate the `jujutsu` skill
automatically and use its read-only inspection rules. Otherwise use read-only Git working-copy inspection, including
relevant tracked and untracked changes. Without a supported VCS, inspect the paths or artifacts named by the user. Use a
named revision or comparison only when the user supplies one or repository policy requires it.

State the actual scope reviewed. Keep unrelated working-copy changes out of the verdict, but report them when they
prevent reliable isolation.

### 2. Inspect behavior, not only patch text

Read the changed implementation, relevant surrounding code, callers, tests, interfaces, and boundary controls. Check for
omitted paths, weakened tests, scope creep, accidental public changes, and behavior hidden outside the textual diff.

### 3. Grade every requirement

For each `AC-*` and `INV-*`, use one grade:

- `met`: the implementation and observed evidence support it;
- `not met`: evidence contradicts it or the implementation omits it;
- `unknown`: the required evidence was not observed or the target cannot be inspected reliably;
- `not applicable`: only when the accepted contract makes that legitimate.

Cite the relevant path, symbol, test, command result, or artifact. Do not infer successful execution from code that
appears intended to pass.

### 4. Determine the verdict

- `conforming`: every mandatory criterion is met, every invariant is preserved, and all required evidence was observed.
- `nonconforming`: at least one criterion or invariant is not met, or the implementation contains material out-of-scope
  behavior.
- `blocked`: the target, contract, or required evidence is incomplete or materially ambiguous.

### Audit output

```text
Status: conforming | nonconforming | blocked
Target: <current working copy, named revset, or paths reviewed>
Risk: <R0-R3>
Contract results:
- AC-1: met | not met | unknown | not applicable — <evidence>
Invariant results:
- INV-1: met | not met | unknown | not applicable — <evidence>
Out-of-scope changes: <none or exact concern>
Observed checks:
- <command or artifact and result>
Missing evidence:
- <none or exact gap>
Required action:
- <none or smallest corrective step>
```

## Independent challenge or audit

When the user asks to involve the other model, or the surrounding workflow explicitly calls for independent review, use
the `cross-agent` skill:

- before implementation, ask the peer to challenge omissions, unsupported assumptions, risk classification, and
  verification quality;
- after implementation, give the peer the accepted contract and current working copy, and ask it to audit behavior and
  evidence;
- do not give the peer a persuasive implementation narrative unless the task is specifically to critique that narrative;
- verify and reconcile the peer’s findings before changing the contract or reporting a verdict.
