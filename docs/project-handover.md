# DevTwin development handover

Updated 2026-10-16. DevTwin is a local development product with a public source repository, public Docker images, and repository-hosted Codex/Claude Code plugin packages. This handover closes the current packaging increment; it is not a production certification or an official plugin-directory release.

## Delivered

- Three-view browser workspace: Welcome, Project Explorer, and Workflow board.
- Read-only, commit-pinned GitHub imports and ZIP selection with explicit limits and previews.
- Thirteen engineering source-investigation workflows, single and sequential batch execution, and downloadable reports.
- Reviewed single-file patch proposals, separately approved ZIP export, isolated Python tests, and bounded repair.
- Public app/worker images at [Docker Hub](https://hub.docker.com/r/raimalraja/devtwin-engineer).
- Canonical project skill, embedded self-contained plugin, both marketplace manifests, and runtime-specific setup instructions.
- A published-package consistency check to detect divergence from the canonical skill resources.

## Install

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

Restart the runtime and confirm discovery. Claude runtime testing remains deferred by the owner. Codex native registration/installation/listing was checked in an isolated temporary home, without changing the normal user configuration. Local marketplace checks do not establish remote install availability until the new files are pushed.

The `-local` marketplace name is retained for existing installations, including when its source is GitHub. These are skill-only plugins: no MCP service, subscription, provider key, or Docker backend is installed with them.

## Maintenance and evidence

Run `python scripts/check_project.py .` for the combined local gates and `python scripts/check_plugin_distribution.py .` for the published package comparison. The checked-in plugin is generated with `scripts/build_plugins.py`; regenerate in a fresh output directory, review its files, and copy only the generated distribution paths into the repository. Rename its root `build-manifest.json` to `plugin-build-manifest.json`. Never manually edit the embedded skill instead of its canonical source.

See [increment 36](increment-36.md) for the final test counts and current validation record. Earlier live model and Docker evidence remains in the completion/increment reports; packaging checks do not repeat or supersede those behavioral checks.

## Remaining release and production work

- License decision and formal release/version policy.
- Authenticated Claude workflow evaluation, deliberately deferred.
- Full browser acceptance of the redesigned interface and broader platform coverage.
- Independent effectiveness comparisons and authorized pilot feedback.
- Production authentication, per-user jobs/quotas, worker containment review, and verified hosting resources for a public execution service.
- Official directory submission if desired; publishing a repository marketplace is a separate distribution path.

The public catalog website is not the full execution backend. The web verification worker supports selected Python standard-library tests, not arbitrary dependencies/languages. No paid service, subscription, hosting purchase, or new license is enabled by this handover.
