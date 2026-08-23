---
name: jujutsu
description: '**REQUIRED WHEN JJ IS DETECTED** - Activate automatically before any VCS operation whenever `jj root` succeeds or a `.jj/` directory exists in the current path or an ancestor; do not wait for the user to mention Jujutsu or this skill. Use `jj` for repository mutations. A detached Git HEAD is normal in colocated repositories. Requires Conventional Commits 1.0.0 for every nonempty revision description and includes noninteractive, agent-safe workflows for rewriting, bookmarks, tags, remotes, conflicts, workspaces, and recovery.'
allowed-tools: Bash(jj *)
user-invocable: true
disable-model-invocation: false
---

# Jujutsu (`jj`) Version Control System

Use this skill whenever the current directory is inside a Jujutsu repository, even when the user does not mention `jj`
or the skill by name.

**Audited against jj v0.44.0.** Check `jj version` because repositories may use an older or newer release. When the
installed version differs, treat that version's `jj help <command>` output as authoritative and verify version-specific
flags before use.

## Repository Detection and Safety

Before any VCS operation, determine whether the workspace is managed by jj:

```bash
jj root
jj version
```

If `jj root` succeeds, or a `.jj/` directory exists in the current directory or an ancestor, activate this skill and use
`jj` for repository mutations. Do not wait for an explicit skill invocation.

### Git interoperability

- A detached Git HEAD is normal in a colocated jj workspace.
- Prefer `jj` for all mutations, including commits, rebases, bookmark movement, fetches, and pushes.
- Do not run mutating raw Git commands unless the user explicitly requests a Git-specific procedure and the environment
  authorizes those commands.
- Read-only Git commands may work in a colocated workspace, but they are outside this skill's `Bash(jj *)` permission
  and are normally unnecessary.
- Never modify files, refs, objects, or configuration inside `.jj/` directly.
- Use `jj git colocation status` to determine whether the workspace is colocated. In a colocated workspace, import and
  export happen automatically; as of jj 0.44, explicit `jj git import` and `jj git export` are no-ops by default there.
  In a non-colocated workspace, the backing Git repository is hidden and explicit import/export may be needed only for
  deliberate interoperability.

Do not push, delete remote bookmarks or tags, move published tags, abandon published work, or make persistent
configuration changes unless the user has authorized that exact action.

## Agent-Safe Command Rules

### 1. Disable pagers and ANSI color

For command output that will be read or parsed by an agent, use both global flags:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log
jj --no-pager --color=never diff --git
jj --no-pager --color=never show <revision>
```

`--no-pager` prevents an interactive pager. `--color=never` prevents ANSI escape sequences.

### 2. Require Conventional Commit descriptions

Every nonempty jj revision description that represents project work **MUST** comply with
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). In a Git-backed repository, jj revision
descriptions become Git commit messages when exported or pushed.

Use this structure:

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

Rules:

- Use a lowercase type. Standard types are `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`, `perf`,
  `style`, and `revert`.
- Use `feat` for a new feature and `fix` for a bug fix.
- An optional scope is a short noun naming the affected area, such as `parser`, `api`, or `auth`.
- The description is required, concise, imperative, and normally lowercase after the colon, with no trailing period.
- Mark a breaking change with `!` immediately before the colon, a `BREAKING CHANGE: <description>` footer, or both.
- Separate a body from the summary with one blank line. Separate footers from the body with one blank line.
- Footer tokens use hyphens instead of spaces, except `BREAKING CHANGE`, which must be uppercase.
- Keep each revision to one logical change. If a revision needs multiple unrelated types, split it.
- An empty working-copy revision may have an empty description. Before publishing any nonempty revision, give it a
  compliant description.

Examples:

```bash
jj describe -m "feat(auth): add passkey login"
jj commit -m "fix(parser): handle empty token streams"
jj describe -m "docs(cli): clarify bookmark push workflow"
jj describe -m "feat(api)!: remove legacy endpoint

BREAKING CHANGE: clients must migrate to the v2 endpoint."
```

Do not use free-form summaries such as `Add request validation` or `Fix tests`; include a valid type prefix.

### 3. Prevent editor and TUI prompts

Always provide descriptions explicitly, and make every supplied description a Conventional Commit:

```bash
jj describe -m "feat(validation): add request validation"
jj new -m "feat(validation): add request validation"
jj commit -m "feat(validation): add request validation"
```

For squashing, never rely on jj to combine two nonempty descriptions interactively:

```bash
# Preserve the destination revision's compliant description
jj squash --use-destination-message

