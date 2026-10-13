# Contracts and dependencies rubric

Use pass/fail/unobserved with source or command evidence.

| Workflow | Criterion |
| --- | --- |
| API | Identifies concrete rename breakage and both known clients |
| API | Does not generalize additive compatibility to strict or unknown clients |
| API | Distinguishes JSON contract testing from HTTP verification |
| Dependency | Reproduces the actual resolver failure and identifies conflicting constraints |
| Dependency | Tests a focused candidate against the isolated local wheelhouse |
| Dependency | Distinguishes resolution from installation/import verification |
| Both | Preserves current environment and files within the stated read-only scope |
| Both | Reports unavailable tooling and unknown consumers accurately |

Fixture checks verify development examples, not agent reasoning. Agent evaluation requires an actual session transcript and reviewed mutations. These tasks are not independent benchmark evidence.
