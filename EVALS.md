# Evaluation Protocol

This repository treats evaluation as an empirical comparison, not a list of desirable answers. The protocol is designed
to distinguish four separate questions:

1. **Availability:** was the target skill installed and eligible under host policy?
2. **Selection:** did the host select it, or did the explicit invocation resolve correctly?
3. **Access:** did the agent actually load or use the distinctive skill procedure during execution?
4. **Outcome:** did the task satisfy an independent verifier?

A selected skill is not necessarily used correctly, and exact skill use is neither necessary nor sufficient for task
success. Record all four fields independently.

The design follows the failure surfaces highlighted by
[*Demystifying Agent Skills: A Comprehensive Evaluation of Skill Use in LLM Agents*](https://arxiv.org/abs/2608.14036)
(arXiv:2608.14036): procedural anchoring, retrieval under distractors, runtime verification, misapplication, and token
cost.

## Files

- `evals/cases.jsonl`: versioned case catalog.
- `.eval-results/runs.jsonl`: local trial records; ignored by Git.
- `scripts/eval_results.py`: validates catalogs and trials and summarizes results.
- `tests/`: static repository regression tests.

## Experimental arms

Run the same fixture and task under at least these arms:

- `raw`: target skill disabled or unavailable; no equivalent procedure pasted into the prompt.
- `skill`: target skill installed with repository metadata and invoked according to the case.
- `workflow-memory` (optional): a compact task-specific procedure supplied directly in the prompt without installing a
  skill, for comparison with procedural context that has no retrieval step.

Do not let one arm see outputs from another. Use a fresh host session for every trial.

## Trial count and controls

For each host/model/arm combination:

1. Run at least five independent trials for exploratory evaluation and more when rates are close or variable.
2. Reset the fixture to the same byte-for-byte state before each trial.
3. Keep user prompt, repository policy, available tools, network policy, and verifier constant across arms.
4. Record exact host and model versions. Do not pool materially different model versions without reporting them.
5. Randomize arm order when practical.
6. Preserve failed trajectories and their outcome labels; they are regression evidence, not disposable noise.

For implicit invocation, include both should-trigger and semantically similar near-miss prompts. For explicit-only skills,
measure whether explicit syntax resolves and whether ordinary-language near misses avoid external or destructive actions.

## Case categories

- `trigger`: should activate under the declared host policy.
- `near-miss`: resembles the skill domain but should not activate or should stop after a failed environment precondition.
- `procedure`: tests a distinctive ordered procedure or output contract.
- `failure`: starts from a failure state and tests stop, retry, or evidence semantics.
- `counterfactual`: probes a tempting but invalid interpretation of metadata or policy.

Each case supplies observable expectations. Convert them into fixture-specific verifiers rather than grading writing
style.

## Result record

Write one JSON object per trial to `.eval-results/runs.jsonl`:

```json
{
  "case_id": "jj-status-implicit",
  "skill": "jujutsu",
  "host": "codex",
  "model": "exact-model-and-version",
  "arm": "skill",
  "trial": 1,
  "available": true,
  "selected": true,
  "accessed": true,
  "success": true,
  "failure_category": null,
  "input_tokens": 1200,
  "output_tokens": 300,
  "wall_seconds": 8.4,
  "notes": "jj root succeeded; status and diff were observed"
}
```

`selected`, `accessed`, or `success` may be `null` only when the host exposes no reliable evidence. Explain the missing
instrumentation in `notes`. The `raw` arm cannot have `accessed: true` for the target skill.

## Evidence for selection and access

Prefer host traces, skill-access logs, debug logs, or explicit tool events. Do not infer access solely because the final
answer resembles the skill.

When host instrumentation is unavailable:

- set the field to `null` rather than guess;
- preserve any observable invocation message or command trace in the trial notes;
- keep outcome verification independent of activation inference.

## Outcome verification

Use an executable or independently inspectable verifier whenever possible:

- seeded repository defect is found or fixed;
- exact forbidden command is absent from a trace;
- required check actually ran and returned the expected result;
- output contains the required stable schema and evidence fields;
- dirty unrelated edits remain byte-identical;
- a mutation or known-bad fixture is caught by the surviving test;
- selected Jujutsu revisions, bookmarks, or tags match the requested set after mutation.

A test name, plausible command, or static code shape is not runtime evidence. A run with missing required evidence is not
a success even when the final prose claims success.

## Failure taxonomy

Use the narrowest applicable category in `failure_category`:

- `retrieval-miss`
- `wrong-skill`
- `skill-ignored`
- `skill-misapplied`
- `environment`
- `authentication`
- `network-policy`
- `service-lifecycle`
- `shell-corruption`
- `output-schema`
- `static-only-verification`
- `algorithmic`
- `timeout`
- `stale-target`
- `scope-drift`
- `unsafe-mutation`
- `verifier-error`
- `other:<specific-label>`

A successful trial uses `null` or `"none"`.

## Cost and latency

Record provider-reported input and output tokens when available, plus wall time. For `cross-agent`, also preserve
provider-reported currency cost in `notes` when exposed. Do not compare success rates without reporting the accompanying
cost and timeout rate.

## Running the repository checks

```sh
python scripts/validate_skills.py
python -m unittest discover -s tests -v
python scripts/eval_results.py check-cases evals/cases.jsonl
```

Validate and summarize recorded trials:

```sh
python scripts/eval_results.py check-results .eval-results/runs.jsonl
python scripts/eval_results.py summarize .eval-results/runs.jsonl
python scripts/eval_results.py summarize --json .eval-results/runs.jsonl
```

## Minimum release gate

Before changing invocation policy, deleting a failure warning, or expanding a skill's implicit scope:

1. static validation passes;
2. all repository unit tests pass;
3. trigger and near-miss cases are run on both hosts when the policy affects both;
4. raw and skill arms are compared on the affected procedural cases;
5. no material regression in downstream success, unsafe mutation, or token/latency budget is unexplained;
6. the change is linked in commit or pull-request notes to the observed failure or opportunity it addresses.

Do not claim that a skill improves outcomes until counterfactual trials support that claim.