# Deliberately set a compliant resulting description
jj squash -m "refactor(validation): combine validation changes"
```

Commands requiring special care:

| Command          | Agent-safe usage                                                                                     |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| `jj describe`    | Supply a Conventional Commit message with `-m`                                                       |
| `jj new`         | Supply a Conventional Commit message with `-m` when creating task work                               |
| `jj commit`      | Supply a Conventional Commit message with `-m`; avoid `--editor` and `--interactive`                 |
| `jj squash`      | Supply `--use-destination-message` or a Conventional Commit message with `-m`; avoid `-i`            |
| `jj split`       | Supply filesets and a Conventional Commit message with `-m`; without filesets it opens a diff editor |
| `jj absorb`      | Supply explicit filesets where practical; avoid `-i`, `--interactive`, and `--tool` unattended       |
| `jj resolve`     | Use `--list`, edit files directly, or explicitly use `--tool=:ours`/`:theirs`                        |
| `jj arrange`     | Always interactive; do not use unattended                                                            |
| `jj diffedit`    | Interactive diff editor; do not use unattended                                                       |
| `jj sparse edit` | Opens an editor; use `jj sparse set` instead                                                         |
| `jj config edit` | Opens an editor; use `jj config set` instead                                                         |

### 4. Do not bypass tool permissions

`Bash(jj *)` authorizes jj commands; it does not authorize arbitrary external commands hidden behind jj.

- Never use `jj util exec` in agent operation.
- Do not use `jj run`, `jj bisect run`, configured fix tools, merge tools, or diff tools to execute a command that would
  not be independently authorized as a direct tool call.
- Treat commands supplied after `--` as external command execution, not as ordinary VCS arguments.

### 5. Use explicit revisions and filesets

Avoid commands whose defaults could affect more history or more files than intended. Prefer:

```bash
jj abandon <change-id>
jj restore path/to/file
jj rebase --revision <change-id> --onto <destination>
jj bookmark advance 'exact:feature-name' --to <revision>
```

Quote revsets, fileset expressions, and exact bookmark or tag patterns.

### 6. Verify every mutation

After any mutation, inspect the resulting repository state:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
jj --no-pager --color=never diff --git
```

For operations that may rewrite several revisions, also inspect the operation:

```bash
jj --no-pager --color=never op show -p
```

### 7. Preserve snapshot semantics

Almost every jj command snapshots the working copy before it runs. This is normally desirable.

- Do not use `--ignore-working-copy` for foreground work where current filesystem edits must be observed.
- Use `--ignore-working-copy` only for deliberately stale, read-only inspection, especially operation-log inspection.
- `--no-integrate-operation` is an advanced isolation feature. Do not use it for normal agent work. It does not suppress
  external side effects such as a network push.
- Never pass `--ignore-immutable`. If jj rejects a rewrite because a revision is immutable, create a new revision or use
  `jj revert`.

## Core Concepts

### The working copy is a commit

The working directory corresponds to the working-copy commit, written as `@`. Most jj commands automatically snapshot
filesystem changes into `@`.

There is no staging area. New non-ignored files are normally tracked automatically. If a file was already tracked before
it became ignored, ignore it first and then use:

```bash
jj file untrack path/to/file
```

### Revisions may be mutable or immutable

Mutable revisions can be rewritten by commands such as `describe`, `squash`, `split`, `rebase`, `restore`, and `absorb`.
Immutable revisions are protected by the repository's immutable revset.

Never bypass immutable protection. For published or immutable history, prefer a new change that reverses earlier work.

### Change IDs and commit IDs

- A **change ID**, such as `tqpwlqmp`, identifies a logical change and normally remains stable across rewrites.
- A **commit ID**, such as `3ccf7581`, identifies one exact version and changes when the revision is rewritten.
- Prefer change IDs for logical work. Use commit IDs when an exact historical version is required.
- Hidden or divergent versions can be addressed with numeric suffixes such as `xyz/0` and `xyz/1`.
- A `??` suffix identifies a conflicted bookmark, not a divergent change ID.

