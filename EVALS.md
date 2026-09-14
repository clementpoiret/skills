# Evaluation protocol

Measure verified task success and unwanted work, not whether a skill sounds helpful. Shorter instructions are a measured size change, not proof of a better model outcome.

## Assets and local checks

`evals/cases.jsonl` contains 123 expected-behavior cases: the original 115 plus eight rewrite-specific cases. These are prompts and expectations, not recorded model results. The five original executable fixtures, their verifiers, and the evaluation runner/results utilities are retained unchanged.

```sh
python scripts/eval_results.py check-cases evals/cases.jsonl
python scripts/eval_fixtures.py list
python scripts/eval_fixtures.py check
python -m unittest discover -s tests -v
```

The catalog covers trigger, near-miss, confusable, procedure, failure, escape, and counterfactual behavior. The new cases target trivial edits, implementation versus unavailable verification, unsolicited workflow chaining, known nonconformance plus missing evidence, remote-tool restrictions, configured peer models, lightweight `jj status`, and reuse of valid test-sensitivity evidence.

## Compare original, revised, and no-skill behavior

Use fresh sessions and byte-identical fixtures. Pin the exact model and host version, skill revision, reasoning effort, tools, permissions, network policy, environment, budget, and stopping rule. Observe the effective model; a requested alias alone is not runtime confirmation. Evaluate different models separately.

Use these supported arms:

| Arm | Exposure |
| --- | --- |
| `no-skill` | Target skill unavailable; do not paste an equivalent procedure. |
| `skill` | Target skill installed with its normal description and invocation policy. |
| `wrong-skill` | Target withheld and a deliberately confusable skill available. |
| `workflow-memory` | Optional compact task-specific procedure without the skill packaging. |

To compare this rewrite with the original, keep **separate result files for each skill revision and host/effort configuration**, each including its matched no-skill baseline. The current summarizer pairs by model, host, case, and trial, not by skill revision, effort, or harness configuration. Do not pool differing configurations or invent unsupported `original`/`revised` arm values.

Use the same global instructions when isolating a skill revision. Compare the two global policies separately with the skills held fixed; compare the complete original and revised bundles only when measuring the combined change. Ensure the no-skill arm does not inherit a copied skill workflow through global or project instructions.

Randomize arm order and prevent one arm from seeing another's output. Five trials per case/configuration can serve as an exploratory starting point, not a statistical guarantee. Preserve negative results and increase trials when variability makes the decision uncertain. Use held-out tasks and task-level paired analysis before claiming improved success, efficiency, or regression avoidance.

Track availability, selection, actual instruction access, procedural adherence, independent verifier outcome, and complete task success separately. Selection is not adherence; adherence is not correctness. Compare token/tool/test/turn counts and latency alongside success. Do not count unauthorized scope expansion as success, and do not treat unavailable measurements as zero.

## Executable fixtures and safety

| Fixture | Decisive property |
| --- | --- |
| `grounded-implementation-single-use-token` | Single-use consumption with preserved non-consuming verification and scope. |
| `reproduction-first-config-flag` | Parser root-cause repair rather than a caller workaround. |
| `precision-review-tenant-cache` | One real tenant-isolation finding without unsupported findings. |
| `specification-grounded-testing-resource-id` | Correct alternatives accepted, incorrect variants rejected, production unchanged. |
| `profile-guided-optimization-first-match` | First-match/duplicate semantics plus deterministic operation and scaling budgets. |

Materialize a fresh candidate workspace; the helper excludes the hidden verifier:

```sh
python scripts/eval_fixtures.py materialize grounded-implementation-single-use-token /tmp/gi-trial
```

After the model completes the task, verify it **inside the disposable sandbox used for the trial**:

```sh
python scripts/eval_fixtures.py verify grounded-implementation-single-use-token /tmp/gi-trial \
  --allow-untrusted-code
```

This flag acknowledges that the verifier executes candidate code; it does not provide a sandbox. Do not use it around credentials, valuable files, production access, or unrestricted network access. The artifact-mode review verifier parses its JSON input without this flag. Materialization and schema checks are not evidence of candidate correctness.

These fixtures are representative smoke tests, not a sufficient real-world task distribution. CLI peer and Jujutsu command recipes additionally need host/version-specific checks in a controlled environment.

## Record and summarize trials

Write one JSON object per trial. The following is a schema example, **not a run performed for this revision**:

```json
{
  "case_id": "rd-config-flag-fixture",
  "skill": "reproduction-first-debugging",
  "host": "codex",
  "model": "observed-model-identifier",
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
  "input_tokens": null,
  "output_tokens": null,
  "skill_tokens": null,
  "tool_calls": null,
  "test_invocations": null,
  "trajectory_turns": null,
  "wall_seconds": null,
  "notes": "SCHEMA EXAMPLE ONLY. Actual records must identify skill/global revisions, effort, harness, and supporting trajectory."
}
```

Use `null` for an unobserved field where the schema allows it, not an invented outcome. Record pre-inference/provider/environment failures with their appropriate failure category. Keep failed trajectories; do not silently switch to another model or retry billable calls to improve the success rate.

```sh
python scripts/eval_results.py check-results .eval-results/revised-config-a.jsonl
python scripts/eval_results.py summarize .eval-results/revised-config-a.jsonl --json
```

The summarizer reports recorded data; it does not conduct trials, establish statistical significance, or validate a skill from its metadata. This revision remains behaviorally unvalidated until live comparative trials establish its effects.
