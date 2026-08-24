---
name: jujutsu
description: Detect Jujutsu repositories and use safe, noninteractive `jj` workflows for status, diffs, revisions, bookmarks, tags, remotes, conflicts, workspaces, configuration, and recovery. Prefer `jj` for repository mutations in an active Jujutsu workspace. A detached Git HEAD is normal in colocated repositories.
allowed-tools: Bash(jj *)
user-invocable: true
disable-model-invocation: false
---

# Jujutsu (`jj`) Version Control

Use this skill whenever the current directory is inside a Jujutsu workspace, even when the user does not mention `jj`.

## 1. Detect the workspace and installed version

Before any VCS operation, run:

```bash
jj root
jj version
```

`jj root` is authoritative. A `.jj/` directory is only a discovery hint; do not assume that an arbitrary ancestor's
metadata governs the current directory when `jj root` fails.

This skill was reviewed against `jj 0.44.0`. The installed version's `jj help <command>` output is authoritative. When
the version differs, a flag is uncertain, or a version-specific workflow is needed, read
[version-compatibility.md](references/version-compatibility.md) and verify the command locally before mutation.

If `jj root` fails, stop applying this skill and use the repository's actual VCS workflow.

## 2. Treat permissions and interoperability correctly

The `allowed-tools: Bash(jj *)` field may preapprove matching Claude Code calls during the invocation turn. It is not a
sandbox and does not deny other tools. Enforce real restrictions through host permissions, deny rules, hooks, and the
current execution sandbox.

When `jj root` succeeds:

- prefer `jj` for repository mutations, including revisions, rebases, bookmarks, fetches, and pushes;
- a detached Git HEAD is normal in a colocated workspace;
- do not run mutating raw Git commands unless the user explicitly requests a Git-specific procedure and policy permits
  it;
- read-only Git inspection may be used only when needed and authorized, but normally `jj` is sufficient;
- never edit `.jj/` files, refs, objects, or configuration directly;
- use `jj git colocation status` when Git interoperability matters.

Do not push, fetch, create or move tags, delete remote references, abandon published work, rewrite immutable history,
create or remove workspaces, or persist configuration unless the user authorized that class of action.

## 3. Use agent-safe commands

For output consumed by an agent, disable pagers and ANSI color:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
jj --no-pager --color=never diff --git
jj --no-pager --color=never show <revision>
```

Use explicit revisions, filesets, bookmark patterns, tag patterns, and remotes. Quote revsets and expressions. Prefer
`exact:<name>` where a `jj` string pattern must select one bookmark or tag.

Prevent unattended editors and TUIs:

- provide `-m` for `describe`, `new`, and `commit`;
- give `split` explicit filesets and `-m`;
- give `squash` `--use-destination-message` or `-m`;
- avoid bare interactive `split`, `diffedit`, `arrange`, `config edit`, and `sparse edit`;
- use `resolve --list`, edit conflict markers directly, or select an explicit merge tool only when authorized.

Do not use `jj util exec` to hide an external command. Treat `jj run`, `jj bisect run`, fix tools, merge tools, diff
tools, and any command after `--` as external execution requiring its own authorization. Read
[configuration-and-run.md](references/configuration-and-run.md) before using them.

Never pass `--ignore-immutable`. If a revision is immutable, create a new revision or use `jj revert`.

## 4. Understand the working-copy model

The working directory corresponds to the working-copy commit `@`. Most commands snapshot filesystem changes into `@`;
there is no staging area. New non-ignored files are normally tracked automatically.

- Prefer change IDs for logical changes across rewrites.
- Use commit IDs only when an exact historical version matters.
- Bookmarks are movable names and do not automatically advance with every `new` or `commit`.
- Operations are recorded in the operation log and are the primary recovery mechanism.

Do not use `--ignore-working-copy` for foreground work whose current filesystem edits must be observed. It is
appropriate for deliberately stale read-only operation-log inspection. Avoid `--no-integrate-operation` during normal
work; it does not suppress external side effects such as a push.

## 5. Inspect before mutation

Before changing repository state, inspect enough context to identify ownership and blast radius:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
jj --no-pager --color=never diff --git
jj --no-pager --color=never bookmark list --all-remotes
```

