# Increment 19: NVIDIA backend foundation — 2026-10-13

The user requested free online resources, provided NVIDIA's Nemotron Ultra example and authorized continuing. The conversation credential was not copied into files, commands or frontend assets. The backend reads `NVIDIA_API_KEY` from its process environment; credential rotation has not been verified.

Added a standard-library HTTP adapter for the fixed NVIDIA endpoint and `nvidia/nemotron-3-ultra-550b-a55b` model. It limits prompt/output/response sizes and timeout, rejects redirects and incomplete answers, excludes reasoning traces, redacts diagnostics and makes no retries or paid-provider fallback. The CLI sends only a fixed synthetic development prompt. This is an inference foundation, not a repository agent or hosted sandbox.

Six provider tests passed with simulated HTTP responses, covering successful request shape, reflected-key redaction, invalid configuration, network/auth/quota failures, malformed/truncated answers, response size and redirects. The initial sandboxed live request reported a connection failure. An approved rerun outside that host sandbox succeeded with a complete answer: “I can respond to a development test.” No repository content was sent. The configured account returned a successful response; its free-tier status, credit balance and key rotation were not inspected or established.

Final project gates passed: 68 Python tests ran, with 66 passing and two Windows symlink cases skipped. All six web tests, package validation and archive integrity checks passed. The unchanged 28-file skill archive SHA-256 remains `18b92ccd1ee0ab9839375ac406822f8cbfdcd1fd2a99663c16532f7a5f8abc76`; the backend is separate from the portable skill/plugin downloads.

The public dashboard was not connected to NVIDIA's trial service. NVIDIA's model documentation points to trial terms restricting hosted access to internal evaluation. Public provider selection, project ingestion, authentication/usage limits, agent tooling, patch review and isolated execution remain unfinished. The website retains the user's confirmed public access and the GitHub repository remains private.
