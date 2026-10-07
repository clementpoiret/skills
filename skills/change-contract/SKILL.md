---
name: change-contract
description: "Explicitly requested change-contract definition or audit: define acceptance criteria and invariants, or assess a target against an already accepted contract."
disable-model-invocation: true
---

# Change contract

Produce a contract or a contract-conformance assessment, not implementation. This workflow is explicit-only
and does not automatically invoke a peer or another skill.

## Select one mode

For **define**, read [the definition workflow](references/define.md). Use it when the user requests a contract
or when invocation is ambiguous and no accepted contract exists.

For **audit**, read [the audit workflow](references/audit.md). Use it when the user requests conformance
assessment against an accepted contract. An explicit audit without that basis is blocked; do not quietly
switch to defining a contract from the implementation.

Keep accepted requirements distinct from proposed assumptions. Existing code and passing tests describe the
target; they cannot retroactively authorize behavior. Stable `AC-*` and `INV-*` identifiers connect
requirements, evidence, and findings without requiring a large template.

## Risk convention

Use the highest applicable class and explain only consequential implications:

| Class | Changed boundary |
| --- | --- |
| R0 | Documentation or other nonbehavioral content. |
| R1 | Reversible private behavior with limited impact. |
| R2 | Public interfaces, persisted formats, protocols, dependencies/build, concurrency, cross-component behavior, or performance guarantees. |
| R3 | Authorization, tenant isolation, secrets, cryptography, untrusted inputs, data loss, irreversible actions, or safety. |

Risk determines the evidence and decisions needed; it does not create permission to change the target or a
requirement for ceremonial approval of settled facts.

Deliver the selected artifact and material unresolved questions. Save a file only when requested or when an
agreed workflow requires it. Stop at the contract or assessment boundary.
