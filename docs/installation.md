# Local development and invocation

Use Python 3.10 or newer. No dependency installation is needed for this increment.

```sh
python -m unittest discover -s tests -v
python scripts/validate_package.py .
```

For a manual development session, ask your agent to read this repository's SKILL.md and use its linked references on an authorized copy of the checkout fixture. Do not repair the canonical intentionally broken fixture.

Frontmatter and progressive references follow the [official skill documentation](https://learn.chatgpt.com/docs/build-skills), checked on 2026-10-12. Automatic discovery, clean-session installation, and Claude Code integration remain unverified. No global agent configuration is changed by these commands.
