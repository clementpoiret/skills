# Evaluation Protocol

This repository evaluates marginal verified value, not whether a skill sounds useful or was invoked. Keep the model,
harness, task, repository revision, tools, budget, and verifier fixed across arms.

Record these events independently:

1. **Availability:** was the target skill installed and eligible?
2. **Selection:** did the host select it or resolve explicit invocation?
3. **Access:** did the agent load the target `SKILL.md`?
4. **Procedural adherence:** did the trajectory exhibit the distinctive intervention?
5. **Verifier result:** did the independent executable or inspectable verifier pass?
6. **Outcome:** did the complete task succeed without unacceptable scope, safety, or regression failure?

Selection is not adherence, and adherence is not correctness.

## Files

- `evals/cases.jsonl`: routing and procedural case catalog.
- `evals/fixtures/`: deterministic representative workspaces and independent verifiers.
- `.eval-results/runs.jsonl`: local trial records; ignored by Git.
- `scripts/eval_results.py`: validates and summarizes trial records.
- `scripts/eval_fixtures.py`: validates, materializes, and verifies executable fixtures.
- `tests/`: repository, schema, and verifier regression tests.

## Experimental arms

Run at least:

- `no-skill`: target skill unavailable; do not paste an equivalent procedure into the task.
- `skill`: target skill installed with its normal metadata and invocation policy.
- `wrong-skill`: withhold the target and supply one deliberately confusable skill to measure interference.
- `workflow-memory` (optional): paste a compact task-specific procedure without installing a skill, separating procedural
  context from routing and standard skill format.

Do not let one arm see another arm's output. Start from a fresh host session and byte-identical fixture every trial.

## Trial design

For each host/model/arm combination:

1. Use at least five independent trials for exploratory evaluation; increase trials when rates are close or variable.
2. Pin exact model, host, repository, fixture, tool permissions, network policy, reasoning effort, and stopping rule.
3. Randomize arm order when practical.
4. Preserve failed trajectories and outcome labels.
5. Blind skill authors to held-out tasks where possible.
6. Report paired confidence intervals or task-level paired analyses before claiming lift.
7. Compare verified success and regression avoidance first; report token, tool, test, turn, latency, and skill-context cost
   beside outcome.

The estimand is:

```text
P(success | same model, harness, task, budget, tools, skill)
-
P(success | same model, harness, task, budget, tools, no skill)
```

## Case categories

- `trigger`: clear positive routing case.
- `near-miss`: similar language where the skill must not activate or must stop after a failed precondition.
- `confusable`: distinguishes a neighboring skill and names it in `confusable_with`.
- `procedure`: tests the distinctive ordered behavior.
- `failure`: starts from a failure state and tests diagnostic or stop semantics.
- `escape`: invalidates procedure assumptions and requires re-localization, abstention, or a bounded result.
- `counterfactual`: probes a tempting but invalid policy interpretation.

Every skill has trigger, near-miss, procedure, and failure/escape coverage. Primary skills also include confusable and
counterfactual cases. Use `check-cases` to report the current catalog size.

## GPT-6 Astra and Fable 5.1 trials

Evaluate each target separately; a result on one model does not validate the other.

| Host | Target model | Initial effort | Additional trials |
| --- | --- | --- | --- |
| Codex | `gpt-6-astra` | Preserve the configured supported setting | Sweep available levels only with a fixed workload and budget. |
| Claude Code | `claude-fable-5-1` | Preserve the configured setting; otherwise `high` | Include lower effort for routine tasks and higher effort where quality warrants it. |

Record the effective model identifier and host version from observable runtime evidence. A requested alias alone is
insufficient to claim the target ran. Keep each effort/harness configuration in a separate results file: the current
summarizer pairs by model, host, case, and trial and does not distinguish effort or harness versions. Record those
settings and the skill revision in `notes`; never pool differing configurations into a paired result.

Run the full catalog and the five executable fixtures, then pay particular attention to these cases:

| Behavior | Cases | Evidence to inspect |
| --- | --- | --- |
| Authorized completion | `gi-authorized-follow-through`, `cc-settled-decisions`, `jj-existing-authorization` | Work proceeds through already authorized steps. |
| Partial blockers | `gi-independent-obligations` | Independent work completes before a focused blocking question. |
| Verification cost | `gi-final-state-checks`, `rd-existing-regression`, `sg-completed-scope`, `st-sensitivity-complete`, `pgo-target-met` | Required checks remain intact; repeated checks have a concrete cause. |
| Scope and output | `pr-assessment-only`, `sg-user-budget`, `st-user-scope` | User scope is honored and evidence is concise. |
| Oracle discipline | `sg-r3-missing-contract`, `sg-security-documented-basis`, `sg-no-evidence-budget`, `sgt-independent-obligations` | Scope completion and evidence limits remain explicit without artificial candidate quotas. |
| Tool and peer behavior | `gi-independent-reads`, `ca-target-model-unavailable`, `ca-continue-primary-analysis` | Independent reads can batch; target models are observable; the reviewed target remains stable. |

These cases express expected behavior, not recorded outcomes. Static validation and an isolated agent smoke test do not
replace paired trials on both target models.

### Host integration checks

These checks apply only to custom API harnesses; skill text cannot configure the host or authenticate a model.

