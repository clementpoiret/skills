# Version compatibility

The core skill was reviewed against `jj 0.44.0` on 2026-08-24. This is a maintenance statement, not a guarantee that
0.44.0 is the newest release when the skill is used.

## Installed help is authoritative

Always observe:

```bash
jj version
jj help <command>
jj help <command> <subcommand>
```

Before using a version-sensitive flag, confirm it appears in installed help and inspect its semantics. Do not translate
old examples mechanically when defaults or selection behavior changed.

## Compatibility procedure

When installed version differs from the audited version:

1. classify the requested operation as read-only, local rewrite, reference mutation, network mutation, configuration, or
   external-command execution;
1. list every flag and default on which the planned command relies;
1. verify those items in installed help;
1. run a read-only preview or `--dry-run` where supported;
1. reduce to a more explicit command when selection behavior is uncertain;
1. stop and report the incompatible assumption rather than guess.

## Notable 0.44 behavior used by these references

Verify these on other versions:

- Git tag fetch and push support is stable; fetched tags are tracked by default.
- `jj tag track` and `jj tag untrack` manage remote tag tracking.
- bare/default push selection and `--all` or `--tracked` can include tags.
- `jj git push --allow-conflicts` exists but bypassing conflict protection still requires explicit authorization.
- `jj run` supports `--ignore-changes`, `--ignore-errors`, and `--passthrough`.
- `jj run` starts selected revisions oldest-first; parallel completion order may still differ.
- clone/fetch tag-selection flags and patterns must be checked because older options may have changed or been removed.

## Maintaining this skill

When updating the audited version:

1. read every intervening official changelog entry;
1. compare installed `help` for every command shown in the core and references;
1. run the repository's static validator and evaluation cases;
1. add a regression case for every changed default that could broaden mutation or publication scope;
1. update the reviewed version and date only after those checks pass.
