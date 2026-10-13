# Foundation decisions

The user's updated scope adds Codex and Claude plugin distributions and a web application around the shared instruction package. The first web application is a plugin catalog and setup dashboard, as selected by the user. It filters thirteen workflows, serves generated package downloads, selects runtime/installation format, and prepares an agent task handoff. Repository execution remains in the user's agent runtime; browser agent execution is future work.

The canonical SKILL.md, references and helpers are packaged once. Plugin builds embed the verified skill bundle under `skills/devtwin-engineer` and add portable, Codex-compatible and Claude manifests plus local marketplaces. Generated wrappers do not introduce hooks or MCP services. Project skill installation remains supported independently of plugin installation.

Core library and synthetic FastAPI HTTP fixtures have been exercised on Windows/Python 3.12.14. Automatic runtime activation remains unverified, and the fresh Codex CLI exercise was blocked by Windows helper setup. The web dashboard distinguishes package integrity from runtime loading; no automatic connection or verification is implied by a download.

No network, credentials, model calls, or paid services are needed for local fixture checks. Agent runtime costs depend on the user's setup. Evidence stays temporary by default; private source and logs are not collected for telemetry. Fixtures contain synthetic code only.

The broken checkout fixture remains unchanged. Automated checks copy it to temporary directories to reproduce the defect and verify a reference correction. This validates the exercise and checks, not the effectiveness of autonomous skill invocation.
