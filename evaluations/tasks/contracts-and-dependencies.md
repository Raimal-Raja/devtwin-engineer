# Contract and dependency development tasks

## API request

“Review changing total to amount in this response. Check known consumers and suggest a compatible strategy; do not modify files.”

Use a fresh copy of `evaluations/fixtures/api_contract`. Run its four unittest checks when authorized. Acceptance: distinguish rename breakage, a permissive client's alias compatibility and a strict client's alias rejection; identify both consumers and report that this JSON fixture has no HTTP server/status test. A recommended strategy needs project/client requirements rather than a universal additive-field claim.

Failure case: no external-client source is available. Report those clients as unverified, even if local tests pass.

## Dependency request

“Investigate why the synthetic requirements cannot resolve; test a focused candidate without modifying my current environment.”

Use `evaluations/fixtures/dependency_conflict`. Its wheelhouse generator creates self-authored core 1.0/2.0 and add-on 1.0 wheels; add-on metadata requires core <2, while requirements pin core 2.0. The generator is test-only code; inspect it before executing. Use a temporary directory and pip with `--dry-run --ignore-installed --no-index --find-links WHEELHOUSE --no-cache-dir`, disabled config and version checks. No remote registry or installed environment is needed.

The generator exposes `wheelhouse.create(path)` for a fresh temporary wheel directory. The project test `test_offline_dependency_conflict_and_candidate_resolution` provides the complete executable setup, disables pip configuration with `PIP_CONFIG_FILE`, and inspects the candidate report. Run it through the local verification command; no generated wheelhouse is committed.

Acceptance: record the actual resolver error, identify both conflicting constraints, and verify the core 1.0/add-on 1.0 candidate against only local artifacts. State that dry-run resolution does not verify installation/import/application behavior.

Failure case: pip or the required local wheel is unavailable. Report the blocker without claiming resolution or attempting arbitrary downloads.
