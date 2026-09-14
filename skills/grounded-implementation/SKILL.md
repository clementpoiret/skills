---
name: grounded-implementation
description: "Implement a nontrivial feature, behavior change, or refactor from requirements in an existing codebase; not bug diagnosis, review-only, or test-only work."
---

# Grounded implementation

Deliver the requested behavior through implementation and relevant verification, using the repository's actual
contracts and mechanisms. A small edit does not need a formal workflow.

## Establish the change

Treat approved requirements and accepted acceptance criteria or invariants as authoritative. Existing code and
tests are evidence of current behavior, not permission to redefine the request. When requirements are
incomplete, infer only low-risk details; isolate consequential unresolved decisions rather than blocking
independent work.

Identify the behavior's owner, directly affected consumers, and evidence of success. Read the relevant
implementations, tests, configuration, and dependency versions. Follow generated files to their maintained
source. Expand inspection when a dependency or boundary warrants it, not into a repository-wide survey.
Independent reads may be batched; dependent decisions must use their results.

For a cross-component change, keep a compact requirement-to-change-to-check mapping. Do not create a separate
planning artifact unless requested or needed to manage the work.

## Implement and establish evidence

Change the owning component and necessary consumers together. Preserve public interfaces, persisted formats,
security boundaries, and concurrency semantics except where the requested change explicitly changes them.
Reuse repository mechanisms and remove only obsolescence caused by this patch. A text search alone does not
establish that dynamically registered or externally consumed behavior is unused.

Use focused checks for the actual requirement and plausible failure cases. For dependency or framework
behavior, verify against the resolved version rather than a remembered API. A visible test passing does not
establish a broader contract; do not hardcode its examples.

Classify failures as caused by the patch, pre-existing, or environmental before expanding scope. Do not repair
unrelated baseline failures opportunistically. If the approach repeatedly fails without new evidence, reassess
the owning invariant and implementation strategy instead of layering workarounds.

Continue authorized implementation, necessary cleanup, and verification until the intended deliverable is
complete. Reuse valid results for the unchanged relevant state rather than rerunning them for ceremony.
Missing credentials or infrastructure block only dependent checks or work; they do not invalidate completed
independent implementation.

## Completion

Inspect the final diff against the requirements. Report what changed, the strongest verification evidence, and
material gaps. Distinguish unfinished implementation from completed implementation whose required checks could
not run. Stop when the requested behavior and required checks are satisfied; do not open an optional audit or
simplification pass.
