# DevTwin Engineer

A shared engineering skill, Codex and Claude plugin packages, and a web catalog/setup dashboard for evidence-based Python investigation and focused repairs.

All thirteen capabilities have workflow references: four core repair workflows and nine expanded drafts, with synthetic development tasks and rubrics. Fresh Codex development sessions exercised repair, blocked reporting and expanded reviews. Broader effectiveness and Claude behavior remain unverified.

Start with [SKILL.md](SKILL.md), [local development](docs/installation.md), the [evaluation procedure](docs/evaluation.md), and the [incremental roadmap](docs/roadmap.md).

See the [support matrix](docs/supported-environments.md) for exercised environments and pending runtime checks. Completed increments are pushed to the private GitHub repository after verification.

The requested standalone web agent is now a separate implementation track. Its first [NVIDIA backend integration](docs/nvidia-backend.md) supports bounded internal trial calls; repository execution from the public website is still in progress.

The [thirteen prerequisite resource sets](docs/capability-prerequisites.md) are audited by the project checker. Work currently prioritizes Codex; Claude execution is explicitly deferred. See [deployment readiness](docs/deployment-readiness.md) for the remaining full-web-agent gates.

Private project adapters are documented for [Codex](integrations/codex/README.md) and [Claude Code](integrations/claude-code/README.md). Codex skill execution and plugin installation/discovery are exercised; Claude's package validates, with model execution deferred by the user. See [completion status](docs/completion-status.md).

See [plugin and web setup](docs/plugins-and-web.md) to build plugin marketplaces or the web application. The dashboard offers workflow search, package downloads, runtime-specific setup and task handoff export.

```sh
python -m unittest discover -s tests -v
python scripts/validate_package.py .
```

Run all local development gates with `python scripts/check_project.py .`; the JSON report includes Python tests, all declared web `.test.mjs` suites, failures/skips, and a temporary archive after extraction. Node.js must be available for the source project's web tests; the exercised version is 23.6.1.

Python 3.10+ is required; core local checks use no third-party dependencies. The [optional FastAPI fixture](docs/fastapi-evaluation.md) needs its isolated dependency environment and is skipped when unavailable. Deliberately broken fixtures are copied to temporary directories for checks. Agent execution may incur runtime costs. Claude execution, independent benchmarks, licensing and formal release remain pending. The web dashboard is live with public access confirmed by the user.

Run the standalone app locally with the [Dockerized app and private verification worker](docs/docker.md). The local repair flow has passed real original/candidate Python tests; the public catalog is separate from this backend.

The local [bounded repair loop](docs/repair-loop.md) connects investigation, proposal, isolated checks and one failure-driven retry. [Free hosting prerequisites](docs/free-hosting.md) track the remaining hosted-service requirements.
