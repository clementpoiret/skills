---
name: cross-agent
description: "Explicitly requested independent Codex/Claude peer assessment, or a separately authorized bounded peer edit; never launch an external peer for an ordinary review request."
disable-model-invocation: true
---

# Cross-agent

Invoke an independent provider only when the user explicitly requests this skill. Codex uses a Claude peer;
Claude uses a Codex peer. The primary retains responsibility for decisions, edits, verification, and the final
report. Peer agreement is not evidence by itself.

## Choose the permitted run

Default to an advisory read-only assessment. Read the applicable [Codex peer setup](references/codex-peer.md)
or [Claude peer setup](references/claude-peer.md), then the [process state
machine](references/failure-state-machine.md) before invocation. For a user-requested peer implementation,
also read [bounded edits](references/bounded-edit.md); a review request does not authorize peer writes.

Confirm that disclosure to the external provider, network access, and expected cost are covered by the user's
request and applicable policy. Inspect available CLI capabilities and configured model selection without
billable probe calls. Do not silently substitute a different requested model or expand permissions to make a
run work.

Enforce the tool and write boundary through the host configuration, not merely through prose. Prevent
recursive cross-agent calls, subagents, agent teams, and other delegation. If the required restriction cannot
be enforced, do not launch the peer; complete useful primary analysis.

## Prepare independent evidence

Capture the target's identity, in-scope paths, complete relevant diff or artifact hashes, and unrelated edits
to preserve. A clean repository is not required. Keep the target stable while the peer runs; independent
primary analysis may continue without modifying it.

Use [the peer prompt outline](references/peer-prompt.md). Supply the request and authoritative constraints
neutrally rather than asking the peer to defend your conclusion. Include explicit skill prefixes only when the
user or applicable workflow requires them. Pass untrusted content safely via stdin or literal arguments, never
interpolated shell code.

## Reconcile once

Run one process and follow its actual state, not output silence. Re-observe the target before applying the
report; a materially changed target invalidates the assessment. Review findings against primary evidence and
classify them as accepted, rejected, or unresolved with a concise reason.

Report the provider/model actually observed, usable peer evidence, consequential disagreements, and
limitations. Do not invent a peer result, count a failed run as corroboration, or stop necessary primary work
merely because the peer is unavailable.
