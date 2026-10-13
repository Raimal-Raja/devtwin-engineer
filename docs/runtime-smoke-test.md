# Private Codex runtime smoke test

This is an integration check on the development checkout fixture, not a held-out benchmark. Use a fresh run directory and the configured runtime model; do not supply the expected correction. The parent evaluator and acceptance code stay outside the target. This is a prompt boundary, not enforced read isolation.

From the source project, using your available Python executable:

```sh
python scripts/evaluate_checkout.py prepare .workspaces/runtime-smoke-new
python scripts/install_skill.py . .workspaces/runtime-smoke-new/target --runtime codex
git -C .workspaces/runtime-smoke-new/target init
codex exec --ephemeral --skip-git-repo-check --sandbox workspace-write -C .workspaces/runtime-smoke-new/target --json -o .workspaces/runtime-smoke-new/final.md
```

Supply the generated request, explicitly invoke `$devtwin-engineer`, and adapt `target/` to the current directory. Require preservation of `test_checkout.py` and `user-note.txt`, forbid sibling evaluator/source reads and delegation, and provide the available Python path. Do not give the agent evaluator-side acceptance checks. Keep raw session logs in the ignored run directory; review before sharing because inherited runtime configuration can expose unrelated context.

After the session finishes, run from the source project:

```sh
python scripts/evaluate_checkout.py check .workspaces/runtime-smoke-new
```

Inspect the actual command events and candidate diff. An agent announcing a skill does not prove it read the resources. A zero CLI exit status does not prove repair: require successful resource reads, reproduction, focused changes, passing evaluator checks, and unchanged protected files. Record startup/tool errors separately from task failures. Do not bypass sandbox protections to turn a blocked run into a pass.

Initialize the synthetic target as its own Git repository before agent execution. An increment-18 run without that boundary picked up parent-repository metadata via an unscoped Git command. The local repository prevents Git discovery from climbing to the development checkout; it does not enforce arbitrary filesystem read isolation.

The flags follow [official non-interactive guidance](https://learn.chatgpt.com/docs/non-interactive-mode) and the installed CLI's help. On Windows, local helper setup may block commands even after a session starts; increment 14 encountered that condition. A new increment-18 session successfully read the skill, reproduced and repaired checkout, and passed parent checks. This is explicit invocation evidence, not a semantic automatic-selection benchmark. Ephemeral mode avoids persisted session files, but explicit output files and runtime operational state may still be written.
