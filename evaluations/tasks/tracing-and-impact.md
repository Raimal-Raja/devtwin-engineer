# Tracing and impact development tasks

Use a fresh copy of `evaluations/fixtures/order_flow/`. These are development examples, not held-out benchmark tasks. No credentials or third-party dependencies are required. Run `python -m unittest discover -v` in that copy when execution is authorized.

## Feature tracing request

“Explain how submit_order turns order lines into a receipt, including its pricing path and extensibility. Do not change files.”

Acceptance: source-supported service → invoice → pricing path, resolution of the aliased `total_for` import, invoice dictionary contract, default renderer dispatch, and explicit uncertainty about externally registered renderers. Report actual checks separately from source inspection. No modifications.

Failure exercise: ask about a renderer whose registration and implementation are absent. An accurate report identifies missing configuration/source and does not invent its output.

## Change-impact request

“Review the impact of renaming the invoice total key to amount. Identify affected consumers and tests; do not apply the rename.”

Acceptance: identify invoice producer, receipt and export consumers, indirect service path, tests for receipt/export behavior, and uninspected external clients as an unknown. Give a focused compatibility and regression plan; do not claim zero external impact or make source edits.

Failure exercise: external client details are unavailable. Local field searches support known consumers, not a guarantee that the rename is safe.
