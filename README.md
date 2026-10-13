# DevTwin Engineer

A local skill for evidence-based Python investigation and focused repairs.

Four core workflows cover repository understanding, reproduction, implementation, and regression verification. Feature tracing, change impact, API compatibility and dependency diagnosis are draft workflows with development tasks and rubrics. Five further capabilities remain planned; agent-level behavior is unverified.

Start with [SKILL.md](SKILL.md), [local development](docs/installation.md), the [evaluation procedure](docs/evaluation.md), and the [incremental roadmap](docs/roadmap.md).

See the [support matrix](docs/supported-environments.md) for exercised environments and pending runtime checks. Completed increments are pushed to the private GitHub repository after verification.

```sh
python -m unittest discover -s tests -v
python scripts/validate_package.py .
```

Run all local development gates with `python scripts/check_project.py .`; the JSON report preserves failures and skips and checks a temporary archive after extraction.

Python 3.10+ is required; local checks use no third-party dependencies. The deliberately broken checkout fixture is copied to temporary directories for checks. Agent execution may incur runtime costs. Clean-session integrations, benchmarks, licensing, and public hosting remain pending.
