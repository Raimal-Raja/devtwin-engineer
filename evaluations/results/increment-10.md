# Increment 10: API and dependency draft workflows — 2026-10-13

Added API-compatibility and dependency-diagnosis references, routing, package resources, realistic development requests, failure cases and rubrics. All four expanded workflows remain explicitly draft and unverified at the agent level; five further capabilities remain planned.

API fixture checks distinguish a breaking response rename from an alias that preserves a permissive client but breaks a strict client. JSON serialization is exercised, but the fixture has no HTTP server or status-code checks.

The dependency fixture generates self-authored wheels in a temporary directory. With pip 26.2.1, local-only dry-run resolution reproduced `ResolutionImpossible` for core 2.0 plus add-on 1.0 requiring core <2. A temporary core 1.0/add-on 1.0 candidate resolved, and pip's report confirmed both selected versions. Pip configuration, indexes, cache and version checks were disabled; no package installation or host-environment change was performed.

Executed `python scripts/check_project.py .` on Windows/Python 3.12.14: all three gates passed. 47 project tests ran, 45 passed and 2 real filesystem symlink checks were skipped. The API fixture separately passed four contract tests. Archive validation passed with 17 selected resources.

These are synthetic development examples, not independent agent evaluation or real dependency/application compatibility evidence. Installation/import verification, external API consumers, HTTP behavior, runtime activation and core independent evaluation remain unverified.