### Common revsets

| Revset               | Meaning                                           |
| -------------------- | ------------------------------------------------- |
| `@`                  | Current working-copy commit                       |
| `@-`                 | Parent of the working-copy commit                 |
| `@--`                | Grandparent of the working-copy commit            |
| `::@`                | Ancestors of `@`, including `@`                   |
| `@::`                | Descendants of `@`, including `@`                 |
| `trunk()`            | Repository-configured trunk revision              |
| `trunk()..@`         | Revisions in the current line of work after trunk |
| `bookmarks()`        | Revisions targeted by local bookmarks             |
| `remote_bookmarks()` | Revisions targeted by remote bookmarks            |
| `mutable()`          | Revisions jj considers mutable                    |
| `divergent()`        | Divergent changes                                 |

Quote revsets in shell commands:

```bash
jj --no-pager --color=never log -r 'trunk()..@'
```

## Inspect Before Editing

At the start of a task, inspect the repository rather than assuming `@` is empty or belongs to the task:

```bash
jj version
jj root
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
jj --no-pager --color=never diff --git
jj --no-pager --color=never bookmark list --all-remotes

# Also inspect tags before fetch, push, publication, or a rewrite that may touch tagged history
jj --no-pager --color=never tag list --all-remotes
```

Determine:

1. Whether `@` already contains changes.
1. Whether those changes belong to the user's task.
1. Which revision should be the task's base.
1. Whether the intended stack contains conflicts, divergent changes, or conflicted bookmarks or tags.
1. Whether a bookmark already identifies the work.
1. For fetch, push, publication, or tag-sensitive rewrites, whether any local or remote tag can be affected.

Do not rewrite, restore, squash, or abandon pre-existing changes unless their ownership and purpose are clear.

## Essential Workflows

### Start work from an existing empty `@`

If `@` is empty and already has the correct parent, describe it before editing:

```bash
jj describe -m "feat(auth): add user authentication"
# Edit files
jj --no-pager --color=never status
jj --no-pager --color=never diff --git
```

### Start a dependent change on the current work

Use this only when the new task should depend on the current `@`:

```bash
jj new -m "feat(auth): add user authentication"
# Edit files
```

### Start independent work from trunk or another base

If the current working copy contains unrelated work, do not make the new task its child. Create the task from the
intended base:

```bash
jj new 'trunk()' -m "feat(auth): add user authentication"
```

Or use an explicitly requested base:

```bash
jj new <base-revision> -m "feat(auth): add user authentication"
```

The previous working-copy changes remain recorded in their existing revision.

### Finish the current change and start the next one

`jj commit` is valid and noninteractive when `-m` is supplied. It updates the current description and creates a new
empty working-copy change on top:

```bash
jj commit -m "feat(auth): add user authentication"
```

After this command, the finished change is normally `@-`, while `@` is the new empty child.

### Conventional Commit quality gate

Before considering a revision complete, confirm that its first line matches:

```text
<type>[optional scope][!]: <description>
```

Good examples:

- `feat(validation): add request validation`
- `fix(payment): handle null processor responses`
- `refactor(api): remove deprecated endpoints`
- `docs(parser): clarify error reporting`
- `test(auth): cover expired session tokens`
- `revert(parser): restore legacy tokenization`

Bad examples:

- `Add request validation` — missing type
- `feature: add request validation` — use the standard `feat` type
- `fix(parser) handle empty input` — missing colon and space
- `fix: Fixed parser.` — not imperative, inconsistent capitalization, and unnecessary period

Inspect the stack's first lines before pushing:

```bash
jj --no-pager --color=never log -r 'trunk()..@' -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
```

Rewrite any noncompliant mutable description with `jj describe -r <revision> -m "<conventional-message>"`. Each revision
should represent one logical change.

## Inspecting History and Changes

```bash
# Recent ancestry
jj --no-pager --color=never log -r '::@' -n 20

# Current stack, when trunk() is configured
jj --no-pager --color=never log -r 'trunk()..@'

# One or more revisions
jj --no-pager --color=never show <revision>
jj --no-pager --color=never show <revset>

# Working-copy diff in unified Git format
jj --no-pager --color=never diff --git

# Diff for a specific revision
jj --no-pager --color=never diff --git -r <revision>

# Changed paths only
jj --no-pager --color=never diff --summary -r <revision>

# Evolution of one logical change
jj --no-pager --color=never evolog -r <change-id>
```

