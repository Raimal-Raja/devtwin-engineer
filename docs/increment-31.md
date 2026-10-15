# Increment 31 — Honest repair outcomes and inspectable evidence

Repair-loop success now distinguishes `checks_passed_no_demonstrated_fix` from `repair_demonstrated`. The latter requires the runner's observed-failure flag plus an actually failed baseline and passing candidate. Passing both versions does not establish a fix. The UI displays the outcome explanation before export review.

Investigations attach the actual cited source line on the server. Prompt guidance explicitly addresses incomplete selections, statement order, optional regex whitespace, hypothetical risks and invented file counts. Proposal guidance rejects invented requirements and asks for explicit disclosure of behavior changes. These instructions improve grounding but cannot guarantee model semantic correctness; source claims remain unverified.

Validation: full project gates passed (148 Python cases, two Windows symlink skips; nine web tests), plus a focused source-evidence assertion. Docker app and worker rebuilt and healthy. No paid inference or new provider was introduced. Prior reports are historical and must be regenerated to use these changes.
