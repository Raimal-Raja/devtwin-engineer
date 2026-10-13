# Supported environments and evidence

| Component | Status | Evidence |
| --- | --- | --- |
| Python library development fixture | Exercised locally | Checkout tests and evaluator-side acceptance checks |
| Tracing and impact workflows | Draft; Codex development exercise completed | Fresh synthetic order-flow reviews and tests; broader independent evaluation pending |
| API and dependency workflows | Draft; Codex development exercise completed | JSON client matrix and offline resolver conflict/candidate evidence; no API transport or installation claim |
| Database and security workflows | Draft; Codex development exercise completed | SQLite migration and synthetic ownership review; no production or authentication integration |
| Migration fixture engine | Exercised locally | SQLite 3.53.1 bundled with Python 3.12.14; in-memory, single-connection checks only |
| Performance/docs/delivery workflows | Draft; Codex development exercise completed | Local measurements/profile, CLI example verification and evidence-based delivery; no production or public-release claim |
| Offline resolver tooling | Requires pip dry-run/report support | Local Python environment has pip 26.2.1; no package installation is performed by the exercise |
| Windows helper execution | Exercised locally | Bundled Python 3.12.14; standard-library unittest |
| Python 3.10+ syntax target | Declared, minimum-version execution pending | Helpers use Python 3.10-compatible syntax and APIs |
| Explicit Codex skill invocation | Exercised in fresh sessions | Library/HTTP repair and blocked reproduction; earlier inconclusive attempts remain historical |
| Codex automatic skill selection | One development request exercised | Ordinary tracing/impact prompt selected/read the installed skill; not an accuracy benchmark |
| Runtime folder installation | Exercised locally | Fresh temporary projects for `.agents/skills` and `.claude/skills`; resources validate, existing files preserved |
| Plugin installation/discovery | Codex installer exercised; Claude manifest validated | Separate temporary Codex CLI home; installed skill appears in prompt metadata. Claude 2.1.263 validation passed; Claude execution deferred |
| Web catalog/setup application | Exercised locally | Workflow search, runtime/format/OS selection, task handoff and package downloads; browser checks and Node logic tests; no browser agent execution |
| Codex CLI tooling | Synthetic runtime exercises completed | `0.162.0-alpha.17.2`; current successful tool execution, [increment 18](../evaluations/results/increment-18.md); initial setup errors remain historical |
| Claude Code integration | Manifest validated; inference deferred by user | Version 2.1.263, no signed-in account; activation/behavior remain unverified |
| FastAPI applications | Synthetic Codex HTTP repair exercised | Agent and parent checks passed; unchanged protected files; no live deployment/auth/database coverage; [procedure](fastapi-evaluation.md) |
| Web hosting | Updated deployment succeeded | User confirmed preserving existing public website access; repository stays private |
| Linux and macOS | Unverified | No platform execution recorded |

Explicit file-based invocation and automatic runtime discovery are separate checks. The project does not infer compatibility from shared Markdown metadata alone. Evaluation harnesses execute trusted synthetic code; they do not isolate untrusted repositories.
