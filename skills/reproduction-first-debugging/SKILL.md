---
name: reproduction-first-debugging
description: "Diagnose and fix a reported bug, failing test, flaky result, or performance regression by reproducing the failure and testing its cause."
---

# Reproduction-first debugging

Establish the failure and its cause before patching. Preserve the expected behavior instead of changing the
oracle to fit the implementation.

## Establish a trustworthy reproduction

Capture the reported input, command, expected versus actual behavior, and relevant environment or version. Run
the closest available reproduction; distinguish the product failure from setup, dependency, credential, or
harness failures. Reduce the case only while preserving the same failure mechanism.

If the failure cannot be reproduced, report what was attempted and what observation is missing. Continue
useful investigation, but do not present a speculative repair as a verified fix. A task without a trustworthy
reproduction remains an investigation until evidence supports proceeding.

## Test the cause

Trace the failing path to the component or invariant that owns the behavior. Check effective configuration,
resolved dependency versions, and boundary inputs where they matter. Use competing hypotheses only when the
evidence is genuinely ambiguous; an existing regression with a clear cause does not need invented
alternatives.

Choose a discriminating observation or experiment, preferably changing one causal factor. Reject explanations
contradicted by traces, types, versions, or observed execution. Logs and extra probes should answer a
question, not expand into indiscriminate instrumentation.

For flaky or concurrent failures, retain timing, ordering, and frequency evidence; a single passing run is not
proof. For a performance regression, preserve a comparable workload and baseline so setup changes or noise
cannot masquerade as recovery.

## Repair and close

Make the smallest complete root-cause repair. Do not substitute larger timeouts, retries, swallowed
exceptions, hardcoded fixture outputs, or weakened assertions unless those behaviors are independently
required by the contract.

Rerun the original reproduction and relevant regression checks. Add a regression test when it provides missing
durable coverage; do not create a duplicate merely to satisfy the workflow. Check necessary consumers when the
repair crosses a boundary.

When repeated patches yield no new evidence, stop that approach and return to a discriminating investigation.
Preserve useful completed work and distinguish an environmental blocker from an incorrect patch.

Report the observed cause, repair, and verification. Without adequate evidence, report the result as
investigation, partial implementation, or implemented-but-unverified, as applicable. Once the original failure
and relevant obligations are resolved, stop optional investigation.
