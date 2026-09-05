# Peer process failure state machine

Read this immediately before invoking a peer CLI.

## States

| State | Evidence | Action |
| --- | --- | --- |
| `preflight-blocked` | CLI missing, unsupported required capability, denied network, unavailable authentication, or policy prohibits disclosure | Do not start a process. Report the exact limitation and continue primary analysis. |
| `not-started` | Preconditions pass; no process exists | Start one process for the target. Record command shape without secrets, target fingerprint, start time, and requested model/effort. |
| `live` | OS process still exists, even if silent or the command runner returned a resumable handle | Observe or resume the same process. Never start another. |
| `usable` | Process exits zero and returns a nonempty report relevant to the task | Reconcile it. |
| `pre-inference-failure` | The CLI proves that no model request began, for example local flag parsing failed before authentication or transport | Correct the demonstrated invocation defect and retry at most once. Record the first failure and correction. |
| `possibly-billable-failure` | Transport started, inference began or may have begun, timeout killed the process, quota or provider failure occurred, or inference status is unknown | Do not retry automatically. Report the failure and continue primary analysis. |
| `unusable` | Empty, irrelevant, truncated beyond use, or malformed output after a completed call | Do not retry automatically. Treat it as no peer evidence. |
| `stale` | Target changed materially while the peer was running or before reconciliation | Do not apply the verdict to the new target. A fresh pass is allowed because the target changed materially. |

## Target identity

Before invocation, record enough information to detect material change without requiring a clean VCS state:

- repository root;
- VCS and user-named revision, if any;
- in-scope paths;
- read-only status/diff summary or hashes of named artifacts;
- unrelated edits that must remain untouched.

Do not edit the target while a process is live. Independent primary analysis may continue without changing that target.
Re-observe the target after completion.

## Retry boundary

A corrected retry is safe only when all are true:

1. the first process has terminated;
2. the CLI provides evidence that no provider request or inference began;
3. the failure is an invocation-layer defect with a concrete correction;
4. the target is unchanged;
5. retry does not violate network, cost, or repository policy;
6. no previous corrected retry has occurred for that target.

Authentication rejection, network connection attempts, provider timeouts, quota errors, empty model output, and unknown
termination points do **not** meet this gate.

## Recording

For every attempt, retain:

```text
Attempt: 1 | corrected retry
Target identity: <scope and observed fingerprint>
CLI/version: <observed>
Requested model/effort: <values or default>
Start and end: <timestamps or duration>
Inference status: not started | started | may have started | unknown
Exit status: <code or termination>
Output status: usable | empty | unusable | unavailable
Correction: <none or exact corrected local invocation defect>
```
