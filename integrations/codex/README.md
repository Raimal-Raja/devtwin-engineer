# Codex project adapter

As checked on 2026-10-13, official guidance documents repository skills under `.agents/skills` and explicit invocation via `$` mentions or `/skills` in CLI/IDE. See [official Codex skill guidance](https://learn.chatgpt.com/docs/build-skills).

From this source package, using an existing target project:

```sh
python scripts/install_skill.py . /path/to/project --runtime codex
```

This copies a validated package into the selected project's `.agents/skills/devtwin-engineer/`. It refuses existing destinations and changes no user-wide settings. Open a fresh Codex session in that project and explicitly invoke `$devtwin-engineer` on an authorized task. If a skill is not visible, check runtime discovery separately; copying files is not evidence that activation worked.

The installed [canonical skill](../../SKILL.md) and references remain shared. Local installer/layout checks are exercised. A fresh explicit CLI session started with `0.162.0-alpha.17.2`, but Windows sandbox helper setup blocked all resource reads and task commands. Activation, successful repair and automatic selection remain unverified. The private source repository contains the [smoke-test procedure](https://github.com/Raimal-Raja/devtwin-engineer/blob/main/docs/runtime-smoke-test.md) and [recorded result](https://github.com/Raimal-Raja/devtwin-engineer/blob/main/evaluations/results/increment-14.md).
