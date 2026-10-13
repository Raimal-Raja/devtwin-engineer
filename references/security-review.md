# Security review (draft workflow)

Activation: a requested review of an authorization or other security-sensitive path, or investigation of a concrete vulnerability within authorized scope.

Required evidence: actor identity, trust boundaries, controlled inputs, protected resource/action, actual enforcement path, relevant caller context and a synthetic reproducer or code-supported finding. Do not infer trusted identity from an unvalidated request field.

Investigation: trace where identity originates and where authorization is enforced. Check ownership/tenant scope and privileged exceptions against the project's intended policy. Inspect error behavior and whether failure exposes private data. Keep findings tied to an actual reachable path; separate a hypothetical risk from demonstrated access.

Actions: reproduce only within authorized fixtures or controlled targets, using synthetic accounts/data. For an authorized repair, apply the policy at the relevant boundary and preserve intended legitimate access. Do not contact external services, retrieve real third-party records or expand scope to attack infrastructure.

Verification: test the original unauthorized path, repaired denial, legitimate access and relevant role/tenant cases. Test direct callers as well as outer handlers when they form a supported interface. Record what authentication, HTTP transport and deployment controls were not exercised.

Failure handling: if policy, identity provenance or reachable environment is unknown, state that limitation and avoid inventing a privilege model. A local function check does not establish application-wide security.

Example: a synthetic repository lookup returns Bob's order to Alice because it accepts an order ID without checking the authenticated actor against the owner. A candidate enforces ownership and has both allowed and denied tests.

Failure case: passing Alice's user ID from an arbitrary request parameter can bypass an otherwise correct owner comparison. The real identity source must be inspected separately.

Expected output: concrete finding and impact, source/reproduction evidence, focused repair if requested, actual positive/negative checks and unresolved trust boundaries. Agent-level behavior remains unverified.
