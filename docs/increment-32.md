# Increment 32 — Local workflow state audit

Fixed stale evidence across task/workflow changes and repeated operations. Editing either clears the downloadable report, patch, execution approvals and repair result, and requires renewed provider consent. A new investigation clears earlier results before submission, including when the request fails. Repair displays its own analysis in the evidence section instead of leaving an older report visible. Candidate export accurately states that export runs no additional tests, preserving the distinction from earlier verification.

Four new Node tests exercise production app event handlers with an in-memory DOM and mocked HTTP responses. They cover task/workflow invalidation, current repair evidence, failed-investigation cleanup, consent gates for verification/export and approval reset after a task edit. These tests do not substitute for a visual browser audit.

Full gates passed: 148 Python cases (146 passed, two Windows symlink skips), 13 web tests, package, all 13 capability resource checks and archive integrity. Rebuilt app and worker became healthy. A GitHub smoke check attempted during restart received connection refused; after health completion the read-only default-branch browse/import passed with seven files at `0338df6737590336d9db084ff6a0d210b6114743`. The pure utility Docker check passed three baseline and three candidate tests using a comment-only candidate. No WhatsApp GUI automation ran and the target repository was unchanged.

## Local acceptance boundaries

| Area | Evidence and boundary |
| --- | --- |
| Connect and select | Fresh public GitHub browse/import passed; ZIP/path/hash/auth rejection cases covered by regression gates |
| Investigate and review | Source schema/citation validation and exact source-line evidence covered; current repair analysis displayed; AI semantic correctness remains unverified |
| Propose and export | Review/approval guards covered by client and HTTP tests; original selection remains unchanged |
| Isolated verification | Fresh Docker utility baseline/candidate checks passed; standard-library Python unittest only |
| Bounded repair | Attempt caps, failure retries, blocked/provider failures and evidence-based outcome distinctions covered by regression tests; no new paid/live model request in this increment |
| Plugin/skills | Packaging and 13 capability-resource gates passed; this is not proof that every capability is independently effective; Claude execution stays deferred |

The local supported workflow is ready for further hands-on testing. A zero-bug claim, arbitrary language/dependency execution, public multi-user hosting, independent containment audit and licensing/release approval are not established by these checks. Free-provider rate limits and generated reasoning errors remain visible limitations.