Add tag, workspace, remote, or operation-log inspection when the requested operation can affect them. Determine:

- whether `@` is empty or already contains unrelated work;
- the intended base and exact revisions or paths affected;
- which revisions are mutable or published;
- whether conflicts, divergent changes, or stale workspaces exist;
- whether local or remote bookmarks and tags can move or be deleted.

Do not rewrite, restore, squash, abandon, or publish pre-existing work whose ownership is unclear.

## 6. Follow the repository's revision-description policy

Follow the repository's revision-description policy. Use Conventional Commits only when repository policy or the user
requires it; Jujutsu itself does not impose that convention. Always provide noninteractive descriptions that are
accurate, atomic, and appropriate for the destination repository.

Read [descriptions.md](references/descriptions.md) before creating, changing, squashing, or publishing a nonempty
revision.

## 7. Use bounded everyday workflows

### Inspect only

```bash
jj --no-pager --color=never status
jj --no-pager --color=never diff --git
jj --no-pager --color=never log -r '::@' -n 20
```

### Start work

If an empty `@` already has the correct parent, describe it with the repository-approved message and edit files:

```bash
jj describe -m "<revision description>"
```

To start dependent work, create a child:

```bash
jj new -m "<revision description>"
```

To keep new work independent from unrelated `@`, use an explicit base:

```bash
jj new 'trunk()' -m "<revision description>"
# or
jj new <base-revision> -m "<revision description>"
```

### Finish and continue

```bash
jj commit -m "<revision description>"
```

After `commit`, the finished change is normally `@-` and `@` is a new empty child.

### Rebase a bounded stack

Inspect the selected stack, then use an explicit destination:

```bash
jj --no-pager --color=never log -r 'trunk()..@'
jj rebase --onto 'trunk()'
```

For exact revision/subtree semantics, rewrites, split, squash, absorb, restore, revert, and abandon, read
[history-and-rewrites.md](references/history-and-rewrites.md).

## 8. Load only the reference needed

- Revision descriptions and optional Conventional Commits: [descriptions.md](references/descriptions.md)
- History inspection, movement, and rewrites: [history-and-rewrites.md](references/history-and-rewrites.md)
- Conflicts, undo, and operation-log recovery: [conflicts-and-recovery.md](references/conflicts-and-recovery.md)
- Bookmarks, remotes, fetch, push, and tags: [bookmarks-remotes-tags.md](references/bookmarks-remotes-tags.md)
- Multiple workspaces and stale-workspace recovery: [workspaces.md](references/workspaces.md)
- Configuration and external commands through `jj run`: [configuration-and-run.md](references/configuration-and-run.md)
- Installed-version and 0.44 compatibility notes: [version-compatibility.md](references/version-compatibility.md)

Do not load every reference for a simple status or diff request.

## 9. Verify every mutation

After every mutation, inspect the relevant state:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
jj --no-pager --color=never diff --git
```

For operations that can rewrite several revisions, also run:

```bash
jj --no-pager --color=never op show -p
```

For bookmark, tag, remote, workspace, or configuration changes, run the corresponding focused list/get command. For a
push, require a dry run, inspect the selected references, then verify local and remote-tracking state afterward.

Never claim a mutation succeeded from exit status alone when the resulting repository state was not inspected.

## Final report

```text
Repository: <jj root>
Version: <observed jj version>
Operation: <read-only inspection or exact authorized mutation>
Target: <revisions, paths, bookmarks, tags, remotes, or workspace>
Commands observed: <commands and results>
Resulting state: <status/log/diff/reference evidence>
Description policy: <repository policy followed, or none found>
Unrelated work preserved: <yes, no, or exact limitation>
Residual risk: <none or exact unverified area>
```
