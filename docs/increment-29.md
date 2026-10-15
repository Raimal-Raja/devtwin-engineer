# Increment 29 — GitHub connection and complete workspace checks

Checked on 2026-10-15 after the user reported “No successful GitHub import” and requested verification of every workspace section.

## Fixes

The repository itself was public and reachable. The original UI required explicit paths and a ref but displayed a generic failure beside the GitHub controls; useful API errors appeared farther down the page. The original field values beyond the repository URL were unavailable, so the exact original rejection is not asserted.

GitHub import now shows actionable inline errors, validates missing/wrong workspace tokens and selections before requests, accepts an omitted ref using the default branch, and offers a bounded file picker. Browse retrieves metadata only; an import from that picker is pinned to its browsed commit. Unsupported/excluded files are filtered and selected contents still receive hash, secret and size validation. Private access and rate errors have specific guidance.

A second failure was reproduced against the user's tests: ordinary recursive discovery missed `tests/test_chat_utils.py` without `tests/__init__.py` and returned no executed cases. The runner now loads explicitly selected unittest modules, including namespace test directories and duplicate basenames in distinct directories. It preserves test bytes and reports actual import failures. Zero tests and all-skipped tests have separate blocked reasons.

## Verification

| Workspace section | Actual evidence |
| --- | --- |
| Connect/select | ZIP preview, selected hashes, authentication rejection and missing-selection rejection passed |
| GitHub connection | Default-branch browse and commit-pinned import passed on the user's public repository |
| Prepare investigation | Provider/public-input consent rejection and live free-model submission passed |
| Review evidence | Structured source-analysis response and literal client rendering/input checks passed |
| Propose/review | Live model proposal, rejection of unapproved export and selected ZIP export passed; test bytes preserved |
| Isolated verification | Rejected missing execution approval; actual synthetic baseline failed and candidate passed all five tests |
| Bounded repair loop | Actual investigation/proposal/test loop passed in one attempt after respecting the verification quota reset |

The user's `Raimal-Raja/AutoReply-Whatsapp-Bot` was imported at commit `0338df6737590336d9db084ff6a0d210b6114743`: seven supported text files imported successfully. Only its pure utility module and three standard-library tests were executed in isolated Docker checks, using a comment-only in-memory candidate. Both baseline and candidate ran three passing tests. The WhatsApp automation was not executed and no target repository changes were applied or pushed.

An initial live proposal call returned an OpenRouter upstream generation error and stopped without paid fallback or automatic retry. A separate later check passed proposal/export/verification/repair. Original source preservation also passed. These results do not imply permanent free-provider availability.

Full regression gates passed: 146 Python tests, 144 passed with two Windows symlink skips; nine Node web/client-input tests passed; package, capability-resource and archive gates passed. Real tests use HTTP endpoints and Docker, with client input unit checks. A visual browser automation connector was unavailable, so full click-through/visual certification is not claimed. The user should refresh the page to load the new file picker and error messages.

See [machine-readable evidence](../evaluations/results/increment-29.json), [GitHub setup](github-workspace.md) and [workspace guide](local-workspace.md). Broader platform, public hosting, independent security/effectiveness validation and licensing remain separate gates; Claude execution stays deferred.
