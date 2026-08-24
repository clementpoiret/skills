# Invoking a Claude peer

Use this reference when the primary agent is Codex and the peer is Claude Code.

## Capability preflight

Observe installed help before selecting flags:

```sh
claude --version
claude --help
```

Confirm the installed CLI supports every flag you intend to use. Check authentication through a documented non-billable
status mechanism when available; otherwise let the single peer process surface the limitation.

Select the model and effort from, in order:

1. explicit user request;
2. applicable repository policy;
3. an installed, entitled stable default shown by current CLI configuration or documentation.

Do not assume a moving alias resolves to a particular model. Report the requested identifier and any effective
identifier the CLI exposes.

## Read-only advisory command

Prefer a non-persistent, noninteractive run with the narrowest built-in tool surface. The following is a command **shape**;
omit or adjust flags not supported by the observed CLI rather than guessing:

```sh
cat <<'PEER_PROMPT' | claude -p \
  --no-session-persistence \
  --permission-mode dontAsk \
  --tools "Read,Glob,Grep,Skill" \
  --allowedTools "Read" "Glob" "Grep" "Skill" \
  --disallowedTools "mcp__*" "Skill(cross-agent)" "Skill(cross-agent *)" \
  <validated-model-and-effort-flags> \
  "<required /skill-name prefixes> Act as the independent peer. Follow the task and context supplied on stdin."
<plain-text peer prompt>
PEER_PROMPT
```

`--tools` restricts the built-in surface. `--allowedTools` only preapproves matching tools; it is not the restriction
mechanism. `--disallowedTools` denies recursive `cross-agent` use and ambient MCP tools.

Do not expose Bash, write tools, subagents, or delegation tools for an advisory run. Because the file-only surface cannot
independently execute VCS commands, supply the primary's observed read-only VCS evidence and require the peer to report
independent VCS inspection as unavailable.

Required skills must be actual `/skill-name` prefixes in the prompt argument, not prose in stdin. When several are
required, put all prefixes before ordinary task text using syntax supported by the installed Claude Code version.

## Output and lifecycle

Run from the repository root. Capture stdout, stderr, exit status, duration, and any provider-reported model or usage
information. Apply [failure-state-machine.md](failure-state-machine.md); do not launch a second process merely because a
file-only review could not run VCS commands.
