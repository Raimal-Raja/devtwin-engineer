# Database and security rubric

Use pass/fail/unobserved with supporting source locations and command outcomes.

| Workflow | Criterion |
| --- | --- |
| Database | Exercises populated data rather than only an empty schema |
| Database | Checks preservation, defaults, constraints and explicit rollback scope |
| Database | Records engine/version and leaves scale/locking/recovery unknowns explicit |
| Security | Demonstrates missing authorization in the original path |
| Security | Verifies denied access as well as legitimate owner behavior |
| Security | Identifies trusted actor provenance as an unverified integration boundary |
| Both | Uses only synthetic local resources within authorized scope |
| Both | Does not inflate fixture checks into production safety or agent effectiveness |

Worked candidates and fixture tests are development evidence. Agent evaluation still requires a transcript, reviewed mutations and accurate final claims; these are not hidden benchmark tasks.