- GPT-6 Astra tool calls require Responses. Confirm the adapter's actual endpoint and supported parameters before
  model trials. See [OpenAI's migration guidance](https://developers.openai.com/api/docs/guides/latest-model#migration-quickstart).
- For Fable 5.1, preserve API conversation history as returned and use supported compaction. Do not splice old thinking
  blocks into edited histories. Confirm how the client exposes progress updates and supports tool selection. See
  [Anthropic's migration guide](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide).
- Keep host policies and permissions fixed across arms. A missing provider connection, model entitlement, or tool is an
  environment limitation, never a successful model trial. Do not route around a refusal or silently switch models.

## Executable fixtures

List and self-check fixtures:

```sh
python scripts/eval_fixtures.py list
python scripts/eval_fixtures.py check
```

Materialize a clean candidate workspace without copying the hidden verifier into it:

```sh
python scripts/eval_fixtures.py materialize grounded-implementation-single-use-token /tmp/gi-trial
cat /tmp/gi-trial/TASK.md
```

After an agent run, verify the candidate **inside the same disposable sandbox used for the trial**. Workspace verifiers
execute candidate code and therefore fail closed unless this risk is explicitly acknowledged:

```sh
python scripts/eval_fixtures.py verify grounded-implementation-single-use-token /tmp/gi-trial \
  --allow-untrusted-code
```

Do not use `--allow-untrusted-code` on a developer workstation or any environment containing credentials, valuable files,
or unrestricted network access. The flag is an acknowledgement, not a sandbox. For the artifact-mode review fixture,
the verifier only parses the supplied JSON artifact and does not require the flag. Materialization refuses destinations
inside a fixture directory so the hidden verifier is not exposed beside the trial.

Current fixtures:

| Fixture | Skill | Primary verifier property |
| --- | --- | --- |
| `grounded-implementation-single-use-token` | `grounded-implementation` | Hidden requirement checks, preserved non-consuming verification, no dependency/scope change. |
| `reproduction-first-config-flag` | `reproduction-first-debugging` | Root-cause parser fix, original reproduction repaired, no caller special-case. |
| `precision-review-tenant-cache` | `precision-review` | Detect one real tenant-isolation defect while rejecting contract-contradicted findings. |
| `specification-grounded-testing-resource-id` | `specification-grounded-testing` | Accept two independently correct implementations, reject five distinct contract violations, and forbid production edits. |
| `profile-guided-optimization-first-match` | `profile-guided-optimization` | Preserve first-match/duplicate/cache semantics while meeting deterministic operation-count and scaling budgets. |

These fixtures are representative smoke tests, not a sufficient task distribution.

## Result record

Write one JSON object per trial:

```json
{
  "case_id": "rd-config-flag-fixture",
  "skill": "reproduction-first-debugging",
  "host": "codex",
  "model": "exact-model-and-version",
  "arm": "skill",
  "trial": 1,
  "available": true,
  "selected": true,
  "selected_skill": "reproduction-first-debugging",
  "accessed": true,
  "procedure_adherent": true,
  "verifier_passed": true,
  "success": true,
  "failure_category": null,
  "input_tokens": 12000,
  "output_tokens": 4500,
  "skill_tokens": 2100,
  "tool_calls": 18,
  "test_invocations": 4,
  "trajectory_turns": 9,
  "wall_seconds": 95.2,
  "notes": "Original failure reproduced before first production edit; verifier passed."
}
```

Boolean evidence may be `null` only when instrumentation cannot establish it. Explain why in `notes` rather than
guessing. Numeric fields may be `null` when the host does not expose them.

Arm semantics:

- `no-skill`, `workflow-memory`, and `wrong-skill` must withhold the target skill.
- `no-skill` and `workflow-memory` cannot select or access the target and consume zero target skill tokens.
- `wrong-skill` records the confusable skill in `selected_skill`; it must differ from the target and, when the case names
  `confusable_with`, must be one of those declared neighbors.
- `skill` makes the target available. Near-miss cases may correctly have `selected: false`.
- `procedure_adherent` may be true in the no-skill arm if the model performs the procedure without the skill; this is
  essential for measuring marginal value against a strong baseline.

## Procedural adherence evidence

Prefer host traces, commands, edit timing, and tool outputs. Examples:

- debugging: the original reproduction runs before the first production edit; competing hypotheses and a discriminating
  experiment are observable; the original reproduction reruns after the patch;
- implementation: requirements are extracted before significant edits; callers/versions/generated boundaries are
  inspected when triggered; every obligation has observed verification;
- review: target and intent are fixed; affected callers and tests are inspected; unsupported suspicions are suppressed;
- testing: an authoritative obligation matrix precedes test edits; production remains unchanged; known-valid behavior
  passes and independently wrong behavior or a targeted mutation fails;
- optimization: the representative workload and correctness baseline run before production edits; profile or deterministic
  cost evidence identifies one bottleneck; the same benchmark and guardrails decide keep/revert;
- version safety: manifest/lock/resolved source is inspected before relying on an API;
- escape: the agent stops or re-localizes when procedure assumptions become false.

Do not infer adherence from polished final prose alone.

## Outcome verification

Use an executable or independently inspectable oracle whenever possible:

- hidden/acceptance tests and pass-to-pass regression tests;
- compile/type/static/package/build results;
- original failure reproduction and regression test;
- mutation, known-bad replay, property, fuzz, race, sanitizer, or benchmark evidence when matched to the failure mode;
- review precision/recall against independently validated defect mechanisms;
- exact output schema and forbidden-action checks;
- preservation of unrelated dirty changes.

A test name, plausible command, or static code shape is not runtime evidence. Missing required evidence means the complete
outcome is not a success even when the final answer says “done.”

## Failure taxonomy

Use the narrowest applicable `failure_category`:

- `retrieval-miss`
- `wrong-skill`
- `skill-ignored`
- `skill-misapplied`
- `procedure-not-followed`
- `environment`
- `authentication`
- `network-policy`
- `service-lifecycle`
- `shell-corruption`
- `output-schema`
- `static-only-verification`
- `visible-test-overfit`
- `oracle-contamination`
- `version-mismatch`
- `unrepresentative-workload`
- `benchmark-noise`
- `performance-guardrail`
- `algorithmic`
- `timeout`
- `stale-target`
- `scope-drift`
- `unsafe-mutation`
- `regression`
- `verifier-error`
- `other:<specific-label>`

Successful trials use `null` or `"none"`; failed trials must record a category. A complete `success: true` requires an
independently observed `verifier_passed: true`.

## Summaries

Validate and summarize:

```sh
python scripts/eval_results.py check-results .eval-results/runs.jsonl
python scripts/eval_results.py summarize .eval-results/runs.jsonl
python scripts/eval_results.py summarize .eval-results/runs.jsonl --json
```

The validator links every result to `evals/cases.jsonl`, rejects case/skill mismatches, and checks declared confusable
neighbors for wrong-skill arms. The summary keeps routing, access, adherence, verifier pass, and complete success
separate. It reports mean resource use plus paired deltas only for records with the same target skill, host, model, case,
and trial number in the `no-skill` arm; unmatched records remain visible in aggregate rates but do not affect paired
deltas.

## Minimum promotion gate

Before declaring a skill effective, expanding implicit scope, or removing a failure warning:

1. structural validation, unit tests, case-catalog validation, and fixture self-tests pass;
2. trigger, near-miss, and confusable routing cases run on both hosts when both are targeted;
3. the candidate is compared with `no-skill` on representative executable tasks;
4. important skills include a `wrong-skill` interference arm;
5. verified success or regression-free correctness improves by a practically meaningful amount;
6. false-positive burden, unsafe scope, token/context growth, tool calls, test invocations, and latency remain acceptable;
7. negative and null results are retained and reported;
8. the observed evidence is linked to the skill revision.

Do not claim GPT-6 Astra or Claude Fable 5.1 benefit from these files until matched trials support that claim.
