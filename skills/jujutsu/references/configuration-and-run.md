# Configuration and external commands

Read this before changing configuration or using `jj run`, `jj bisect run`, configured fix tools, merge tools,
or diff
tools.

## Configuration

Read values through Jujutsu:

```bash
jj config get <name>
jj --no-pager --color=never config list [name]
jj config path --user
jj config path --repo
jj config path --workspace
```

Some `config path` commands may create secure external configuration directories. Call them only when the path
is
needed.

Persist configuration only when explicitly requested, at the narrowest scope:

```bash
jj config set --user <name> <toml-value>
jj config set --repo <name> <toml-value>
jj config set --workspace <name> <toml-value>
```

Do not use `jj config edit` unattended. Do not edit legacy files under `.jj/`; repository and workspace
configuration
may live in secure external locations. After setting a value, read it back from the intended scope and verify
side
effects.

## External-command authorization

`Bash(jj *)` or permission to run `jj` does not authorize a hidden child command. Before any external command
through
Jujutsu:

1. confirm the exact executable and arguments are independently authorized;
1. inspect the selected revision set;
1. decide whether filesystem changes may be saved into history;
1. prevent secrets, network access, or destructive behavior not permitted for a direct call;
1. choose explicit job count and clean-workspace behavior when reproducibility matters.

Never use `jj util exec` during agent operation.

## `jj run`

`jj run` executes an external command in an isolated working copy for each selected revision. By default,
tracked-file
changes may amend selected revisions, so it is a history mutation rather than merely a test runner.

For a deliberately mutating run:

```bash
jj run --revision 'mutable() & trunk()..@' --clean -- <authorized-command> [args...]
jj --no-pager --color=never op show -p
```

For read-only checks on versions supporting it, prefer `--ignore-changes`; modifications made by the child
command are
discarded:

```bash
jj run --revision 'trunk()..@' --ignore-changes --clean -- <authorized-test-or-lint-command> [args...]
```

On `jj 0.44`, revisions start oldest-first, `--ignore-changes` prevents revisions from being edited, and
`--ignore-errors` continues after failures. Do not use `--ignore-errors` for a quality gate because the
overall run no
longer stops at the first failing revision. Verify installed help on other versions.

Do not use `--passthrough`, parallel jobs, or a configured tool merely for convenience. Choose them only when
their
output, ordering, isolation, and permissions are understood.

## Verification

After a mutating external-command workflow, choose checks relevant to its effects; do not automatically run
every command below:

```bash
jj --no-pager --color=never op show -p
jj --no-pager --color=never status
jj --no-pager --color=never log -r '<selected-revset>'
jj --no-pager --color=never diff --git
```

Report child-command failures per revision and any history edits separately.
