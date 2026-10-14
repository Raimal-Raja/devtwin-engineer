# Thirteen capability prerequisites

The [machine-readable registry](../evaluations/capabilities.json) records required inputs, checks and a failure boundary for every capability. Each maps to a real shared reference, development task, rubric and fixture. `python scripts/check_capabilities.py .` audits those resources without executing a target repository. The unified project checker includes this resource gate. Resource readiness and agent behavior are separate results.

| Capability | Required evidence/tools | Current development validation |
| --- | --- | --- |
| Repository understanding | Relevant files, entry points, instructions, current changes | Codex library/HTTP review and metadata helpers |
| Feature tracing | Entry point, calls and indirect dispatch | Codex order-flow trace and six fixture tests |
| Change impact | Proposed contract/signature, known consumers | Codex direct/indirect consumer checks |
| Bug reproduction | Expected/observed behavior, interpreter or precise blocker | Codex library/HTTP failures and missing-interpreter reporting |
| Dependency diagnosis | Constraints, resolver and wheelhouse | Codex offline conflict and candidate dry-run |
| Focused implementation | Authorized contract, observed failure, existing work | Codex focused repair with protected originals |
| Regression verification | Existing tests, edge cases, actual interpreter | Codex candidate and parent acceptance checks |
| API compatibility | Before/after shapes, strict/permissive consumers | Codex fixture compatibility matrix |
| Database review | Existing synthetic rows, engine/rollback contract | Codex SQLite migration/rollback checks; production concurrency unverified |
| Security review | Authorized synthetic cases and trusted-actor assumptions | Codex ownership allow/deny checks; authentication integration unverified |
| Performance investigation | Matching inputs, baseline, profiler, equivalence | Codex synthetic measurement/profile and malformed-input limitation |
| Documentation verification | Actual CLI, documented examples and expected output | Codex bad/corrected CLI commands |
| Delivery preparation | Final scope, actual checks, pending gates and authority | Codex evidence-based handoff; no unsupported release claim |

These observations come from the [increment-18 development evidence](../evaluations/results/increment-18.md). They do not constitute independent baseline comparisons or all-platform certification. The [GitHub web connection](github-workspace.md) and [patch review](patch-review.md) have separate tests. The browser dispatcher loads all thirteen references, but browser source-only calls cannot verify runtime behavior, migrations or performance without an execution stage.

Claude execution is deferred by explicit user choice; structural plugin validation remains recorded. A Codex-focused candidate need not pretend Claude is tested. Formal release documentation must keep that limit visible.
