---
name: precision-review
description: "Review a diff, commit, or named code target for concrete actionable defects; assess without editing or turning missing tests into speculative findings."
disable-model-invocation: true
---

# Precision review

Assess the requested target without editing it. Return only actionable findings supported by a reachable
failure mechanism; no findings is a valid result.

## Establish scope

Identify the target, comparison basis, and intended behavior from the request and available repository
evidence. A dirty workspace or untracked file is a valid review target; preserve it. Ask for a target only
when inspection cannot resolve it.

Read the complete in-scope diff and enough surrounding code, tests, and consumers to understand changed
behavior. Follow public, persisted-data, security, concurrency, or dependency boundaries when implicated. Do
not turn a focused review into a whole-repository audit.

Use the resolved dependency version and actual caller constraints. Existing tests help explain behavior but do
not override an authoritative requirement. If there is no accepted change contract, do not invent one or turn
this review into a contract audit.

## Qualify findings

For each candidate, establish:

- a reachable input, state, or caller that triggers it;
- the changed mechanism and observable adverse consequence;
- a precise location and supporting evidence, including a focused check when needed.

Actively look for a falsifier: validation upstream, an invariant, a type restriction, version behavior, or a
consumer contract that makes the suspected failure impossible. Drop disproven or unsupported candidates.
Calibrate severity to actual impact and exposure rather than a worst-case story without a reachable path.

Do not report style preferences, imagined future requirements, duplicate symptoms of one cause, or missing
tests alone as correctness defects. When test adequacy is explicitly in scope, explain the concrete
unprotected obligation rather than prescribing tests by quota. Distinguish a relevant pre-existing defect from
one introduced by the change.

## Deliver the assessment

Lead with findings ordered by impact, each giving its location, trigger, mechanism, consequence, and evidence.
Keep uncertainty explicit. If none qualify, say so and name material coverage gaps; do not manufacture a
finding.

Summarize the reviewed scope and consequential checks or limitations without a mandatory ledger. Do not fix
findings, offer unsolicited implementation, or automatically request an external peer. Stop when the requested
assessment is supported, not after an arbitrary number of findings.
