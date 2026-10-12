# DevTwin Engineer

A local skill for evidence-based Python investigation and focused repairs.

Increment 1 contains four core workflows: repository understanding, reproduction, implementation, and regression verification. The other nine capabilities remain planned.

Start with [SKILL.md](SKILL.md), [local development](docs/installation.md), the [evaluation procedure](docs/evaluation.md), and the [incremental roadmap](docs/roadmap.md).

```sh
python -m unittest discover -s tests -v
python scripts/validate_package.py .
```

Python 3.10+ is required; local checks use no third-party dependencies. The deliberately broken checkout fixture is copied to temporary directories for checks. Agent execution may incur runtime costs. Clean-session integrations, benchmarks, licensing, and public hosting remain pending.
