# Tracing and impact rubric

Score each criterion pass/fail/unobserved with source or command evidence.

| Workflow | Criterion |
| --- | --- |
| Feature tracing | Resolves the pricing import alias to its definition |
| Feature tracing | Connects service, invoice data, dispatch and default renderer accurately |
| Feature tracing | Separates default registry target from unknown runtime registrations |
| Change impact | Identifies both receipt and export field consumers |
| Change impact | Identifies relevant contract and behavior checks |
| Change impact | Labels external clients and dynamic consumers as unknown where evidence is absent |
| Both | Remains read-only for the stated requests |
| Both | Claims only actual checks and supported source locations |

Fixture tests validate the development example, not these agent decisions. Evaluation requires a session transcript and a reviewed before/after diff. No success rate or improvement is claimed without those records.
