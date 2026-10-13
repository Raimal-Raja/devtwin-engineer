# Increment 13: private project runtime adapters — 2026-10-13

Consulted and opened current [official Codex guidance](https://learn.chatgpt.com/docs/build-skills) and [official Claude Code guidance](https://code.claude.com/docs/en/skills). Added thin adapter documentation and a common explicit-project installer preserving the canonical skill/resources. The supported project layouts are `.agents/skills` for Codex and `.claude/skills` for Claude Code. No hooks, runtime-specific agents or global configuration are introduced.

The installer builds/verifies a private package before writing, requires an existing selected project, rejects linked destinations and refuses overwrite of an existing skill folder. Bundled builder, installer and allowlist make the installed resources self-contained. A partial destination may remain after filesystem failure; atomic installation and concurrent replacement isolation are not claimed.

Executed `python scripts/check_project.py .` on Windows/Python 3.12.14: after correcting a test comparison between Windows short and canonical temporary paths, all three local gates passed. 54 tests ran, 52 passed and 2 real filesystem symlink checks were skipped. Archive verification passed with 28 resources plus manifest.

Executed the installer CLI against `.workspaces/runtime-adapter-13` for Codex: copy succeeded with 28 resources and `activation_verified: false`. No model inference was started. After strengthening the installer test, reran its three tests successfully, including invocation of the installed bundle's own CLI to copy into a second fresh project for both runtime layouts. Existing user files and user-owned installations were preserved.

Codex CLI `0.162.0-alpha.17.2` was inspected with version/help only; sandbox output warned that home/PATH aliases could not be created. Claude Code was not found on PATH, and no Claude runtime version/session was tested. File layout and link validation do not establish fresh-session discovery, activation, behavior or full runtime compatibility. Those gates, independent evaluation, licensing and public release remain pending.
