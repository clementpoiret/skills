# Bounded peer edit run

Use this only when the user explicitly asks the peer itself to implement or fix a narrowly scoped change. Prefer an
advisory proposal followed by primary-owned edits.

## Admission gate

A writable run is allowed only when all are true:

- exact writable paths and behavior are named;
- existing edits in those paths can be preserved and reviewed;
- the peer does not need commits, bookmark or branch movement, history rewrites, pushes, deployment, dependency changes,
  or unrelated cleanup;
- the primary can inspect every resulting byte and run the required checks;
- repository policy permits the external provider to receive the scoped content.

If isolation is uncertain, use a read-only proposal instead.

## Procedure

1. Capture the current status, complete in-scope diff, unrelated edits, and observed checks.
2. Explicitly invoke required peer skills before ordinary task text.
3. State exact writable paths and prohibited actions.
4. Grant only workspace editing and the smallest required file tools. Do not add Bash, network-facing tools, MCP tools,
   or delegation merely because a skill requests them.
5. Keep one synchronous peer process. The primary must not edit concurrently.
6. After completion, inspect every changed path and the complete diff against the captured baseline.
7. Reject or undo out-of-scope changes with inverse edits that preserve unrelated work; never reset the working copy.
8. Run focused and broader checks and reconcile the result as primary-owned evidence.

A bounded peer edit does not transfer ownership. The primary remains responsible for correctness and the final report.
