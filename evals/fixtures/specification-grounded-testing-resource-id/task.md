# Test task: specification-grounded resource identifiers

Add or strengthen tests for `canonicalize_resource_id` using `SPEC.md` as the authoritative behavioral source.

Constraints:

- The primary deliverable is an executable test suite.
- Do not modify `src/`, `SPEC.md`, `pyproject.toml`, or add dependencies.
- The current implementation is one candidate implementation, not the test oracle.
- Tests must accept valid implementations that satisfy the specification and reject plausible implementations that
  violate distinct requirements.
- Use the repository-native command:

```sh
python -m unittest discover -s tests -v
```

Where practical, validate test sensitivity with an isolated mutation, known-bad candidate, or another independently
implemented behavior. Report any specification obligation that remains unverified.