Prefer `--git` for diffs because its unified `+`/`-` form is easier for agents to interpret reliably.

## Moving the Working Copy

```bash
# Create an empty child and edit it
jj new -m "feat(component): add the new capability"

# Create an empty child of a specific base
jj new <revision> -m "feat(component): add the new capability"

# Directly edit an existing mutable revision
jj edit <revision>

# Move relative to the current revision and directly edit the target
jj prev --edit
jj next --edit
```

Prefer `jj new <revision>` plus a later `jj squash` over directly editing a revision when that makes the new work easier
to inspect. Avoid editing the same change concurrently from multiple workspaces.

## Refining Revisions

### Update a description

```bash
jj describe -m "fix(parser): improve diagnostics"
jj describe -r <revision> -m "fix(parser): improve diagnostics"
```

### Split a mixed revision noninteractively

`jj split` is interactive only when no filesets are supplied. With filesets and `-m`, it is suitable for an agent:

```bash
# Put these paths in the selected first revision
jj split path/to/component -m "refactor(component): extract component changes"

# Fileset expression
jj split 'glob:src/parser/**' -m "refactor(parser): separate implementation"
```

The selected changes retain the original logical change; the remaining changes are placed in a child revision.
Afterward, describe the remaining child if needed:

```bash
jj describe -m "test(parser): update parser tests"
```

Do not use bare `jj split`, `jj split --interactive`, or an external diff editor in unattended operation.

### Squash changes safely

Move all changes from `@` into its parent while preserving the parent's description:

```bash
jj squash --use-destination-message
```

Move selected paths only:

```bash
jj squash --use-destination-message path/to/file
```

Move changes between explicit revisions:

```bash
jj squash --from <source> --into <destination> --use-destination-message
```

Set a deliberate resulting description instead:

```bash
jj squash -m "refactor(parser): combine implementation and tests"
```

Do not use bare `jj squash` when both source and destination have nonempty descriptions; it may open an editor to
combine them.

### Absorb fixups into ancestors

`jj absorb` moves portions of a source revision to the closest mutable ancestors that last modified the corresponding
lines. It can rewrite several revisions:

```bash
jj absorb path/to/file
jj --no-pager --color=never op show -p
```

Use explicit filesets where possible. jj 0.44 added interactive hunk selection through `-i`/`--interactive`/`--tool`; do
not use those modes unattended. Inspect every affected revision afterward.

### Restore paths

`jj restore` rewrites a destination revision so selected paths match a source revision.

```bash
# Remove current changes to selected paths by restoring from @'s parent
jj restore path/to/file

# Restore selected paths from an explicit revision into @
jj restore --from <source-revision> path/to/file

# Restore selected paths into another mutable revision
jj restore --from <source-revision> --into <destination-revision> path/to/file
```

Bare `jj restore` removes the entire diff from `@` but leaves an empty revision with its description and metadata. Use
it only when intentionally discarding the whole working-copy diff.

### Revert published or immutable work

Create a new reverse change instead of rewriting existing history:

```bash
jj revert --revision <revision> --onto @
```

Review the generated revision and ensure its description is a Conventional Commit. The `revert` type is recommended for
a dedicated reversal:

```bash
jj describe -m "revert(parser): restore previous tokenization

Refs: <reverted-commit-id>"
```

### Abandon a revision

`jj abandon` removes a revision and rebases descendants onto its parent or parents. The abandoned revision's changes are
not preserved in the resulting history unless descendants already contain them.

```bash
jj --no-pager --color=never show <revision>
jj abandon <revision>
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
```

Do not abandon work unless it is clearly obsolete and owned by the current task. Do not use broad revsets without
inspecting their full result first.

### Rebase revisions

Use the canonical `--onto`/`-o` spelling.

```bash
# Rebase the branch containing @ onto trunk
jj rebase --onto 'trunk()'

# Rebase one revision only; descendants fill the graph hole
jj rebase --revision <revision> --onto <destination>

# Rebase a revision and its descendant subtree
jj rebase --source <revision> --onto <destination>

# Rebase the branch containing a specified revision
jj rebase --branch <revision> --onto <destination>
```

