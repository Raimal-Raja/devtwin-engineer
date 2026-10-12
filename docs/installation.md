# Local development and invocation

Use Python 3.10 or newer. No dependency installation is needed for this increment.

```sh
python -m unittest discover -s tests -v
python scripts/validate_package.py .
```

For a complete local development check:

```sh
python scripts/check_project.py .
```

This trusted-source command validates the package, runs tests in a subprocess, builds a temporary archive and verifies its integrity and extracted links. Its JSON report includes failures and skip reasons. Empty or entirely skipped test suites fail. The command makes no network requests or Git writes and does not publish a release; runtime activation and licensing remain separate gates.

For a manual development session, ask your agent to read this repository's SKILL.md and use its linked references on an authorized copy of the checkout fixture. Do not repair the canonical intentionally broken fixture.

Frontmatter and progressive references follow the [official skill documentation](https://learn.chatgpt.com/docs/build-skills), checked on 2026-10-12. Automatic discovery, clean-session installation, and Claude Code integration remain unverified. No global agent configuration is changed by these commands.

## Build a private archive

```sh
python scripts/build_package.py . dist/devtwin-engineer-dev.zip
```

The builder validates both the source tree and a temporary copy of selected resources. It includes only the paths in `package-files.json`, normalizes CRLF to LF, uses fixed archive timestamps and records file hashes in a manifest. Repeated builds from identical inputs produce identical archive bytes. Existing output files are never overwritten; choose another output name for a new build.

Extract into a fresh directory and follow [package usage](package-usage.md). The archive is a local private development artifact, not a pip package or verified runtime installation. Licensing and public release remain pending. Generated archives stay ignored by Git; the build recipe is committed and pushed.
