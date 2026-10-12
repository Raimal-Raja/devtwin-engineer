# Increment 8: local verification gates and archive verifier — 2026-10-13

Added `check_project.py` to validate source, execute tests in a subprocess, build a temporary archive and verify its integrity and extracted links. JSON reports preserve test logs, failures and skip reasons. Empty or entirely skipped suites fail. No network, hosted CI or Git mutations are required by this command.

Added `verify_archive.py` to check portable filenames, path traversal, duplicates/case collisions, symlink entries, entry and size limits, manifest membership/hashes and package links after safe temporary extraction. It does not execute archived Python. The verifier is included in the private archive's allowlist.

Executed with Python 3.12.14 on Windows:

- `python scripts/check_project.py .`: passed all three local gates. 44 tests ran, 42 passed and 2 real filesystem symlink checks were skipped.
- `python scripts/build_package.py . dist/devtwin-engineer-increment-8.zip`: succeeded with 13 selected files plus the manifest.
- `python scripts/verify_archive.py dist/devtwin-engineer-increment-8.zip`: valid, 13 files, signature not verified.

Archive SHA-256: `a1035157e471b378b2d95c9b10bbf1eb242ad3edbab9a46bdb104117405d2141`.

New tests reject archive tampering, unlisted files, traversal, case collisions, reserved portable filenames and synthetic symlink entries. Worker tests verify failing/empty/all-skipped suite handling and capture import/test stdout inside valid JSON logs. Synthetic symlink archive coverage does not replace the skipped real filesystem checks.

These are local development gates. A manifest is not an author signature; independent agent evaluation, automatic runtime activation, licensing and public release remain pending. Generated archives remain local and ignored by Git.
