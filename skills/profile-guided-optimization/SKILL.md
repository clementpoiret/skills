---
name: profile-guided-optimization
description: Improve the measured performance or resource use of already-correct repository behavior through a representative workload, reproducible baseline, profiling, one bottleneck hypothesis at a time, and keep-or-revert verification. Use when optimization is the primary objective. Do not use for reported performance regressions requiring diagnosis, new feature implementation with a performance constraint, read-only review, test-suite simplification, or work without a defensible workload and observable metric.
compatibility: Intended for Codex and Claude Code sessions that can inspect repository-local performance contracts, execute correctness checks and representative benchmarks, and use available profilers or deterministic cost probes.
metadata:
  assurance-validation-status: "unvalidated-candidate"
  assurance-eval-catalog: "evals/cases.jsonl"
user-invocable: true
disable-model-invocation: false
---

# Profile-Guided Optimization

Optimize observed bottlenecks, not plausible code. Keep a change only when comparable measurements show useful
improvement without violating correctness or resource guardrails.

## Applicability

Use this as the primary procedure when the user asks to improve latency, throughput, CPU, memory, allocation, I/O,
contention, startup, build time, or another explicit performance/resource outcome of behavior that is already accepted as
correct.

This procedure may include building or repairing a benchmark when measurement is part of the optimization task. It may
compose with:

- `jujutsu` for VCS mechanics when `jj root` succeeds;
- an explicitly invoked `change-contract` that supplies accepted functional and performance obligations;
- an explicitly invoked `cross-agent` that independently challenges workload validity or the bottleneck hypothesis.

Use at most one primary task-family skill. Do not also apply `grounded-implementation`,
`reproduction-first-debugging`, `precision-review`, or `specification-grounded-testing` unless the task changes family.

## Do not use when

- A reported slowdown or performance regression must be reproduced and diagnosed. Use
  `reproduction-first-debugging`; its triggered performance branch owns the causal repair.
- The task adds new behavior or changes a contract, even when it includes a performance requirement. Use
  `grounded-implementation` and treat performance as one obligation.
- The task is a read-only performance review of a diff or revision. Use `precision-review`.
- The goal is to remove or merge slow tests after a green baseline. Use explicit `simplify-tests-after-green`.
- The request is generic cleanup, lower line count, or “make it faster” with no user-relevant workload or measurable
  proxy that can be established.
- Correctness is already failing or unknown at the target boundary. Establish the behavioral baseline or switch to the
  appropriate implementation/debugging procedure first.
- The only proposed evidence is intuition, asymptotic appearance, a single noisy timing, or an unrepresentative toy
  microbenchmark.

## Invariants

Maintain these throughout the task:

- Accepted functional, security, compatibility, reliability, and data behavior remains unchanged.
- The workload, metric, environment, and measurement method remain comparable before and after each candidate.
- Profile evidence precedes production optimization unless a deterministic cost model already identifies the bottleneck.
- Change one measured bottleneck per experiment so the effect remains attributable.
- No cache, dependency, concurrency, batching, approximation, or complexity increase is retained without measured value
  and explicit guardrail checks.
- A candidate whose improvement is indistinguishable from noise, shifts unacceptable cost elsewhere, or regresses
  correctness is reverted.
- Completion requires observed benchmark and correctness evidence, not a faster-looking implementation.

## 1. Define the performance contract

Before editing, record:

```text
PERF-1 Outcome: <user-visible or system objective>
Representative workload: <input sizes/distribution, concurrency, state, warm/cold conditions>
Primary metric: <latency statistic, throughput, CPU, allocations, memory, I/O, operations, build time>
Baseline command and environment: <exact reproducible setup>
Target or decision rule: <required threshold or material improvement beyond variance>
Correctness guardrails: <tests, contracts, output equivalence, error behavior>
Resource guardrails: <memory, tail latency, startup, network, storage, cost, fairness>
```

Prefer user-visible outcomes and production-shaped workloads. Use a proxy only when the relationship to the real outcome
is explicit and testable.

Establish, as relevant:

- data size, distribution, cardinality, hit/miss ratio, and adversarial cases;
- concurrency, request mix, burstiness, cache state, and warm-up;
- runtime, compiler, dependency, build, hardware, operating-system, and configuration versions;
- p50, tail, throughput, allocation, peak memory, CPU, I/O, lock wait, or deterministic operation counts according to
  the actual objective;
- permitted output, API, approximation, and resource trade-offs.

If the user did not supply a target, do not invent an SLO. Define a keep/revert rule based on repeatability, practical
materiality, and guardrails.

## 2. Establish correctness and measurement baselines

