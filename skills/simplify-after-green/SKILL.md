---
name: simplify-after-green
description: "Explicitly requested behavior-preserving simplification of already-correct production code after a credible green baseline; not bug repair or test-suite reduction."
---

# Simplify after green

Reduce material maintenance complexity while preserving required behavior. This workflow is explicit-only; do
not append it automatically to implementation or debugging.

## Establish scope and baseline

Use the user's named scope and change budget. Without a narrower scope, inspect repository production code,
not merely the current diff. Review the entire agreed scope and apply all material, justified, verifiable
simplifications within its budget; do not stop after the easiest candidate.

Require a credible relevant green baseline. Reuse existing checks when they cover the exact relevant state;
otherwise establish it. If the baseline fails, report the blocker rather than repairing bugs under the guise
of simplification.

Identify the behavioral basis from accepted requirements, documented policy, tests with an independent oracle,
and established contracts. High-risk behavior needs an explicit basis and evidence, but an already documented
policy does not need a newly numbered contract for ceremony.

## Qualify and simplify

Seek fewer concepts, clearer ownership, simpler control flow, or less duplication with the same obligations.
Rank by maintenance benefit and evidence, not by line count or ease alone. Avoid speculative architecture
changes, aesthetic churn, and additional configurability.

For each material candidate, identify what changes structurally and why behavior remains equivalent. Preserve
security and validation, compatibility, atomicity and protocols, ownership, backpressure, performance
obligations, and observability when relevant. Do not infer dead code solely from absent text references:
examine dynamic registration and external consumers.

Reject candidates whose equivalence cannot be established within the available evidence budget, and continue
with independent candidates. A blocked risky candidate is not permission to abandon the rest of the scope or
weaken its proof.

Apply coherent simplifications and verify affected behavior. Test adjustments may accommodate an equivalent
production refactor but must preserve their obligations and fault sensitivity. Remove only artifacts made
obsolete by these edits. Do not change intended behavior, fix unrelated defects, or perform cleanup outside
the agreed scope.

## Finish the scope

Use verification proportionate to the changed boundaries and reuse still-valid results. When evidence
contradicts equivalence, restore your own candidate safely rather than redefining the contract. Once the
agreed scope is reviewed and justified work is complete, stop; do not restart candidate hunting indefinitely.

Report the audited scope, material simplifications and their evidence, and consequential retained or blocked
candidates. A no-change result is correct when no worthwhile supported simplification exists. Do not imply
that unreviewed scope was audited or that fewer lines proves improvement.
