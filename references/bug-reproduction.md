# Bug reproduction

Activation: a reported failure or suspected regression.

Required evidence: input, expected behavior, observed failure, environment, and a command or precise blocker.

Investigation: locate the failing path and existing tests. Reduce the case while retaining the failure. Check whether setup, dependencies, or the code cause it. Capture useful error details without private payloads.

Actions: create a regression test when a repair is requested. Use synthetic inputs. Do not modify production data to reproduce.

Verification: run the case before patching; confirm that it fails for the reported reason. An import failure is not reproduction of a business-logic bug.

Failure handling: if required tools or access are missing, state what was attempted and what remains unknown. Do not rerun flaky tests until green and claim reproduction.

Expected output: minimal failing case, command and outcome, supported cause or remaining hypotheses.