Before production edits:

1. Determine repository root, VCS state, unrelated edits, and allowed scope.
2. Run the cheapest relevant correctness suite and record pre-existing failures.
3. Locate repository-native benchmark, load, trace, profile, or build commands. Inspect their fixtures, data generation,
   setup/teardown, and version assumptions.
4. Run the representative benchmark enough to estimate variance or use its established statistical protocol. Preserve
   raw observations, not only one aggregate number.
5. Separate setup, warm-up, compilation, cache population, network, and measured work when the distinction matters.
6. Confirm the benchmark result changes when the intended work changes; calibrate harness overhead when it could dominate.

Prefer deterministic operation counts, allocation counts, query counts, or profiler samples when wall time is too noisy.
Do not compare runs made with different code generation, dependency resolution, CPU affinity, service state, or workload
unless that difference is the variable under test.

If correctness fails, the workload cannot be reproduced, or measurement is dominated by uncontrolled infrastructure,
return `blocked` or switch task family rather than optimize from invalid evidence.

## 3. Profile before optimizing

Use the cheapest tool that can localize the relevant resource:

- CPU samples or traces for compute time;
- allocation/heap profiles for memory pressure;
- I/O, query, syscall, or network traces for waiting and request volume;
- lock, race, scheduler, or contention tools for concurrency bottlenecks;
- build traces and dependency graphs for build latency;
- deterministic operation instrumentation when it directly represents cost.

Build a compact cost map:

```text
Measured component: <symbol, query, phase, wait, allocation site, build action>
Observed share or count: <evidence>
Caller/workload path: <why representative requests reach it>
Constraint: <correctness or resource invariant that limits changes>
```

Apply observation-dependent rules:

- **No dominant hotspot** → improve instrumentation or inspect end-to-end waits; do not optimize the most visually complex
  function by intuition.
- **External dependency dominates** → measure request count, payload, batching, caching, and service contract before local
  computation changes.
- **Tail differs from median** → separate slow-path inputs, retries, queueing, saturation, and failures.
- **Allocation or memory dominates** → inspect lifetime and peak retention, not only allocation count.
- **Build dominates** → inspect invalidation, dependency fan-out, cache hits, generated steps, and remote/local execution.
- **Profiler materially perturbs behavior** → corroborate with a lower-overhead trace or deterministic counter.

## 4. Form one falsifiable bottleneck hypothesis

For the leading candidate, state:

```text
H1: <mechanism causing the measured cost>
Evidence: <profile/trace/count supporting it>
Predicted movement: <which metric should change and by approximately what mechanism>
Correctness risk: <contract that could be violated>
Resource trade-off: <cost that may move elsewhere>
Cheapest coherent change: <one bottleneck>
Falsified by: <measurement or profile outcome that rejects H1>
```

Rank candidates by expected impact, evidence strength, implementation risk, and reversibility. Do not select an
optimization merely because it is familiar or asymptotically attractive on an unrepresentative input range.

## 5. Optimize one bottleneck transactionally

1. Make the smallest coherent change that tests the hypothesis.
2. Preserve API, ordering, duplicate, error, precision, consistency, cache-invalidation, concurrency, and lifecycle
   semantics explicitly relevant to the path.
3. Inspect the diff immediately. Remove unrelated refactors, formatting churn, dependencies, and speculative helpers.
4. Run the cheapest correctness check before spending on the benchmark.
5. Run the comparable benchmark and inspect whether the predicted metric moved.
6. Re-profile when the candidate materially changes the cost distribution or exposes the next bottleneck.

Treat common optimizations as conditional decisions:

- **Cache** → define key identity, invalidation, consistency, memory bound, eviction, lifecycle, and tenant/security
  isolation before retaining it.
- **Batching** → preserve ordering, partial-failure, timeout, retry, and resource-bound semantics.
- **Parallelism** → account for contention, cancellation, determinism, saturation, and downstream capacity.
- **Algorithm/data structure** → preserve duplicates, stability, iteration order, precision, and worst-case inputs.
- **New dependency or native extension** → establish resolved compatibility, clean build/package behavior, startup and
  deployment cost, and maintenance justification.
- **Approximation or semantic relaxation** → requires an explicit contract change; it is not an optimization-only edit.

## 6. Measure, compare, and keep or revert

Use the same workload and relevant environment as the baseline. Report raw observations and the repository tool's
statistical summary when available.

Accept a candidate only when:

1. the primary metric improves enough to satisfy the target or exceed observed noise by a practically meaningful margin;
2. focused and relevant regression checks pass;
3. output, ordering, error, compatibility, security, and concurrency semantics remain accepted;
4. tail, memory, allocation, I/O, startup, saturation, and cost guardrails relevant to the change do not regress
   unacceptably;
