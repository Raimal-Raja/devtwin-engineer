# Supported environments and evidence

| Component | Status | Evidence |
| --- | --- | --- |
| Python library development fixture | Exercised locally | Checkout tests and evaluator-side acceptance checks |
| Windows helper execution | Exercised locally | Bundled Python 3.12.14; standard-library unittest |
| Python 3.10+ syntax target | Declared, minimum-version execution pending | Helpers use Python 3.10-compatible syntax and APIs |
| Explicit agent invocation | Inconclusive attempt | Fresh evaluator contexts were dispatched but returned no results before interruption |
| Codex automatic skill discovery | Unverified | No installed clean-session discovery check |
| Claude Code integration | Unverified | No runtime session exercised |
| FastAPI applications | Planned | No FastAPI fixture or dependency environment yet |
| Linux and macOS | Unverified | No platform execution recorded |

Explicit file-based invocation and automatic runtime discovery are separate checks. The project does not infer compatibility from shared Markdown metadata alone. Evaluation harnesses execute trusted synthetic code; they do not isolate untrusted repositories.
