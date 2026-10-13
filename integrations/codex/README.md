# Codex project adapter

As checked on 2026-10-13, official guidance documents repository skills under `.agents/skills` and explicit invocation via `$` mentions or `/skills` in CLI/IDE. See [official Codex skill guidance](https://learn.chatgpt.com/docs/build-skills).

From this source package, using an existing target project:

```sh
python scripts/install_skill.py . /path/to/project --runtime codex
```

This copies a validated package into the selected project's `.agents/skills/devtwin-engineer/`. It refuses existing destinations and changes no user-wide settings. Open a fresh Codex session in that project and explicitly invoke `$devtwin-engineer` on an authorized task. If a skill is not visible, check runtime discovery separately; copying files is not evidence that activation worked.

The installed [canonical skill](../../SKILL.md) and references remain shared. Codex CLI `0.162.0-alpha.17.2` exercised explicit skill reading, library/HTTP repairs and truthful blocked reproduction in fresh synthetic sessions. An ordinary tracing/impact request also selected and read the skill without an explicit mention. The real plugin installer and prompt-input inspection passed in a separate temporary CLI home. Project-skill execution and registered-plugin discovery are distinct evidence; this does not establish broad effectiveness or every plugin surface. Historical Windows helper failures remain recorded. The private source repository contains the [smoke-test procedure](https://github.com/Raimal-Raja/devtwin-engineer/blob/main/docs/runtime-smoke-test.md) and [completion evidence](https://github.com/Raimal-Raja/devtwin-engineer/blob/main/evaluations/results/increment-18.md).
