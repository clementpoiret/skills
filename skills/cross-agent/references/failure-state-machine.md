# Peer process state machine

Read immediately before invoking a peer. Record the target fingerprint, CLI/version, requested model/effort,
command shape without secrets, start/end or duration, inference status, exit status, and output status. Retain
any corrected invocation error.

| State | Evidence | Action |
| --- | --- | --- |
| Preflight blocked | Missing CLI/capability, denied disclosure/network, or unavailable required authentication/model. | Do not launch; continue primary analysis. |
| Not started | Preconditions pass and no process exists. | Start one process for the stable target. |
| Live | The process exists, including silent output or a resumable runner handle. | Observe or resume that same process; do not duplicate it. |
| Usable | Zero exit with a relevant nonempty report. | Reconcile against primary evidence. |
| Proven pre-inference invocation failure | CLI proves a local invocation defect before any provider request. | One corrected retry is permitted under the gate below. |
| Possibly billable failure | Transport/inference began or may have begun, timeout, quota/provider failure, or unknown termination. | No automatic retry; report and continue primary work. |
| Unusable | Completed call yields empty, irrelevant, or unusably truncated/malformed output. | No automatic retry; no peer evidence. |
| Stale | Target changed materially. | Do not apply the verdict to the new target. A fresh assessment needs authorization still covering its scope and cost. |

A corrected retry requires all of: the first process has terminated; evidence proves no provider request
began; there is a concrete correction to a local invocation defect; the target is unchanged;
disclosure/network/cost policy still permits the run; and no corrected retry has already occurred for this
target.

Authentication rejection, connection attempts, provider timeouts, quota errors, empty model output, and
unknown inference status do not satisfy that gate. An external failure does not justify repeated billable
probes or silently changing models.

Target identity must include repository root, named revision if any, in-scope paths, and relevant diff or
artifact hashes, including dirty and untracked state. Re-observe it before reconciliation. Independent primary
analysis may continue while the peer runs, but do not edit the live target.
