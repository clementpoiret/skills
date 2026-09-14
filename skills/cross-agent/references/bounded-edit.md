# Bounded peer edits

Use only when the user explicitly asks the peer itself to implement a named change. Prefer an advisory
proposal with primary-owned edits when isolation is uncertain.

Require exact writable paths and behavior, preservation of existing edits, provider disclosure permission, and
the ability to inspect every resulting change and verify it. Use a host-enforced isolated write boundary; a
prompt listing allowed paths is not isolation. Do not grant commits, branch/bookmark movement, history
rewrites, pushes, deployments, dependency changes, or unrelated cleanup.

Capture the complete in-scope state before launch. Supply required peer skill invocations and exact
constraints. Grant only necessary file tools and bounded writes, not shell, network-facing actions, MCP, or
delegation merely because a skill asks for them. If supported controls cannot enforce that surface, use a
read-only proposal or report the blocker.

Keep one process and do not edit its target concurrently. After completion, inspect every changed path and the
complete diff against the captured baseline. Reject out-of-scope changes through precise inverse edits that
preserve unrelated work, never a wholesale working-copy reset. Run checks required by the actual changed
boundaries and reconcile the result as primary-owned evidence.
