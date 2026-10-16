# Plugin distribution and setup dashboard

The user's updated product scope has three interfaces: Codex plugin/skill, Claude Code plugin/skill, and a web application. The initial web workflow is the user-selected plugin catalog and setup dashboard. The original project specification remains historical input; the updated scope here takes precedence for development.

## Install the repository marketplace

The public repository now contains both native marketplace manifests and the embedded plugin. Users do not need a local package build first.

Codex:

```sh
codex plugin marketplace add Raimal-Raja/devtwin-engineer
codex plugin add devtwin-engineer@devtwin-engineer-local
```

Claude Code, in its interactive session:

```text
/plugin marketplace add Raimal-Raja/devtwin-engineer
/plugin install devtwin-engineer@devtwin-engineer-local
```

Restart and confirm plugin/skill discovery. See the [Codex adapter](../integrations/codex/README.md), [Claude Code adapter](../integrations/claude-code/README.md), and [handover](project-handover.md). The marketplace identifier retains `-local` for compatibility; GitHub and local sources use the same identity. Official-directory listing, Claude runtime testing, licensing, and production hosting remain separate.

## Build or verify a package

Build local plugin marketplaces from the canonical skill:

```sh
python scripts/build_plugins.py . dist/plugin-marketplace-new
```

The fresh output contains a local Codex marketplace, a local Claude marketplace and one plugin folder with portable `plugin.json`, `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json`. All reference/helper paths stay inside the embedded skill. A build manifest records hashes. Output overwrite and linked ancestors are rejected; filesystem failure can leave partial output. This is local structure/integrity checking, not validation by either live runtime or public-directory acceptance.

For Codex, add the generated marketplace with `codex plugin marketplace add ./dist/plugin-marketplace-new`, then use the Plugins browser to install the package and start a fresh session. For Claude Code, use `/plugin marketplace add ./dist/plugin-marketplace-new` and `/plugin install devtwin-engineer@devtwin-engineer-local`, then start a fresh session. Paths are examples relative to the source root; extracted dashboard ZIPs use the `devtwin-engineer-marketplace` folder instead. Project-only skill installation continues to use `install_skill.py`.

Packaging follows current [OpenAI plugin guidance](https://developers.openai.com/plugins/build/plugins) and [Claude manifest guidance](https://code.claude.com/docs/en/plugins-reference). Runtime policies/account access still apply. License remains pending; public repository distribution does not grant an open-source license.

Build the dashboard and its downloads:

```sh
python scripts/build_web.py . web/dist
node --test web/model.test.mjs
python -m http.server 4173 --bind 127.0.0.1 --directory web/dist
```

The output path must be fresh. Use a new path for repeat local builds; hosting expects `web/dist`. The Sites source checkout uses the same builder with its selected output directory. The static application uses no external fonts, model API, telemetry, browser storage or credentials. Search, category selection, runtime/OS/format selection, clipboard copying and Markdown handoff export run in-browser. Task text is not sent to a server by the application. It is not retained across page reloads.

Downloads contain the same skill resources as the canonical package, not private evaluation logs. The site starts owner-private. No runtime installation, agent execution, account connection, marketplace publication or GitHub repository visibility change is performed by the dashboard. Model-runtime testing, licensing and public release remain separate gates.

Historical increment 16 status (superseded by the public catalog deployment and local workspace): the local app, packages and browser checks passed. Owner-private Site creation and source push succeeded, but the deployment archive upload failed with a platform transport error. The hosted app is not live yet; retain the existing Site identity rather than creating another. Details are in the [increment record](../evaluations/results/increment-16.md).
