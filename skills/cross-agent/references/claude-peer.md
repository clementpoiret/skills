# Claude peer setup

Use when Codex is primary and Claude Code is the peer.

Observe `claude --version` and `claude --help` once for the run configuration. Check authentication using a
documented non-billable status mechanism when available; otherwise let the single authorized run surface the
limitation. Honor an explicit user model selection, then repository policy, then the configured provider
default. Do not hardcode a moving model alias or infer entitlement from support for a model flag. Preserve
configured effort and record only effective values the CLI exposes; do not map another provider's effort
labels by guesswork.

Use a non-persistent, noninteractive, file-only advisory run. The original CLI recipe uses these options,
which must be checked against installed help before use:

```text
claude -p --no-session-persistence --permission-mode dontAsk
  --tools "Read,Glob,Grep,Skill"
  --allowedTools "Read" "Glob" "Grep" "Skill"
  --disallowedTools "mcp__*" "Skill(cross-agent)" "Skill(cross-agent *)"
  <validated-model-options> <literal-prompt-argument>
```

Treat this as a command shape, not a verified command for every version. Require an effective restriction to
the intended file tools; preapproval alone is not a tool restriction. Deny recursive cross-agent invocation
and ambient MCP actions. Do not expose Bash, writes, subagents, agent teams, or other delegation in an
advisory run. Block the run if these boundaries cannot be enforced.

Supply required `/skill-name` invocations before ordinary task text using syntax supported by the installed
host. Pass the context safely through stdin or literal arguments. Because a file-only peer cannot execute VCS
commands, provide the primary's observed VCS evidence and have the peer distinguish that supplied evidence
from independent inspection.

Capture output, errors, exit status, duration, and observed provider/model metadata. Apply the process state
machine from the root skill. No automatic retry for an unavailable skill or check.
