# Optimization task: batch first-match lookup

Optimize `resolve_first` for the representative batch workload defined in `PERFORMANCE.md` and `benchmark.py`.

The current implementation is functionally correct and the correctness suite is green. Preserve the complete functional
contract while reducing measured key operations.

Required workflow:

1. Run the correctness baseline.
2. Run the benchmark and preserve the baseline result.
3. Use the deterministic operation evidence, and profiling if useful, to identify the bottleneck.
4. Change one bottleneck coherently.
5. Rerun correctness and the same benchmark.
6. Keep the change only if it meets the performance target without violating guardrails.

Commands:

```sh
python -m unittest discover -s tests -v
python benchmark.py
```

Constraints:

- Preserve `Entry` and `resolve_first(entries, queries)` as public API.
- Do not change `PERFORMANCE.md`, `benchmark.py`, `pyproject.toml`, or add dependencies.
- Do not change first-match, ordering, duplicate-query, missing-key, or no-persistent-cache semantics.
- Do not special-case the visible benchmark size or data.