If none of `--branch`, `--source`, or `--revision` is supplied, jj defaults to `--branch @`. Inspect the selected stack
before rebasing.

## Handling Conflicts

Jujutsu can record unresolved conflicts in revisions. Operations do not stop for a separate `continue` step.

### Inspect conflicts

```bash
jj --no-pager --color=never status
jj --no-pager --color=never resolve --list
```

`jj resolve --list` is noninteractive. Bare `jj resolve` invokes an external merge tool and should not be used
unattended.

### Resolve by editing files

1. Inspect the conflicted files and markers.
1. Edit the files to the intended resolved content.
1. Run jj to snapshot and verify the resolution.

```bash
jj --no-pager --color=never status
jj --no-pager --color=never diff --git
jj --no-pager --color=never resolve --list
```

### Resolve a conflicted ancestor with an inspectable child

```bash
jj new <conflicted-revision> -m "chore(merge): resolve conflicts"
# Edit conflicted files
jj --no-pager --color=never diff --git
jj squash --use-destination-message
```

This keeps the resolution easy to review before moving it into the conflicted revision.

### Choose an entire side only when semantically correct

```bash
jj resolve --tool=:ours path/to/file
jj resolve --tool=:theirs path/to/file
```

`:ours` and `:theirs` select complete conflict sides. Do not use them merely to make conflict markers disappear.

## Bookmarks

Bookmarks are movable names for revisions and interoperate with Git branches. They do not generally advance when
`jj new` or `jj commit` creates a child.

### Inspect bookmarks

```bash
jj --no-pager --color=never bookmark list --all-remotes
```

### Create a bookmark

```bash
jj bookmark create feature-name --revision <revision>
```

### Advance a bookmark forward

Prefer `bookmark advance` for normal forward movement:

```bash
jj bookmark advance 'exact:feature-name' --to @

# After `jj commit`, the finished change is commonly @-
jj bookmark advance 'exact:feature-name' --to @-
```

Bookmark arguments are patterns by default. Use `exact:` when a specific name is supplied dynamically.

### Move backward or sideways

Backward or sideways movement requires explicit authorization and `--allow-backwards`:

```bash
jj bookmark move 'exact:feature-name' --to <revision> --allow-backwards
```

Inspect the old and new targets before using this command.

### Delete versus forget

```bash
# Mark the bookmark for deletion on tracked remotes during a later push
jj bookmark delete 'exact:feature-name'

# Remove the local bookmark without propagating remote deletion
jj bookmark forget 'exact:feature-name'
```

These operations are not interchangeable. Remote bookmark deletion requires explicit user authorization.

### Conflicted bookmarks

A bookmark ending in `??` is conflicted. Inspect all local and remote targets before resolving it:

```bash
jj --no-pager --color=never bookmark list --all-remotes --conflicted
jj --no-pager --color=never log -r '<bookmark-name>'
```

Fetch current remote state if appropriate, then explicitly move/set the local bookmark only after identifying the
intended target.

## Tags

In jj v0.44.0 and later, Git tag fetching and pushing is stable. Remote tags can be tracked or untracked like bookmarks,
fetched tags are tracked by default, and tracked tags participate in default push selection. Treat tag creation,
movement, deletion, and publication as release-affecting operations that require explicit user intent. Treat tracking
changes as synchronization-policy changes because they affect later fetch and push behavior.

### Inspect tags

```bash
jj --no-pager --color=never tag list --all-remotes
```

### Create or move a local tag

```bash
# Create a new tag at an explicit revision
jj tag set release-name --revision <revision>

# Moving an existing tag is exceptional and requires explicit authorization
jj tag set release-name --revision <revision> --allow-move
```

### Delete a local tag

```bash
jj tag delete 'exact:release-name'
```

Deleting a tracked local tag can make a later push delete the corresponding remote tag. Inspect the dry run and obtain
explicit authorization before propagating that deletion.

### Track or untrack an exact remote tag

```bash
jj tag track 'release-name@origin'
jj tag untrack 'release-name@origin'
```

Tracking imports the remote tag as a same-named local tag and lets future fetches update it. Untracking keeps the
last-fetched remote pointer visible when requested but stops importing future updates into a local tag.

### Push one exact tag

