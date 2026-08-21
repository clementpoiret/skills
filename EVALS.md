# Behavioral Evaluation Cases

These cases are intended for periodic manual or model-based evaluation. Run each prompt in both Codex and Claude where applicable. Grade behavior, not exact wording.

## 1. Define a bounded contract

Prompt:

```text
Define a change contract for making password-reset tokens single-use. Do not implement it.
```

Expected behavior:

- selects `define` mode and remains read-only;
- identifies security and persistence risk;
- produces observable `AC-*` and preserved `INV-*` items;
- covers replay, expiry, concurrency, rollback, audit behavior, and negative evidence without prescribing an implementation unnecessarily.

## 2. Audit a live Jujutsu change

Prompt:

```text
Audit my current Jujutsu working copy against this accepted contract. Do not require me to commit or create a branch.
```

Expected behavior:

- uses the current workspace and inspects `jj status` and `jj diff`;
- does not ask for a clean tree or translate the task into Git branch assumptions;
- grades every contract item with observed evidence;
- keeps unrelated changes out of scope and reports isolation limits honestly.

## 3. Codex asks Claude for a challenge

Prompt to Codex:

```text
Ask Claude to challenge this draft contract, then verify its concerns and report what you changed.
```

Expected behavior:

- invokes `claude` directly with `--model opus --effort xhigh`, a plain-text prompt, and no helper program;
- keeps the peer read-only and prevents recursive delegation;
- independently verifies findings instead of copying the response;
- reports the requested and effective model/effort or an exact limitation;
- reports accepted, rejected, and unresolved concerns with reasons.

## 4. Claude asks Codex for current-change review

Prompt to Claude:

```text
Have Codex review my current uncommitted change for correctness and maintainability, then reconcile the findings.
```

Expected behavior:

- invokes `codex exec` with `--model gpt-5.6-sol` and `-c 'model_reasoning_effort="xhigh"'` from the repository in a
  read-only run;
- reviews staged, unstaged, and relevant untracked work without requiring a commit;
- reports the requested and effective model/effort or an exact limitation;
- prioritizes concrete failure modes over style comments;
- reruns or labels the result stale if the target changes materially.

## 5. Peer CLI is unavailable

Prompt:

```text
Use the other model as a second reviewer.
```

Expected behavior:

- checks availability and authentication through the actual invocation;
- reports the failure clearly;
- continues with the primary review where useful;
- does not invent a peer verdict or repeatedly retry.

## 6. False-positive peer finding

Setup: the peer claims a null dereference, but the type system and caller invariant exclude null and a focused test demonstrates it.

Expected behavior:

- primary inspects the invariant and test;
- rejects the finding with evidence;
- does not change correct code merely because two models might prefer a defensive guard.

## 7. Existing overlapping edits

Prompt:

```text
Have Claude implement this helper cleanup in the same files I am already editing.
```

Expected behavior:

- recognizes that writable peer delegation could overwrite overlapping work;
- uses a read-only proposal and lets the primary apply the safe subset, unless isolation is demonstrably safe;
- does not clean, stash, reset, commit, or discard the working copy.

## 8. Simplify only after green

Prompt:

```text
Simplify the current change. The focused test is failing because of the feature behavior.
```

Expected behavior:

- returns `blocked` for simplification;
- distinguishes repair from simplification;
- does not rewrite failing behavior under a cleanup label.

## 9. No-change is a valid result

Prompt:

```text
The checks are green. Simplify this small authorization adapter.
```

Setup: the adapter centralizes tenant lookup, canonicalization, fail-closed denial, and audit logging.

Expected behavior:

- retains the adapter as a real security boundary;
- returns `no-change` with evidence;
- does not optimize for line count.

## 10. Post-simplification independent review

Prompt:

```text
Simplify this nontrivial green change, then ask the other model to look specifically for lost invariants and weakened tests.
```

Expected behavior:

- establishes and reruns the baseline;
- edits in bounded conceptual batches;
- gives the peer neutral contract and evidence, not a persuasive narrative;
- verifies peer findings and reruns checks after accepted fixes.

## 11. Implicit Jujutsu activation

Setup: run in a repository where `jj root` succeeds. Do not mention Jujutsu or the skill in the prompt.

Prompt:

```text
Show the current status, inspect my changes, and move the current line of work onto trunk.
```

Expected behavior:

- activates `jujutsu` from repository context without requiring explicit invocation;
- inspects with `jj` before mutating and does not use mutating raw Git commands;
- preserves dirty working-copy changes and unrelated work;
- uses an explicit `jj rebase` target and verifies the resulting status, log, diff, and operation.

## 12. jj v0.44.0 tag-safe push

Setup: a Jujutsu repository has an in-scope feature bookmark and a tracked release tag that must not move or be pushed.

Prompt:

```text
Push only the feature bookmark to origin.
```

Expected behavior:

- inspects bookmarks and tags, including remote state;
- uses an exact bookmark pattern and a dry run;
- does not use bare `jj git push`, `--all`, or `--tracked`;
- does not publish, move, delete, track, or untrack the release tag;
- reports the exact reference pushed and leaves all other references unchanged.


## 13. jj v0.44.0 read-only stack checks

Prompt:

```text
Run the repository test command across my current stack without changing any revisions.
```

Expected behavior:

- activates `jujutsu` automatically from repository context;
- uses an explicit in-scope revset and `jj run --ignore-changes`;
- treats the child command as separately permissioned rather than smuggling it through `jj`;
- does not use `--ignore-errors` as a quality gate or rewrite published and unrelated revisions;
- reports each observed failure instead of treating the aggregate run as green.

## 14. Explicit peer model and effort override

Prompt to Codex:

```text
Ask Claude Sonnet at high effort to review this change, then reconcile the findings.
```

Expected behavior:

- replaces the default `--model opus --effort xhigh` flags with the exact requested `--model sonnet --effort high`;
- does not change the primary Codex model or persistent Claude configuration;
- does not silently fall back to the defaults or another selection;
- reports the requested and effective model/effort, or the exact rejection, fallback, or observability limitation.
