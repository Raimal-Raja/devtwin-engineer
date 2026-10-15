# Increment 34 — Selection prerequisites and actionable repair failures

Fresh live acceptance also passed after deployment: the synthetic checkout repair returned `repair_demonstrated` in one attempt, with failed baseline and all five candidate tests passing. No source changes were applied. This is selected Python fixture evidence, not full ML project validation.

The reported Flask/ML project imported only README.md and requirements.txt. A fresh GitHub metadata check confirmed its flask_app/app.py is 20,341 bytes, above the existing 16,000-byte selected-text budget. The old file picker silently omitted oversized and unsupported files. Source investigation could succeed on documentation while the implementation and tests remained unavailable.

The picker now reports omission counts and up to 20 oversized paths with sizes. This explains the actual selection boundary without silently expanding model submissions or executing notebook/model artifacts. The user chooses supported files explicitly.

Preview identifies selections without Python test modules. Investigation and proposals remain available, while verification/repair controls show prerequisites and remain disabled. The repair API independently rejects missing or nonimportable test-module paths before reserving model or verification quota. Invalid requests therefore do not consume the app's inference allowance.

Repair failures now distinguish investigation/proposal provider failures, invalid candidate/input validation, and blocked verification. An investigation provider failure returns a structured blocked report with stage and error code and performs no candidate generation or tests. Previously that exception lost the repair report. Validation errors are no longer mislabeled as provider outages. No provider details, credentials or fallback requests are added.

Validation: full project gates passed with 151 Python cases (149 passed, two Windows symlink skips), 15 web tests, package validation, all 13 capability-resource checks and archive integrity. Real deployed HTTP checks confirmed documentation-only repair returns actionable HTTP 400 and fresh GitHub listings expose omitted files. Tests verify zero model/verification quota reservation on prerequisite rejection, provider failure before execution, distinct invalid-candidate outcomes, browser-side prerequisite gating and inspectable blocked results. App and runner rebuilt successfully.

These fixes improve the supported local selected-file workflow. They do not implement whole-repository indexing, larger-file context management, arbitrary language/dependency environments, Flask/TensorFlow execution, or a platform serving millions of users. Those remain separate engineering work; passing local gates does not establish production scalability or AI semantic correctness. Full visual browser workflow acceptance remains pending after the earlier Computer Use URL-policy interruption.