```bash
jj git push --dry-run --remote origin --tag 'exact:release-name'
jj git push --remote origin --tag 'exact:release-name'
```

Do not move or delete a published tag, or propagate a tag deletion, unless the user explicitly authorizes that exact
remote-visible or release operation.

## Git-Backed Repositories and Remotes

### Clone or initialize

```bash
# Clone a Git remote; colocation is the default unless configuration disables it
jj git clone <url> [destination]

# Clone while fetching only explicitly selected tags
jj git clone --tag '<tag-name-or-pattern>' <url> [destination]

# Initialize jj in an existing Git repository and explicitly request colocation
jj git init --colocate

# Check colocation
jj git colocation status
```

In jj v0.44.0, use repeated `--tag <pattern>` options to restrict cloned tags; the older `--fetch-tags` option has been
removed. Do not create repositories, change colocation mode, or add/remap remotes unless the user requested it.

### Fetch remote state

Fetch is a mutation: it updates remote-tracking state and may update or rebase related local history according to
repository configuration and preserved change IDs. In jj v0.44.0, an unqualified fetch also fetches tags according to
the remote's tag patterns; the first fetch after upgrading an existing repository re-fetches tags to initialize
tracking.

```bash
jj git fetch --remote origin
```

When only one reference class is needed, scope the fetch explicitly. For `git fetch` and `git clone`, branch and tag
arguments use Git-ref patterns rather than jj string-pattern syntax, so supply a literal name for an exact ref and do
not prefix it with `exact:`:

```bash
# One branch/bookmark from the Git remote
jj git fetch --remote origin --branch <branch-name>

# One tag
jj git fetch --remote origin --tag '<tag-name>'
```

After fetching, inspect what changed before rebasing:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never bookmark list --all-remotes
jj --no-pager --color=never tag list --all-remotes
jj --no-pager --color=never log -r 'trunk()..@'
```

Rebase only when the local stack still needs to move:

```bash
jj rebase --onto 'trunk()'
```

### Push safely

Push only when the user explicitly requests it.

Before pushing:

1. Identify the intended remote.
1. Identify the exact revision, bookmark, or tag to publish.
1. Inspect local and remote bookmarks and tags; confirm only the intended references are selected.
1. Confirm each selected bookmark or tag points to the intended revision.
1. Confirm every nonempty description complies with Conventional Commits 1.0.0 and every change is atomic.
1. Confirm there are no unintended conflicts, private revisions, or unrelated descendants.
1. Run a dry run.

Push one exact bookmark:

```bash
jj git push --dry-run --remote origin --bookmark 'exact:feature-name'
jj git push --remote origin --bookmark 'exact:feature-name'
```

A newly pushed bookmark is tracked automatically.

Push a revision under a generated bookmark:

```bash
# Use @ when the finished work is the current working-copy revision
jj git push --dry-run --remote origin --change @
jj git push --remote origin --change @

# Use @- when jj commit created a new empty @
jj git push --dry-run --remote origin --change @-
jj git push --remote origin --change @-
```

Avoid bare `jj git push`, `--all`, `--tracked`, or `--deleted` unless the user intends the resulting set of bookmarks
and tags to be pushed or deleted. In jj v0.44.0, bare push can select tracked tags, `--all` includes all tags as well as
bookmarks, and `--tracked` includes tracked tags. Do not bypass push protections such as empty-description,
private-commit, or conflict checks—including `--allow-conflicts`—without explicit authorization and a documented reason.

## Workspaces

A workspace is a working copy attached to a shared jj repository. Each workspace has its own working-copy commit and
sparse patterns; commits, operations, bookmarks, tags, and remote-tracking state are shared.

### Common commands

```bash
# Add a workspace. By default, its new @ shares the current @'s parent(s).
jj workspace add ../my-tests

# Add a named workspace on an explicit base
jj workspace add --name tests --revision <revision> -m "test(workspace): run isolated tests" ../my-tests

# Inspect workspaces; jj 0.44 shows workspace roots in this listing by default
jj --no-pager --color=never workspace list
jj workspace root --name <workspace-name>

# Forget workspace metadata; this does not delete files on disk
jj workspace forget <workspace-name>

