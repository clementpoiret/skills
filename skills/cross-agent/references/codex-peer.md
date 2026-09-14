# Codex peer setup

Use when Claude is primary and Codex is the peer.

Observe `codex --version` and `codex exec --help` once for the run configuration. Verify the installed
working-directory, stdin, ephemeral, sandbox, and model/effort options before using them. Flag support does
not prove model entitlement. Honor the user or repository model selection; otherwise target `gpt-6-astra` only
when available. Keep configured effort unless a supported alternative was requested. Record only effective
values actually exposed by the CLI.

Prefer ephemeral execution with a read-only filesystem boundary. The following is a command shape, not an
executable template with known-supported flags:

```text
codex exec --ephemeral --sandbox read-only -C <repository-root> <validated-model-options> -
```

Supply the prompt through stdin. Put required `$skill-name` mentions before ordinary task text. Disable or
restrict ambient MCP/connector actions, network-facing tools, additional agents, and delegation using the
installed host's supported configuration. Do not assume a read-only filesystem sandbox prevents remote
mutations or delegation. Inspect effective permissions; if the advisory boundary cannot be enforced, report a
preflight blocker rather than widening access.

Use only the capabilities needed for the requested assessment. A skill does not expand them. Capture stdout,
stderr, exit status, duration, and provider-reported model or usage information. Apply the process state
machine from the root skill. Missing required skills or unavailable checks are evidence gaps, not reasons to
retry automatically.
