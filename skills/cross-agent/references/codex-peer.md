# Invoking a Codex peer

Use this reference when the primary agent is Claude Code and the peer is Codex.

## Capability preflight

Observe installed help before selecting flags:

```sh
codex --version
codex exec --help
```

Confirm support for the selected model, reasoning-effort configuration, ephemeral execution, sandbox, working-directory,
and stdin behavior. Use an explicit user or repository selection when supplied. Otherwise use a supported stable
default and report effective values only when observable.

## Read-only advisory command

Prefer an ephemeral read-only run. This is a command **shape**; include model or effort flags only after preflight shows
they are supported:

```sh
cat <<'PEER_PROMPT' | codex exec \
  --ephemeral \
  --sandbox read-only \
  -C "<repository-root>" \
  <validated-model-and-effort-flags> \
  -
<required $skill-name prefixes, if any>

<plain-text peer prompt>
PEER_PROMPT
```

Required `$skill-name` mentions must precede ordinary task text. The peer may use other relevant local skills when the
host makes them available, but the prompt must prohibit `cross-agent`, delegation workflows, subagents, agent teams, and
other external agents.

Do not grant workspace write, network tools, MCP tools, or additional capabilities for an advisory review. A loaded skill
does not expand the sandbox.

## Output and lifecycle

Run from the repository root. Capture stdout, stderr, exit status, duration, and any provider-reported model or usage
information. Apply [failure-state-machine.md](failure-state-machine.md). An unavailable required skill is missing evidence,
not permission to retry or broaden the sandbox.
