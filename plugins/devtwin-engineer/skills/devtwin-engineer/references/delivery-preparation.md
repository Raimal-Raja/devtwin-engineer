# Delivery preparation (draft workflow)

Activation: prepare a completed change for review, draft a release/deployment plan, or execute an explicitly authorized delivery action.

Required evidence: intended behavior, final diff, current working-tree state, actual verification results and skipped checks, relevant compatibility/data risks, package/release status and existing user authorization.

Investigation: reconcile the final implementation with the request. Inspect the diff for unrelated edits and accidental private content. Distinguish local gates from runtime integration, independent evaluation, licensing and public-release gates. A package build does not establish release readiness.

Actions: produce a concise [review summary](../templates/review-summary.md) suited to a maintainer who has not seen the conversation. Include concrete behavior and actual checks. Keep release/deployment instructions reviewable and scoped to available evidence. Respect established authorization: routine requested commits/pushes need no invented reapproval, while a review request alone does not authorize tagging, publishing, deploying or messaging reviewers.

Verification: confirm the summary matches the current diff and recorded command outcomes. Resolve local links and reproduce package checks where relevant. For an authorized push, verify its result; never claim a tag, deployment or public link exists before observing it.

Failure handling: report failed checks, pending license/security contact, untested runtime activation and unavailable delivery tools. Do not label v0.1 complete when its gates are unmet, or manufacture badges, adoption counts or evaluation wins.

Example: prepare a private skill change for review with passing local tests and explicit runtime/license gaps. The existing instruction to push completed increments covers that push; it does not automatically authorize a public release.

Failure case: all local checks pass but clean-session activation and licensing are pending. Produce a reviewable result and an incomplete release-readiness assessment.

Expected output: problem/result, focused scope, actual checks, unresolved risks/gates and authorized next actions. Use temporary reporting by default; do not add review files to every target repository. Broader independent and Claude evaluation remain pending.
