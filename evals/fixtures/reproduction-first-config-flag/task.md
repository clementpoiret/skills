# Bug: `FEATURE_X=false` enables the feature

The following reproduction currently fails:

```sh
python -m unittest tests.test_service.FeatureFlagTests.test_false_string_disables_feature -v
```

Expected repository contract, already documented in `src/config_flags.py`:

- boolean strings are case-insensitive and ignore surrounding whitespace;
- true values: `true`, `1`, `yes`, `on`;
- false values: `false`, `0`, `no`, `off`;
- `None` returns the supplied default;
- any other non-`None` value raises `ValueError`.

Diagnose and fix the root cause. Preserve `src/service.py` and unrelated behavior. Add or strengthen a regression test, rerun
the original reproduction, and run the relevant suite.
