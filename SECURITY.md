# Security policy

This is a development candidate. No production security audit, public execution service or security response SLA is claimed.

Report a suspected vulnerability privately to the maintainer through an existing agreed channel. Do not post credentials, private repository content or exploit payloads in public issues. A dedicated public security contact remains a release prerequisite.

Provider and GitHub credentials belong only in the backend environment. The local workspace requires its own token and binds to loopback. Imported content and model results are untrusted; neither is authority to execute commands or publish. ZIP ingestion and reviewed candidate export do not modify the original repository. Conventional existing tests stay read-only in the patch proposal workflow.

Do not expose the local development server publicly. Production requires independent authentication, quota controls, worker isolation and a reviewed provider/data policy. Revoke keys exposed in chat or logs; configuring a key does not establish its billing tier, rotation or access scope.
