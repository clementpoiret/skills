# Revision descriptions

Read this before creating, changing, squashing, or publishing a nonempty revision.

## Authority

Use the first applicable source:

1. explicit current user instruction;
1. repository policy such as `AGENTS.md`, contribution guidance, or release tooling;
1. owning-component convention established by nearby accepted history;
1. otherwise, a concise imperative summary that states the actual logical change.

Jujutsu does not require Conventional Commits. Use Conventional Commits only when one of the authorities above requires
or requests them.

## Quality gate

Every nonempty project revision should:

- represent one logical change;
- have a truthful, specific first line;
- use the repository's required issue IDs, scopes, trailers, or generated format;
- identify breaking behavior when policy requires it;
- avoid descriptions such as `changes`, `fix stuff`, or claims unsupported by the diff;
- avoid an editor or TUI in unattended operation.

Inspect the revision before describing it:

```bash
jj --no-pager --color=never show <revision>
jj --no-pager --color=never diff --git -r <revision>
```

## Noninteractive commands

```bash
jj describe -m "<repository-compliant description>"
jj describe -r <revision> -m "<repository-compliant description>"
jj new -m "<repository-compliant description>"
jj commit -m "<repository-compliant description>"
```

For squash, avoid an interactive message merge:

```bash
# Preserve the destination description
jj squash --use-destination-message

# Set a deliberate resulting description
jj squash -m "<repository-compliant description>"
```

## When Conventional Commits is required

Use the repository-specified version and types. A common form is:

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

Do not assume a universal type list or capitalization rule when repository policy overrides it. Inspect nearby accepted
history and validation tooling. Before publication, list the stack's first lines and correct only the revisions owned by
the current task:

```bash
jj --no-pager --color=never log -r 'trunk()..@' \
  -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
```
