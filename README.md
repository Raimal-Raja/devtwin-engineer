# DevTwin Engineer

A shared engineering skill, Codex and Claude plugin packages, and a web catalog/setup dashboard for evidence-based Python investigation and focused repairs.

All thirteen capabilities have workflow references: four core repair workflows and nine expanded drafts, with synthetic development tasks and rubrics. Local package/fixture checks exist; agent-level effectiveness and runtime activation remain unverified.

Start with [SKILL.md](SKILL.md), [local development](docs/installation.md), the [evaluation procedure](docs/evaluation.md), and the [incremental roadmap](docs/roadmap.md).

See the [support matrix](docs/supported-environments.md) for exercised environments and pending runtime checks. Completed increments are pushed to the private GitHub repository after verification.

Private project adapters are documented for [Codex](integrations/codex/README.md) and [Claude Code](integrations/claude-code/README.md). File installation is tested; runtime activation remains unverified.

See [plugin and web setup](docs/plugins-and-web.md) to build plugin marketplaces or the web application. The dashboard offers workflow search, package downloads, runtime-specific setup and task handoff export.

```sh
python -m unittest discover -s tests -v
python scripts/validate_package.py .
```

Run all local development gates with `python scripts/check_project.py .`; the JSON report preserves failures and skips and checks a temporary archive after extraction.

Python 3.10+ is required; core local checks use no third-party dependencies. The [optional FastAPI fixture](docs/fastapi-evaluation.md) needs its isolated dependency environment and is skipped when unavailable. Deliberately broken fixtures are copied to temporary directories for checks. Agent execution may incur runtime costs. Clean-session integrations, benchmarks, licensing, and public hosting remain pending.
