# Claude Code skill and plugin setup

As checked on 2026-10-13, official guidance documents project skills under `.claude/skills/<name>/SKILL.md` and explicit `/skill-name` invocation. See [official Claude Code skill guidance](https://code.claude.com/docs/en/skills).

## Install the public repository plugin

In an authenticated Claude Code session:

```text
/plugin marketplace add Raimal-Raja/devtwin-engineer
/plugin install devtwin-engineer@devtwin-engineer-local
```

Restart the session, check the plugin browser with `/plugin`, and invoke `/devtwin-engineer:devtwin-engineer`. For a source checkout, `/plugin marketplace add .` uses the same marketplace. The stable marketplace identifier retains `-local` for compatibility. No paid account or authenticated Claude runtime is included; runtime testing remains deferred.

## Install only the project skill

From this source package, using an existing target project:

```sh
python scripts/install_skill.py . /path/to/project --runtime claude-code
```

This copies a validated package into the selected project's `.claude/skills/devtwin-engineer/`. It refuses existing destinations and changes no personal settings. In a fresh Claude Code session in that project, invoke `/devtwin-engineer` on an authorized task and verify loading before claiming compatibility.

The [canonical skill](../../SKILL.md) and references remain shared; no Claude-specific hooks, agents or tool dependencies are added. Filesystem/layout checks are exercised. Claude Code 2.1.263's native `plugin validate` passed the generated plugin with no warnings after adding project attribution. Its CLI reports no signed-in account; the user explicitly deferred Claude model execution. Activation and behavioral compatibility therefore remain unverified. This is a repository-hosted development candidate, not a claim that Claude runtime testing passed.
