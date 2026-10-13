# Internal browser workspace

This increment connects browser ZIP selection, selected-file preview and source investigation through a loopback-only HTTP backend. It requires no Codex/Claude plugin. It is an internal development preview, separate from the hosted public catalog. NVIDIA trial restrictions still apply; submit only nonconfidential inputs you are authorized to send.

Set the provider credential as `NVIDIA_API_KEY` in the backend environment. Set a separate `DEVTWIN_SESSION_TOKEN` with at least 32 random ASCII letters/digits. Neither value belongs in source control or command-line arguments. The browser session token is not the NVIDIA key. Enter it in the local page; it stays in page memory and is not stored by the application.

Alternatively, select Groq or Gemini using `DEVTWIN_PROVIDER` and its environment key as described in [free-tier providers](free-providers.md). Preview displays the selected provider/model and notice before approval. It rejects a submission naming a different provider and never silently switches after a quota failure.

From the repository root:

```powershell
python -m backend.server --port 8765
```

Open `http://127.0.0.1:8765/`. Enter the workspace token, choose a ZIP and list exact selected paths, one per line. Preview validates and displays selected source and hashes without calling NVIDIA. Choose a workflow and enter the task. Approve submission of the selected nonconfidential files before investigating. Review the report and optionally download its JSON. Source/result text is rendered literally, including HTML-like content. Inputs are locked during requests to avoid attaching results to a changed task/selection.

The server binds only `127.0.0.1`, enforces its exact Host and Origin, requires the separate token for API calls, serves only three explicit static paths, accepts bounded JSON requests, and limits investigations to five requests per rolling minute. It makes no automatic provider retries. Responses disable caching and apply a restrictive content security policy. HTTP request logs are disabled. ZIP files and analysis are held in memory; reports are persisted only by explicit browser download. These controls are for local development, not a production authentication/abuse system. A shared computer administrator or process may inspect memory/environment; no multi-user isolation is claimed.

Seven real loopback HTTP test methods exercise authentication, origin/host rejection, preview, consent/input limits, rate limits, provider/unexpected failures and asset path controls. Browser QA uses synthetic files with a simulated provider. Earlier live NVIDIA checks establish provider availability separately; this does not claim a live browser-to-model test or security audit.

The next [patch review workflow](patch-review.md) supports one selected-file proposal and approved ZIP export. It does not modify your checkout. An autonomous agent tool loop, isolated execution and production provider/access/hosting validation remain unfinished. Do not expose this development server through a public tunnel.
