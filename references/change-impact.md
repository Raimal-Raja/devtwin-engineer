# Change-impact investigation (draft workflow)

Activation: a proposed or existing edit whose affected callers, contracts or checks need investigation. A review request alone does not authorize applying the proposed edit.

Required evidence: changed symbol or data contract, current diff if available, known direct callers/import aliases, field consumers, relevant tests and unresolved external/dynamic consumers.

Investigation: define what changes in behavior or interface before searching. Inspect definitions and actual reference context, including serialization, exports, fixtures and adapters. Follow affected contracts until a stable boundary; do not recursively inspect unrelated code. Distinguish direct breakage from possible downstream effects. Search history or dependency metadata only when useful and available.

Actions: produce a conservative impact list and focused verification plan. For an authorized implementation, preserve the original working-tree evidence and use the implementation workflow. No matches in the inspected repository does not establish that there are no external consumers.

Verification: check each claimed consumer against source. Use contract tests or a temporary candidate experiment when authorized. Record search scope and checks actually executed. Report omitted submodules, generated code and external clients where relevant.

Failure handling: if callers are constructed dynamically, contract ownership is unclear or tests are missing, state the uncertainty rather than declaring the edit safe. Reaching the search limit is incomplete investigation.

Example: renaming an invoice's `total` key affects both the receipt renderer and CSV export, even though the service calls the renderer through a registry. Trace test expectations as well as direct key reads.

Failure case: a private external client reads the invoice dictionary. The local repository cannot prove that client compatibility; ask for relevant contract evidence if it is required for the task.

Expected output: proposed behavior, known affected locations, inferred risks clearly labeled, focused checks, and remaining uncertainty. Broader independent and Claude evaluation remain pending.
