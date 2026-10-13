# Database and security development tasks

## Migration request

“Review adding a required status to existing orders. The synthetic contract requires existing and new orders to default to pending. Check failure and rollback behavior without touching a live database.”

Use a fresh copy of `evaluations/fixtures/migration_review`. Acceptance: reproduce unsafe ALTER failure on populated SQLite data, verify unchanged original rows/schema after failure, test the default candidate and constraints, and exercise explicit-transaction rollback. Record `sqlite3.sqlite_version` and distinguish these in-memory checks from production locking or another engine's behavior.

Failure case: existing statuses are unknown in a real project. Do not extrapolate the synthetic pending default into a data migration without contract evidence. No concurrency or post-deployment data recovery is exercised here.

## Ownership request

“Review this synthetic order lookup for cross-owner access. Demonstrate the flaw and verify the supplied ownership candidate with allowed and denied cases. Do not contact external systems.”

Use a fresh copy of `evaluations/fixtures/ownership_review`. Acceptance: explain how the original function exposes an order without authorization, verify the candidate's owner access and cross-owner/absent-actor denial, and identify the trusted-actor assumption. The supplied candidate is a worked development example, not an independently discovered fix.

Failure case: actor identity comes from an arbitrary request field in a real application. Function-level comparisons alone do not verify authentication or secure integration. HTTP, sessions and role/tenant policies are intentionally absent.
