# Increment 7: private skill archive — 2026-10-13

Added an explicit package allowlist and a deterministic ZIP builder. The archive contains only the core skill, its linked workflows/templates, three local helpers and package-usage instructions. Fixtures, results, Git internals and temporary exercises are excluded. A generated manifest records included file sizes and SHA-256 hashes.

Executed with Python 3.12.14 on Windows:

- `python -m unittest discover -s tests -v`: 34 tests ran; 32 passed and 2 real symlink checks were skipped.
- `python scripts/build_package.py . dist/devtwin-engineer-increment-7.zip`: succeeded with 12 selected files plus the generated manifest. Source validation and isolated selected-resource validation passed inside the builder.

Archive SHA-256: `e8ceaee791f6b88fa0e82adc6b96572e6b47ab52410ee04ea473a7a30c5f8769`.

New tests verify repeated-build byte equality, clean extraction and package validation, manifest integrity, omission of evaluation/private workspace content, overwrite prevention, unsafe allowlist rejection, and detection of a dependency omitted from selected resources.

The generated archive is ignored by Git; its source, allowlist, tests and build instructions are pushed. This is a private development artifact, not a published release, pip package, signed distribution or verified automatic runtime installation. A license, clean-session runtime adapters and independent evaluation remain pending.
