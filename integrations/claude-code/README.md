# Claude Code project adapter

As checked on 2026-10-13, official guidance documents project skills under `.claude/skills/<name>/SKILL.md` and explicit `/skill-name` invocation. See [official Claude Code skill guidance](https://code.claude.com/docs/en/skills).

From this source package, using an existing target project:

```sh
python scripts/install_skill.py . /path/to/project --runtime claude-code
```

This copies a validated package into the selected project's `.claude/skills/devtwin-engineer/`. It refuses existing destinations and changes no personal settings. In a fresh Claude Code session in that project, invoke `/devtwin-engineer` on an authorized task and verify loading before claiming compatibility.

The [canonical skill](../../SKILL.md) and references remain shared; no Claude-specific hooks, agents or tool dependencies are added. Filesystem/layout checks are exercised, but Claude Code was not found on the development PATH and no runtime session/version was tested. Activation and behavioral compatibility remain unverified.
