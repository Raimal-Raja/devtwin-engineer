# Increment 21: internal browser/API workspace — 2026-10-13

Added an authenticated loopback-only HTTP server and a separate browser UI for the requested standalone engineering experience. Users can select a ZIP, list exact source paths, preview source/hashes without inference, choose one of thirteen workflows, approve nonconfidential source submission, investigate and download a report. No Codex/Claude plugin is needed for this internal preview. The hosted public catalog remains unchanged.

Server controls include exact Host/Origin enforcement, a separate environment-configured workspace token, explicit static asset routes, JSON/body limits, rolling five-per-minute investigation limits, no caching, restrictive CSP and disabled request logs. Browser text is rendered literally. Inputs are locked while requests run; re-preview clears prior reports/approval. These local development controls are not a production security audit or multi-user sandbox.

Seven real loopback HTTP test methods passed: preview/no inference, authentication/Host/Origin, consent/input limits, inference/rate limits, provider/unexpected errors, static routes/security headers and token validation. Full project gates passed with 81 Python tests run, 79 passing and two Windows symlink cases skipped, plus all six web tests and package/archive checks. The final browser script passed Node syntax checking after the input-lock change.

Browser QA used a disposable local server with a simulated provider and a built-in synthetic ZIP. Verified file upload, selected-source/hash preview, workflow/task selection, explicit submission approval, report rendering and JSON download. Repeated the flow after the input-lock fix and saved an ignored screenshot. This is simulated browser inference; earlier successful real NVIDIA calls are separate evidence. The owned preview server was stopped after QA.

Public production inference, production authentication/usage controls, agent tools, patch review/application and isolated tests remain unfinished. NVIDIA trial usage stays internal; no public provider endpoint, API credential, source upload or execution service was published.
