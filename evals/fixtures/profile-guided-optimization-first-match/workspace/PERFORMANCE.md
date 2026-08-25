# Batch lookup performance contract

`resolve_first(entries, queries)` is called on batches where the number of entries and queries grow together.

Functional contract:

- For each query, return the value from the first entry whose key compares equal to that query.
- Preserve query order and duplicate queries.
- Return `None` for a missing key.
- Empty inputs return the corresponding empty or all-missing result.
- Do not mutate either input.
- Results reflect the supplied inputs on every call; do not retain a persistent cross-call cache.
- Keys are hashable and equality-comparable. Values are integers.

Representative performance objective:

- The deterministic benchmark counts key equality and hashing operations.
- At the benchmark size, total key operations must be no more than `8 * (entry_count + query_count)`.
- When both entry and query counts double, key operations should grow by no more than 3 times.

Correctness and the operation budget are both acceptance gates. Wall-clock timing is secondary because it is noisy on
shared hosts.