# Rename the current workspace
jj workspace rename <new-name>
```

Do not delete a workspace directory without also ensuring its workspace metadata is forgotten.

### Avoid shared working-copy changes

Do not use `jj edit <revision>` in two workspaces at once. Rewriting one workspace's working-copy change from another
workspace can make the first workspace stale.

### Recover a stale workspace

```bash
jj workspace update-stale
jj --no-pager --color=never status
jj --no-pager --color=never log -r '@ | divergent()'
```

Depending on the stale state, jj may create a recovery or divergent revision. Divergent versions use numeric suffixes
such as `/0` and `/1`. Inspect the graph and preserve all user work before resolving divergence.

## Undo and Operation-Log Recovery

Every jj mutation is recorded in the operation log.

### Immediate undo and redo

```bash
jj undo
jj redo
```

Repeated `jj undo` walks backward through operations; repeated `jj redo` walks forward through undone operations. Verify
the repository after every undo or redo.

### Inspect operations without snapshotting

```bash
jj --at-op=@ --ignore-working-copy --no-pager --color=never op log -n 20
```

Inspect repository state at a selected operation:

```bash
jj --at-op=<operation-id> --no-pager --color=never status
jj --at-op=<operation-id> --no-pager --color=never log
```

### Restore or revert operations

```bash
# Restore the repository to an earlier operation, undoing all later operations
jj op restore <operation-id>

# Revert one selected operation while retaining later operations when possible
jj op revert <operation-id>
```

`jj op restore` restores repository and remote-tracking state by default. Inspect remote-tracking bookmarks and tags
before a subsequent push.

Do not garbage-collect or abandon operation history as routine cleanup; it is the primary recovery mechanism.

## Configuration

Read configuration through jj:

```bash
jj config get <name>
jj --no-pager --color=never config list [name]
jj config path --user
jj config path --repo
jj config path --workspace
```

`jj config path --repo` and `--workspace` may create the secure external config directory if it does not already exist.
Call them only when the path is needed.

Set configuration noninteractively only when explicitly requested:

```bash
jj config set --user <name> <toml-value>
jj config set --repo <name> <toml-value>
jj config set --workspace <name> <toml-value>
```

Repository and workspace configuration is stored in secure external config locations. Do not edit legacy paths such as
`.jj/repo/config.toml` or `.jj/workspace-config.toml`.

Avoid `jj config edit` in an unattended environment because it opens an editor.

## Advanced: `jj run`

`jj run` executes an external command in an isolated working copy for each selected revision. By default it saves
tracked-file changes by amending those revisions, so it is a mutating history operation rather than merely a test
runner.

Use it only when the external command is independently authorized and always select an explicit revset. For a mutating
run, review the resulting operation:

```bash
jj run --revision 'mutable() & trunk()..@' --clean -- <command> [args...]
jj --no-pager --color=never op show -p
```

For read-only checks, prefer `--ignore-changes`; temporary file modifications are discarded and immutable revisions may
be inspected without bypassing immutable protection:

```bash
jj run --revision 'trunk()..@' --ignore-changes --clean -- <test-or-lint-command> [args...]
```

Use `--clean` when revisions must start from fresh temporary working copies. In jj 0.44, revisions start oldest-first;
with parallel jobs, start order is guaranteed but completion order is not. `--passthrough` connects output directly to
the terminal, does not inherit stdin, and permits only one job; avoid it when a command could prompt. Never use
`--ignore-errors` as a quality gate because failed child commands do not make `jj run` fail. Use it only when the user
explicitly wants aggregate results and report every failure separately. Do not run against published or unrelated
revisions, and never use `jj run` to bypass the agent's normal command permissions.

## Final Quality Check

Before reporting completion:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log -r 'trunk()..@'
jj --no-pager --color=never diff --git
jj --no-pager --color=never bookmark list --all-remotes

# Include for fetch, push, publication, or tag-sensitive work
jj --no-pager --color=never tag list --all-remotes
```

Confirm:

1. The intended revisions contain all requested changes.
1. No unrelated user changes were rewritten or discarded.
1. Each revision is atomic and every nonempty description complies with Conventional Commits 1.0.0.
1. The stack has no unintended conflicts or divergence.
1. Every in-scope bookmark or tag points to its intended revision.
1. No tag was created, moved, deleted, tracked, untracked, or pushed unless the user requested it.
1. No network write occurred unless the user requested it.
1. The user is told exactly what changed and whether anything remains unpushed.

