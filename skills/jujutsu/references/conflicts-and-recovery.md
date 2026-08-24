# Conflicts and recovery

Jujutsu can record conflicts inside revisions. Most graph operations do not stop for a separate `continue` step.

## Inspect conflicts

```bash
jj --no-pager --color=never status
jj --no-pager --color=never log -r 'conflicts()'
jj --no-pager --color=never resolve --list
jj --no-pager --color=never show <conflicted-revision>
```

Read surrounding history and determine the intended semantics before choosing a side.

## Resolve by editing

Edit conflict markers in the working copy, then verify that the conflict disappeared and tests cover the resolved
behavior:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never resolve --list
jj --no-pager --color=never diff --git
```

When the conflict belongs to a mutable ancestor, create or use an inspectable child, fix the ancestor deliberately, and
inspect any descendant rebases. Do not edit the same change from multiple workspaces.

Use `jj resolve --tool=:ours` or `:theirs` only when taking the entire selected side is semantically correct. Do not use
an external merge tool unless it is independently authorized and noninteractive for the intended operation.

## Immediate undo and redo

Every mutation is recorded in the operation log:

```bash
jj undo
jj redo
```

Repeated undo walks backward through operations; repeated redo walks forward through undone operations. Verify status,
graph, diff, bookmarks, and tags as relevant after each step.

## Inspect operations without snapshotting

```bash
jj --at-op=@ --ignore-working-copy --no-pager --color=never op log -n 20
jj --at-op=<operation-id> --no-pager --color=never status
jj --at-op=<operation-id> --no-pager --color=never log
```

Use `--ignore-working-copy` here only to avoid snapshotting current filesystem changes while inspecting historical
operations.

## Restore or revert operations

```bash
# Restore repository state to an earlier operation, undoing later operations
jj op restore <operation-id>

# Revert one selected operation while retaining later operations when possible
jj op revert <operation-id>
```

`op restore` can restore remote-tracking state as well as revisions. Inspect bookmarks and tags before any later push.
Do not garbage-collect or abandon operation history as routine cleanup.

## Recovery discipline

Before recovery:

1. capture current status, graph, diff, bookmarks, tags, and workspace list as relevant;
1. identify the exact bad operation and later work that must survive;
1. prefer the narrowest reversible action;
1. inspect the resulting operation with `jj op show -p`;
1. preserve unresolved or divergent user work instead of forcing a clean graph.
