# Skill archive

This archive contains the [core skill](../SKILL.md), linked workflows, templates and local helpers. It has no agent runtime, model dependency, telemetry or hosted backend. It is a development package from the public repository; licensing remains undecided.

Extract the archive to a fresh directory, then run Python 3.10+:

```sh
python scripts/validate_package.py .
```

Ask an authorized agent to read SKILL.md explicitly and use its relevant references on your target repository. This instruction does not install or confirm automatic discovery in Codex or Claude Code. Codex project execution has development coverage; Claude runtime execution remains deferred. Optional Git inspection requires a Git executable; all helpers use the Python standard library.

`manifest.json` records the included file sizes and SHA-256 digests. It provides integrity evidence for these files, not an author signature. Preserve directory structure so relative links resolve. The development evaluation fixtures and results are deliberately not included.

To verify an archive using a trusted copy of the helper:

```sh
python scripts/verify_archive.py /path/to/archive.zip
```

Verification checks portable paths, entry/size limits, manifest hashes and extracted package links in a temporary directory. It does not execute archived Python files. A passing manifest confirms internal consistency; it cannot establish the author or defend against an attacker replacing both files and manifest. Use a trusted distribution channel.

For project installation, use the [Codex adapter](../integrations/codex/README.md) or [Claude Code adapter](../integrations/claude-code/README.md). The bundled installer requires an explicit source and existing project, validates the selected package before copying and refuses existing skill destinations. Installation does not verify activation or run model inference.
