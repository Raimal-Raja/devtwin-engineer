# Private skill archive

This archive contains the [core skill](../SKILL.md), linked workflows, templates and local helpers. It has no agent runtime, model dependency, telemetry or hosted backend. It is a private development package; public distribution and a license remain pending.

Extract the archive to a fresh directory, then run Python 3.10+:

```sh
python scripts/validate_package.py .
```

Ask an authorized agent to read SKILL.md explicitly and use its relevant references on your target repository. This instruction does not install or confirm automatic discovery in Codex or Claude Code. Clean-session runtime integrations remain unverified. Optional Git inspection requires a Git executable; all helpers use the Python standard library.

`manifest.json` records the included file sizes and SHA-256 digests. It provides integrity evidence for these files, not an author signature. Preserve directory structure so relative links resolve. The development evaluation fixtures and results are deliberately not included.
