# Contributing

This repository is private and licensing is undecided. Work only through access authorized by the owner. Keep changes focused and preserve unrelated edits.

Run `python -B scripts/check_project.py .` with the project evaluation environment and Node available. It validates package resources, thirteen-capability prerequisites, Python tests, catalog tests and archive integrity. The optional FastAPI fixture needs its isolated dependencies; report any skips. Local browser modules also need `node --check backend/ui/app.mjs`. Runtime/production evidence is separate from local unit tests.

Use self-authored synthetic fixtures, keep raw model logs and generated workspaces ignored, and never commit provider/GitHub keys or private project source. Backend UI changes should receive local browser verification. Do not execute imported repositories on the host or imply a process timeout is an execution sandbox.

For skill changes, preserve the canonical package allowlist, validate a clean build and use fresh scoped Codex examples where warranted. Record actual commands, failures, skips and remaining limits. Completed increments are committed and pushed as authorized; deployment and formal release follow the documented readiness gates.
