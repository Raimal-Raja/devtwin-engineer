# Regression verification

Activation: a candidate patch or a request to verify behavior.

Required evidence: actual commands, exit status, assertions exercised, environment, and skipped checks.

Investigation: choose checks that would catch the original defect and relevant regressions. Include existing callers and boundary inputs when they matter.

Actions: execute the narrow regression first, then the relevant existing suite. Broaden testing only when risk or new failures justify it.

Verification: confirm the regression failed before the correction and passes afterward. Inspect the final diff and preservation of unrelated edits. A helper harness passing does not establish clean-session skill activation or benchmark improvement.

Failure handling: record failed tests and missing tooling. Do not claim full correctness from a finite suite or report tests that were not run.

Expected output: checks and outcomes, exercised behavior, remaining limitations.
