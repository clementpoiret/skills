# Define a change contract

Inspect the task and directly relevant repository contracts. Draft the smallest contract that separates the
requested change from unchanged obligations:

- intent, scope, and explicit non-goals;
- observable acceptance criteria with stable `AC-*` identifiers;
- invariants that must remain true with stable `INV-*` identifiers;
- risk class and required evidence for consequential boundaries;
- material unresolved decisions or assumptions, with their owner when known.

Give each criterion a decisive observable result. Link evidence obligations to criteria or invariants rather
than prescribing a broad test suite by default. Include failures, compatibility, migration, rollback, or
security requirements only when implicated by the change.

Example:

| ID | Obligation | Evidence |
| --- | --- | --- |
| AC-1 | A valid unused token can be consumed once. | Success case followed by rejection of reuse. |
| INV-1 | A token never grants access to another tenant. | Cross-tenant rejection without disclosure or state change. |

Distinguish an accepted requirement from a proposed implementation detail. Do not derive intent solely from
current code or tests, add speculative requirements, or force the user to reapprove decisions already settled.
Where consequential alternatives remain, explain the decision needed and draft independent criteria in the
meantime.

Deliver a clearly labeled draft unless acceptance is established by the user or applicable workflow. Defining
a contract does not authorize implementation or external actions.
