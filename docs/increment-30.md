# Increment 30 — GitHub browsing and import budgets

The shared two-request GitHub budget interrupted normal repeated browsing and importing. Browsing now has a separate six-request-per-minute budget; imports allow four requests per minute. Both remain authenticated and bounded, and rate-limit responses include an actionable wait in seconds and `retry_after_seconds`.

Validation: all 16 server regression tests passed, including browse-budget exhaustion, successful import after browsing is exhausted, and expiry of the browse window. The first sandboxed run was blocked by Windows socket permissions; the permitted rerun passed.
