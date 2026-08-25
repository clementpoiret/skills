# Review task: tenant-aware response cache

Review `workspace/change.diff` against `workspace/intent.md` and the before/after source. Do not edit the files.

Write a JSON object with this schema:

```json
{
  "findings": [
    {
      "id": "stable-defect-id",
      "severity": "critical|high|medium|low",
      "location": "path:line",
      "mechanism": "exact failure mechanism",
      "trigger": "specific precondition",
      "consequence": "observable effect",
      "evidence": "supporting source or contract evidence",
      "verification": "safe reproduction or check"
    }
  ]
}
```

Report only actionable defects introduced by the change. A style preference, impossible trigger, documented invariant, or
pre-existing behavior is not a finding. Collapse multiple manifestations of one root cause into one finding.
