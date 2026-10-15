# Local browser workspace

The browser app connects selected-file preview, GitHub import, source investigation, reviewed proposals, ZIP export, isolated verification and a bounded repair loop. It requires no Codex/Claude plugin. It is separate from the public catalog; the full backend is not publicly hosted.

Use [Docker setup](docker.md) and [OpenRouter setup](openrouter.md). The current local configuration uses free Nemotron with the user-approved public/synthetic-only storage/training policy. Provider secrets stay in the app environment; the private worker receives no provider keys. Enter `DEVTWIN_SESSION_TOKEN` from `.env.docker` in the page, never a provider API key. It stays in page memory rather than browser storage.

At http://127.0.0.1:8765/:

1. Upload a ZIP and list selected paths, or [browse a GitHub repository](github-workspace.md), select files and import them. Blank branch uses the default branch.
2. Preview files and hashes without a model call. Select a workflow, enter the task and review the provider policy. Confirm public/synthetic inputs when required.
3. Investigate selected source and review evidence. Citation bounds and JSON structure are checked; semantic correctness remains unverified. Download the report if useful.
4. Request a focused patch. Review its diff and complete replacement. Export requires explicit approval; existing selected tests are preserved and the original repository remains unchanged.
5. Separately approve isolated execution. The worker runs baseline and candidate unittest cases in disposable containers and reports actual counts, failures, skips and limits.
6. Alternatively approve the bounded loop: one investigation, proposal and verification, with one further candidate only after failed tests. Review the final replacement before export.

Selected UTF-8 source is limited to 30 files and 16,000 bytes; ZIP uploads are limited to 2 MiB. Test execution supports selected standard-library Python unittest modules with importable module paths, including namespace test directories without `__init__.py`. GUI applications, dependency installation and arbitrary user commands are not execution features.

The direct server entry point defaults to loopback. Compose publishes only the app at 127.0.0.1:8765 and keeps the verification worker private. Exact Host/Origin, separate app/worker tokens, explicit static assets, bounded JSON, no-cache/CSP headers, disabled request logging and rolling request limits are enforced. Browse/import share two requests per minute, model calls five, and verification two; the repair loop reserves its maximum budget. No automatic transport retry, paid fallback or billing upgrade occurs. See [runner controls](isolated-runner.md).

API checks exercise authentication, preview, consent, live analysis, proposals, approval-gated export, Docker execution, the bounded loop and source preservation. Client input tests exercise missing/wrong tokens, repository URLs and selection errors. These are local development checks, not visual browser certification, an independent security audit or public deployment approval. Do not expose the development server through a public tunnel.