5. the final profile or deterministic count supports the claimed mechanism;
6. added complexity and maintenance cost are justified by the measured result.

Otherwise revert the candidate exactly. If two consecutive candidates do not improve the primary metric or the profile
contradicts the current mechanism, discard the hypothesis set and re-profile from the preserved baseline. Do not stack a
third speculative optimization.

When multiple candidates are useful, keep them as separately measured conceptual changes when practical. Do not report
combined speedup as attributable to each component.

## 7. Add a stable performance guardrail when justified

Add or update a benchmark or regression threshold only when it is reproducible enough to be useful:

- prefer deterministic counts or controlled benchmark statistics over exact wall-clock assertions on shared hosts;
- choose tolerances from observed variance and operational budgets, not from the best local run;
- separate warm and cold behavior when both matter;
- keep benchmark setup representative and bounded;
- verify that a known slower implementation or targeted inverse change breaches the guardrail;
- avoid a blocking CI gate that is noisier than the regressions it is meant to detect.

If the benchmark remains noisy, retain it as observational evidence or run it in a controlled scheduled environment
rather than creating a flaky merge gate.

## 8. Run the completion gate

Re-read the performance contract, inspect the final diff, and rerun from a stable state. Require, as applicable:

1. exact baseline and final workload commands, environment, and raw observations are recorded;
2. the primary target or keep/revert rule is satisfied;
3. focused correctness, compile/type/lint/static, and relevant regression checks pass;
4. broader checks scale with interface reach, concurrency, persistence, security, and deployment risk;
5. before/after profiles or deterministic counts support the bottleneck explanation;
6. relevant resource and tail guardrails are evaluated;
7. no benchmark-only branch, hard-coded fixture, disabled work, weakened assertion, or changed workload creates the
   apparent speedup;
8. the patch remains coherent and unrelated working-copy edits are preserved.

A valid result may be `optimized`, `no-change`, `measurement-only`, or `blocked`. A no-change result is preferable to
retaining complexity without distinguishable value.

## Failure signatures and diagnostic actions

- **Microbenchmark improves but the representative workload does not** → reject the proxy or identify the missing
  production cost before further edits.
- **Mean improves while tail latency worsens** → inspect slow-path distribution, queueing, saturation, retries, and
  failures; evaluate the metric named in the contract.
- **Profile does not show the assumed hotspot** → abandon the hypothesis and re-profile; do not optimize by code shape.
- **Speedup appears only after changing data, cache warmth, compiler flags, or environment** → restore comparable
  conditions and measure the changed variable separately.
- **Fewer operations produce wrong ordering, duplicate, precision, or error semantics** → revert and restore the
  correctness invariant before trying another design.
- **Cache improves hits but returns stale or cross-tenant data** → treat invalidation or isolation as a correctness defect;
  revert the optimization.
- **Wall-time distributions overlap materially** → report no distinguishable improvement or increase measurement
  precision; do not claim the best run.
- **CPU falls while memory, I/O, startup, or downstream load rises** → evaluate the declared guardrails and total resource
  effect before keeping the change.
- **Benchmark harness dominates the profile** → separate setup and measured work or use a deterministic cost probe.

## Escape conditions

Abandon or narrow this procedure when:

- new evidence shows the task is a performance regression, functional defect, new behavior, or read-only review;
- no representative workload or defensible proxy can be established;
- the environment cannot produce comparable measurements and no deterministic cost model is available;
- the requested target requires changing functional, compatibility, consistency, precision, security, or reliability
  semantics without approval;
- an external system dominates but cannot be observed or controlled safely;
- profiling or load generation would violate production safety, credentials, rate limits, or data policy;
- the measured benefit is too small or unstable to justify the added complexity.

Return the baseline, workload limitation, profile evidence, rejected hypotheses, and the next measurement needed. Do not
force an optimization patch.

## Final report

```text
Status: optimized | no-change | measurement-only | blocked
Performance contract: <PERF items, workload, metric, target, and guardrails>
Baseline: <exact command/environment and raw/statistical observations>
Profile evidence: <measured bottleneck and cost share/count>
Hypothesis: <mechanism, prediction, and falsifier>
Change: <one coherent optimization and complexity/resource trade-off>
Final measurement: <comparable observations and effect>
Correctness validation: <exact commands and results>
Resource/tail guardrails: <observed results>
Keep/revert decision: <evidence-based rationale>
Residual uncertainty: <none or exact limitation>
```
