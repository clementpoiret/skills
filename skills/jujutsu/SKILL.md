---
name: jujutsu
description: "Perform version-control work in a Jujutsu workspace when jj root succeeds, including status, diffs, commits, history, bookmarks, or remotes; not unrelated coding."
disable-model-invocation: false
---

# Jujutsu

Use `jj` for version-control work in a confirmed Jujutsu workspace. An unrelated coding request does not
require a VCS workflow merely because `.jj` exists.

## Establish context once

Check `jj root` and `jj --version` when workspace identity or command compatibility is not already known. If
`jj root` fails, do not apply Jujutsu-specific advice. Reuse observed context until the workspace or installed
version changes.

For an ordinary status or diff request, run the requested read command and explain its output; do not load
every reference or perform a history audit. Use installed command help when a needed option is uncertain. The
advanced examples in this skill came from the supplied library and are not a guarantee of support in the
installed version.

## Select the relevant reference

- Revisions, commits, splitting, rebasing, and history edits: [history and rewrites](references/history-and-rewrites.md).
- Bookmarks, fetch/push, remotes, and tags: [bookmarks, remotes, and tags](references/bookmarks-remotes-tags.md).
- Commit messages or description policy: [descriptions](references/descriptions.md).
- Conflicts, operation log, and recovery: [conflicts and recovery](references/conflicts-and-recovery.md).
- Multiple or stale workspaces: [workspaces](references/workspaces.md).
- Configuration or temporary command execution: [configuration and run](references/configuration-and-run.md).
- Unsupported options or version differences: [version compatibility](references/version-compatibility.md).

## Preserve Jujutsu's boundaries

There is no Git-style staging step. Working-copy commands can snapshot changes even when they appear
read-only; avoid concurrent edits or state reads that make the target ambiguous. Distinguish stable change IDs
from commit IDs, and remember that committing creates a new working-copy change. Bookmarks need deliberate
movement when not handled by repository policy.

In a colocated repository, do not substitute raw Git mutations unless the user explicitly requests a
Git-specific operation. Scope mutations to named revisions, paths, bookmarks, and remotes. Use noninteractive
message options rather than launching an editor accidentally.

Existing authorization remains valid for the task. Obtain authorization covering remote/network operations,
workspace/configuration changes, destructive recovery, shared-history rewrites, or other newly crossed
boundaries; do not repeatedly ask for already-authorized actions. Never use `--ignore-immutable` to bypass
protected history. A `jj` command prefix is not a sandbox: `jj util exec`, arbitrary child commands, and
unrelated effects need their own authorization.

After a mutation, inspect the postcondition that proves the requested result. Choose relevant checks rather
than mechanically repeating status, log, and diff after every command. Report the result, affected revisions
or references, and material limitations, then stop.
