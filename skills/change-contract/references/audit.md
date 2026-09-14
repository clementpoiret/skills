# Audit contract conformance

Identify the accepted contract, target, comparison basis, and complete in-scope changes. Without an accepted
basis or identifiable target, report the missing input; do not manufacture criteria from the patch.

For every applicable `AC-*` and `INV-*`, compare the required evidence with what is actually available. Use a
compact record:

| ID | Required evidence | Observed evidence | Status |
| --- | --- | --- | --- |
| AC-1 | Decisive behavior check | Command/result or precise source evidence | met / not met / unknown / not applicable |

Mark evidence as sufficient, missing, or unavailable where the distinction matters. Source inspection can
establish some properties but cannot replace execution when the contract requires runtime evidence. A test
command that could not run is unavailable evidence, not a pass or necessarily an implementation defect.

Check for unapproved scope expansion and invariant violations, including relevant public, data, security, and
concurrency boundaries. Qualify findings with location, reachable condition, consequence, and the violated
obligation. Do not rewrite requirements to fit the implementation or silently edit the target.

Use one verdict:

- **Conforming:** every applicable obligation is met with sufficient required evidence.
- **Nonconforming:** at least one established violation or unapproved scope expansion exists; note any additional unknowns.
- **Blocked:** no established violation, but missing contract, target, decision, or required evidence prevents a conformance verdict.

Complete independent assessment despite a localized evidence gap. Report the verdict, decisive findings, and
exact missing evidence. A blocked audit does not imply all implementation is unfinished. Finish at the
assessment boundary.
