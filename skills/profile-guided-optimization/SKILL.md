---
name: profile-guided-optimization
description: "Optimize accepted-correct code using a representative workload, measured baseline, and identified bottleneck; not diagnosis of a known regression."
---

# Profile-guided optimization

Keep only a demonstrated improvement that preserves required behavior. Measurement-only and no-change outcomes
are valid.

## Define the comparison

Establish the accepted-correct behavior, representative workload, metric, environment, and relevant resource
constraints. Agree on what would count as a useful improvement from the request or project policy; do not
invent an SLO or claim an unspecified target was met.

Record a baseline under reproducible conditions. Include workload size and distribution, warmup or caching
state, variability, and important latency, throughput, memory, or resource guards. If the workload or
correctness basis is missing, establish it before optimization. A known regression belongs to diagnosis first.

Identify a bottleneck using a profile, trace, or deterministic operation count that is relevant to the metric.
Optimize a measured cause, not a code smell or a remembered rule of thumb.

## Change one supported cause

State the bottleneck hypothesis and expected effect. Make a coherent candidate change, keeping its comparison
interpretable. Independent inspection may run concurrently; competing benchmarks that contaminate measurements
may not.

Preserve ordering, duplicate and first-match behavior, numeric precision, errors, side effects, and
concurrency semantics where required. For caching, establish key completeness, tenant isolation, invalidation,
staleness, ownership, and memory bounds. A faster implementation with a changed contract is not an
optimization of the same behavior.

Validate correctness, then compare baseline and candidate under equivalent conditions. Use repeated
measurements when variability matters and retain the distribution or summary rule, not only the best run.
Report costs shifted to memory, startup, tails, contention, or another workload. A microbenchmark does not
establish an end-to-end improvement outside its measured scope.

## Keep or revert

Keep a candidate only when evidence establishes meaningful improvement under the decision rule and relevant
guards hold. Otherwise restore your own candidate edits without discarding pre-existing work. Do not keep
speculative changes because they look faster or because the benchmark happened to pass once.

If measurements are invalid or indistinguishable from noise, report that limitation rather than an
improvement. If experiments stop producing new evidence, reconsider the bottleneck or measurement design
instead of cycling through arbitrary rewrites.

Report the workload, metric, comparable before/after evidence, behavioral checks, and decision. Once the
requested target is met, stop optional tuning. If no useful verified improvement is available, return a
measurement-only or no-change result with the limiting evidence.
