# Bookmarks, remotes, and tags

Read this before fetch, push, bookmark deletion or movement, or any tag operation. These are repository mutations and
may have remote-visible effects.

## Bookmarks

Bookmarks are movable revision names and Git branch counterparts. They do not generally advance when `new` or `commit`
creates a child.

```bash
jj --no-pager --color=never bookmark list --all-remotes
jj bookmark create feature-name --revision <revision>
jj bookmark advance 'exact:feature-name' --to @
jj bookmark advance 'exact:feature-name' --to @-
```

Use `bookmark advance` for normal forward movement. Backward or sideways movement requires explicit authorization and
inspection of both targets:

```bash
jj bookmark move 'exact:feature-name' --to <revision> --allow-backwards
```

Deletion and forgetting differ:

```bash
# Mark tracked remote counterparts for deletion on a later push
jj bookmark delete 'exact:feature-name'

# Remove only the local bookmark relationship
jj bookmark forget 'exact:feature-name'
```

A bookmark ending in `??` is conflicted. Inspect all local and remote targets before resolving it:

```bash
jj --no-pager --color=never bookmark list --all-remotes --conflicted
jj --no-pager --color=never log -r '<bookmark-name>'
```

## Clone, initialize, and colocation

```bash
jj git clone <url> [destination]
jj git init --colocate
jj git colocation status
```

Do not create repositories, change colocation mode, add remotes, or remap remotes unless the user requested it. Verify
version-specific clone tag flags from installed help.

## Fetch

Fetch updates remote-tracking state and tags according to repository and version behavior:

```bash
jj git fetch --remote origin

# Exact Git branch or tag names; these options use Git-ref patterns, not jj exact: patterns
jj git fetch --remote origin --branch <branch-name>
jj git fetch --remote origin --tag '<tag-name>'
```

After fetch, inspect before rebasing:

```bash
jj --no-pager --color=never status
jj --no-pager --color=never bookmark list --all-remotes
jj --no-pager --color=never tag list --all-remotes
jj --no-pager --color=never log -r 'trunk()..@'
```

## Tags

Tag creation, movement, deletion, tracking, and publication require explicit user intent because they can affect release
identity and later push selection.

```bash
jj --no-pager --color=never tag list --all-remotes
jj tag set release-name --revision <revision>
jj tag set release-name --revision <revision> --allow-move
jj tag delete 'exact:release-name'
jj tag track 'release-name@origin'
jj tag untrack 'release-name@origin'
```

Moving an existing tag, deleting a tracked tag, or changing tracking policy requires exact authorization. A local tag
deletion can become a remote deletion on a later push.

## Push safely

Push only when the user explicitly requests it.

Before push:

1. identify the intended remote and exact bookmark, tag, or change;
1. inspect local and remote bookmarks and tags;
1. confirm the selected references point at intended revisions;
1. verify descriptions, atomicity, conflicts, private revisions, and unrelated descendants under repository policy;
1. run a dry run and inspect its complete selection.

Exact bookmark:

```bash
jj git push --dry-run --remote origin --bookmark 'exact:feature-name'
jj git push --remote origin --bookmark 'exact:feature-name'
```

Exact tag on versions supporting tag push:

```bash
jj git push --dry-run --remote origin --tag 'exact:release-name'
jj git push --remote origin --tag 'exact:release-name'
```

One change under a generated bookmark:

```bash
jj git push --dry-run --remote origin --change @
jj git push --remote origin --change @

# When commit created a new empty @ and finished work is @-
jj git push --dry-run --remote origin --change @-
jj git push --remote origin --change @-
```

Avoid bare push, `--all`, `--tracked`, or `--deleted` unless the user intends the complete resolved set. On `jj 0.44`,
tracked tags can participate in default selection, `--all` includes tags, and `--tracked` includes tracked tags. Verify
installed help on other versions. Do not bypass protections such as empty-description, private-commit, or conflict
checks—including `--allow-conflicts`—without explicit authorization and a documented reason.

After push, re-list bookmarks and tags and report exactly what changed.
