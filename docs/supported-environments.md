# Supported environments and evidence

| Component | Status | Evidence |
| --- | --- | --- |
| Python library development fixture | Exercised locally | Checkout tests and evaluator-side acceptance checks |
| Tracing and impact workflows | Draft; agent-level behavior unverified | Synthetic order-flow fixture, tasks and rubrics |
| API and dependency workflows | Draft; agent-level behavior unverified | JSON clients and offline synthetic wheel metadata; no HTTP verification |
| Database and security workflows | Draft; agent-level behavior unverified | In-memory SQLite migration and synthetic ownership checks; no production or authentication integration |
| Migration fixture engine | Exercised locally | SQLite 3.53.1 bundled with Python 3.12.14; in-memory, single-connection checks only |
| Offline resolver tooling | Requires pip dry-run/report support | Local Python environment has pip 26.2.1; no package installation is performed by the exercise |
| Windows helper execution | Exercised locally | Bundled Python 3.12.14; standard-library unittest |
| Python 3.10+ syntax target | Declared, minimum-version execution pending | Helpers use Python 3.10-compatible syntax and APIs |
| Explicit agent invocation | Inconclusive attempt | Fresh evaluator contexts were dispatched but returned no results before interruption |
| Codex automatic skill discovery | Unverified | No installed clean-session discovery check |
| Claude Code integration | Unverified | No runtime session exercised |
| FastAPI applications | Planned | No FastAPI fixture or dependency environment yet |
| Linux and macOS | Unverified | No platform execution recorded |

Explicit file-based invocation and automatic runtime discovery are separate checks. The project does not infer compatibility from shared Markdown metadata alone. Evaluation harnesses execute trusted synthetic code; they do not isolate untrusted repositories.
