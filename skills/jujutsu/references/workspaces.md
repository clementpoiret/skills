# Workspaces

A workspace is a working copy attached to a shared Jujutsu repository. Each workspace has its own working-copy revision
and sparse patterns; revisions, operations, bookmarks, tags, and remote-tracking state are shared.

Creating, forgetting, renaming, or deleting a workspace requires explicit user intent.

## Inspect

```bash
jj --no-pager --color=never workspace list
jj workspace root --name <workspace-name>
```

## Add

```bash
# New workspace whose @ normally shares the current @'s parent or parents
jj workspace add ../my-tests

# Named workspace at an explicit base with a noninteractive description
jj workspace add --name tests --revision <revision> -m "<description>" ../my-tests
```

Inspect destination existence, requested base, and shared repository state first. Do not create a workspace merely to
hide uncertain changes.

## Forget or rename

```bash
# Forget metadata; does not delete files on disk
jj workspace forget <workspace-name>

# Rename current workspace
jj workspace rename <new-name>
```

Do not delete a workspace directory until metadata handling and preservation of any filesystem changes are clear.

## Avoid shared working-copy changes

Do not use `jj edit <revision>` in two workspaces at once. Rewriting one workspace's working-copy change from another
can make the first stale. Use separate logical changes when concurrent work is necessary.

## Recover a stale workspace

```bash
jj workspace update-stale
jj --no-pager --color=never status
jj --no-pager --color=never log -r '@ | divergent()'
```

Recovery may create a divergent revision or preserve stale work under another version. Numeric suffixes such as `/0` and
`/1` identify divergent versions. Inspect all versions and preserve user work before resolving divergence.

## Verify

After any workspace mutation:

```bash
jj --no-pager --color=never workspace list
jj --no-pager --color=never status
jj --no-pager --color=never log -r '@ | divergent()'
```
