# History, movement, and rewrites

## Contents

- [Inspect history and changes](#inspect-history-and-changes)
- [Move the working copy](#move-the-working-copy)
- [Split noninteractively](#split-noninteractively)
- [Squash safely](#squash-safely)
- [Absorb fixups](#absorb-fixups)
- [Restore paths](#restore-paths)
- [Revert immutable or published work](#revert-immutable-or-published-work)
- [Abandon](#abandon)
- [Rebase](#rebase)
- [Verification](#verification)

Read this before editing an existing revision or changing graph structure.

## Inspect history and changes

```bash
jj --no-pager --color=never log -r '::@' -n 20
jj --no-pager --color=never log -r 'trunk()..@'
jj --no-pager --color=never show <revision>
jj --no-pager --color=never diff --git
jj --no-pager --color=never diff --git -r <revision>
jj --no-pager --color=never diff --summary -r <revision>
jj --no-pager --color=never evolog -r <change-id>
```

Prefer `--git` when an agent must interpret a patch. Resolve broad revsets to an inspected set before
mutation.

## Move the working copy

```bash
# New child of @
jj new -m "<description>"

# New child of an explicit base
jj new <revision> -m "<description>"

# Directly edit an existing mutable revision
jj edit <revision>

# Directly edit an adjacent revision
jj prev --edit
jj next --edit
```

Prefer a new child plus a later bounded squash when it makes new work easier to inspect. Never edit the same
logical
change concurrently from multiple workspaces.

## Split noninteractively

Bare `jj split` opens a diff editor. Supply filesets and a description:

```bash
jj split path/to/component -m "<description for selected first revision>"
jj split 'glob:src/parser/**' -m "<description for selected first revision>"
```

The selected changes retain the original logical change; remaining changes become a child revision. Inspect
and describe
both results.

## Squash safely

```bash
# Move all changes from @ into its parent, preserving destination description
jj squash --use-destination-message

# Move selected paths only
jj squash --use-destination-message path/to/file

# Explicit source and destination
jj squash --from <source> --into <destination> --use-destination-message

# Deliberate resulting description
jj squash -m "<description>"
```

Do not use bare `jj squash` when both source and destination have nonempty descriptions; it may open an
editor.

## Absorb fixups

`jj absorb` can rewrite several mutable ancestors:

```bash
jj absorb path/to/file
jj --no-pager --color=never op show -p
```

Use explicit filesets. Avoid interactive hunk selection in unattended operation. Inspect every rewritten
revision.

## Restore paths

`jj restore` rewrites a destination so selected paths match a source:

```bash
# Selected paths from @'s parent into @
jj restore path/to/file

# Explicit source into @
jj restore --from <source> path/to/file

# Explicit source and destination
jj restore --from <source> --into <destination> path/to/file
```

Bare `jj restore` removes the entire diff from `@` while leaving the revision metadata. Use it only when
intentionally
discarding the complete working-copy diff and after preserving unrelated work.

## Revert immutable or published work

Create a new reverse change rather than rewrite existing history:

```bash
jj revert --revision <revision> --onto @
jj describe -m "<repository-compliant reversal description>"
```

Inspect the generated revision and its parent relationship.

## Abandon

`jj abandon` removes a revision and rebases descendants onto its parent or parents:

```bash
jj --no-pager --color=never show <revision>
jj abandon <revision>
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
```

Use only for clearly obsolete mutable work owned by the current task. Inspect the complete resolved revision
set first.

## Rebase

Use explicit selection and destination:

```bash
# Branch containing @
jj rebase --onto 'trunk()'

# One revision only; descendants fill the graph hole
jj rebase --revision <revision> --onto <destination>

# Revision and descendant subtree
jj rebase --source <revision> --onto <destination>

# Branch containing a named revision
jj rebase --branch <revision> --onto <destination>
```

Without `--branch`, `--source`, or `--revision`, `jj rebase` defaults to the branch containing `@`. Inspect
that stack
before running it.

## Verification

After a rewrite, choose the checks that establish its graph, content, or operation postconditions. The
commands below are options, not a mandatory sequence:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log -r '::@' -n 20
jj --no-pager --color=never diff --git
jj --no-pager --color=never op show -p
```