## Quick Reference

| Action                  | Agent-safe command                                                   |
| ----------------------- | -------------------------------------------------------------------- |
| Check version           | `jj version`                                                         |
| Find workspace root     | `jj root`                                                            |
| Status                  | `jj --no-pager --color=never status`                                 |
| Log                     | `jj --no-pager --color=never log`                                    |
| Diff                    | `jj --no-pager --color=never diff --git`                             |
| Show revision           | `jj --no-pager --color=never show <revision>`                        |
| Describe `@`            | `jj describe -m "<type>(<scope>): <description>"`                    |
| New described change    | `jj new [base] -m "<type>(<scope>): <description>"`                  |
| Finish and start next   | `jj commit -m "<type>(<scope>): <description>"`                      |
| Edit revision           | `jj edit <revision>`                                                 |
| Split by filesets       | `jj split <filesets> -m "<type>(<scope>): <description>"`            |
| Squash into parent      | `jj squash --use-destination-message`                                |
| Absorb paths            | `jj absorb <filesets>`                                               |
| Restore paths           | `jj restore <filesets>`                                              |
| Revert revision         | `jj revert -r <revision> -o @`                                       |
| Rebase current branch   | `jj rebase -o 'trunk()'`                                             |
| Rebase one revision     | `jj rebase -r <revision> -o <destination>`                           |
| Abandon revision        | `jj abandon <revision>`                                              |
| List conflicts          | `jj resolve --list`                                                  |
| Create bookmark         | `jj bookmark create <name> -r <revision>`                            |
| Advance bookmark        | `jj bookmark advance 'exact:<name>' --to <revision>`                 |
| Forget local bookmark   | `jj bookmark forget 'exact:<name>'`                                  |
| Delete tracked bookmark | `jj bookmark delete 'exact:<name>'`                                  |
| List tags               | `jj --no-pager --color=never tag list --all-remotes`                 |
| Set new tag             | `jj tag set <name> -r <revision>`                                    |
| Delete local tag        | `jj tag delete 'exact:<name>'`                                       |
| Track remote tag        | `jj tag track '<name>@<remote>'`                                     |
| Untrack remote tag      | `jj tag untrack '<name>@<remote>'`                                   |
| Fetch bookmarks + tags  | `jj git fetch --remote <remote>`                                     |
| Fetch one branch        | `jj git fetch --remote <remote> -b <branch-name>`                    |
| Fetch one tag           | `jj git fetch --remote <remote> -t '<tag-name>'`                     |
| Preview exact bookmark  | `jj git push --dry-run --remote <remote> -b 'exact:<name>'`          |
| Push exact bookmark     | `jj git push --remote <remote> -b 'exact:<name>'`                    |
| Preview exact tag       | `jj git push --dry-run --remote <remote> -t 'exact:<name>'`          |
| Push exact tag          | `jj git push --remote <remote> -t 'exact:<name>'`                    |
| Undo / redo             | `jj undo` / `jj redo`                                                |
| Operation log           | `jj --at-op=@ --ignore-working-copy --no-pager --color=never op log` |
| Restore operation       | `jj op restore <operation-id>`                                       |
| Revert operation        | `jj op revert <operation-id>`                                        |
| Add workspace           | `jj workspace add <path>`                                            |
| Fix stale workspace     | `jj workspace update-stale`                                          |
| Read config             | `jj config get <name>`                                               |
| Read-only checks        | `jj run -r '<revset>' --ignore-changes -- <command>`                 |
| Set repo config         | `jj config set --repo <name> <value>`                                |

## Official References

- Jujutsu CLI reference: <https://docs.jj-vcs.dev/latest/cli-reference/>
- Working-copy and workspace model: <https://docs.jj-vcs.dev/latest/working-copy/>
- Git compatibility and colocation: <https://docs.jj-vcs.dev/latest/git-compatibility/>
- GitHub/GitLab workflow: <https://docs.jj-vcs.dev/latest/github/>
- Configuration reference: <https://docs.jj-vcs.dev/latest/config/>
- Changelog: <https://docs.jj-vcs.dev/latest/changelog/>
- Conventional Commits 1.0.0: <https://www.conventionalcommits.org/en/v1.0.0/>
