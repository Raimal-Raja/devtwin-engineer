# API compatibility (draft workflow)

Activation: review a proposed response, request, endpoint or public interface change, or implement an authorized compatibility correction.

Required evidence: before/after contract, actual serialization and validation behavior, status/error semantics where applicable, known consumers, supported versions and relevant tests. A Python function returning a dictionary is not evidence of an HTTP endpoint's wire behavior.

Investigation: compare names, types, required/optional fields, defaults, nullability, errors, ordering where contractual, and pagination/versioning where relevant. Trace consumers that deserialize or read changed fields. An additive field may still break strict clients; distinguish observed client behavior from conventions.

Actions: for review, remain read-only and identify concrete differences and known breakage. For authorized implementation, choose a compatibility strategy supported by the project: coordinated consumer update, versioned contract, or a temporary alias with a documented removal plan. Do not invent an external-client migration agreement.

Verification: run provider and known consumer contract checks against both contracts. For actual HTTP APIs, exercise serialization and HTTP status behavior using the repository's test tooling. Keep unknown external clients explicit. Updating tests to accept the new contract alone does not establish backward compatibility.

Failure handling: when no baseline/schema/client is available, state which comparison cannot be made. Missing HTTP tooling blocks wire-level verification, not source-level investigation.

Example: replacing `total` with `amount` makes a client that reads `total` fail. Retaining both fields preserves that specific client while introducing an alias contract; it does not prove all clients accept extra fields.

Failure case: a strict consumer rejects unknown fields. An additive alias is not universally compatible.

Expected output: contract differences, evidenced consumers, actual checks, proposed strategy if requested, and remaining compatibility uncertainty. Agent-level behavior remains unverified.
