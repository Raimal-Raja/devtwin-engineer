# Increment 28 — OpenRouter free inference integration

On 2026-10-14 the user requested OpenRouter and provided a key. The key was used only through process/container environments, not source files or archive payloads. It was not printed in diagnostic output or committed. Because it was pasted into chat, the operator should rotate it before public deployment.

The public OpenRouter model catalog showed paid prompt/completion prices for the unsuffixed Nemotron Ultra ID and zero prices for `nvidia/nemotron-3-ultra-550b-a55b:free`. The backend allowlists only that free variant and `openrouter/free`. It requests zero prompt/completion/per-request pricing, required parameter support, data-collection denial and disabled upstream fallback. No paid plugin, model list, credit purchase or client retry is performed. Nonzero reported costs, incomplete answers and malformed responses stop the request. Actual and requested model IDs are recorded separately.

The free Nemotron variant does not advertise JSON-mode support, so it uses JSON instructions and strict local schema/citation validation without sending unsupported `response_format`. Its reasoning is disabled. The general free router receives JSON-mode requirements and chooses a compatible upstream free model; consent discloses that forwarding and model variability.

Live evidence:

- A bounded free-Nemotron smoke returned HTTP 503 and stopped.
- A separately selected general free-router smoke returned HTTP 429 and stopped.
- A read-only key-status request authenticated successfully and reported a Free-tier account with 50 daily requests remaining and zero used. The failures are therefore not evidence that the daily allowance is exhausted. Their precise upstream cause remains unverified.
- Neither failed smoke triggered the setup helper's Docker startup. The local app was subsequently configured explicitly for the free Nemotron variant so the operator can test availability later without selecting a paid model.

The final full project checker passed 139 Python tests with two Windows symlink skips (137 passed), six web tests, package/resource and archive gates. Targeted tests cover fixed endpoints, free-only routing, paid-model rejection, privacy/parameter controls, actual-model reporting, redaction, nonzero cost, missing keys, quota/error stop behavior and setup preservation. The hidden-key helper does not save the key or forward unrelated provider keys; a failed smoke leaves running containers untouched.

The deployment bundle contains the OpenRouter setup helper and documentation via an explicit credential-free allowlist. Before the policy approval below, only configuration/error paths were ready and successful inference remained blocked. Public hosting still requires a confirmed free VM/account and hosted job/authentication/security checks. No paid resource, license decision, public repository change or release tag was made; Claude remains deferred.

## Final approved-policy validation

The later routing diagnostic identified the 404 as a data-policy mismatch. The user explicitly approved upstream storage/training for public or synthetic inputs only. A configurable policy was added with a matching browser disclosure and server-enforced public-input confirmation. The default remains collection denial; no private/confidential input is authorized in the approved mode. OpenRouter key patterns are also screened during source ingestion.

After that approval and concise-report guidance, all thirteen workflow analyses passed schema/citation checks with free Nemotron. The summaries were spot-checked against the synthetic fixtures; this is not a held-out effectiveness comparison or proof that every semantic claim is correct. A real HTTP repair loop through the Dockerized app passed in one attempt: original five tests had two errors; candidate five passed, observed failure resolved, no host changes applied. Public Requests import also passed at commit `611c6162cbc4ac2020a2f91c7cfa4f3abf9bbb60`. Earlier failures above remain part of the evidence.

The final policy regression gate passed 141 Python tests with two Windows symlink skips (139 passed), six web tests, package/resource and archive gates. The final local configuration is ready for public/synthetic test inputs. See the [machine-readable development evidence](../evaluations/results/increment-28.json) and [OpenRouter setup](openrouter.md). Full public hosting, broader independent evaluation and licensing/release remain separate.
