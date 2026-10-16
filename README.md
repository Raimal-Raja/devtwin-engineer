<div align="center">

# DevTwin Engineer

### AI code analysis, repository investigation, and verified Python repairs.

**Understand a repository. Trace the problem. Review the change. Verify the result.**

[![Docker Hub: public app and worker images](docs/assets/docker-badge.svg)](https://hub.docker.com/r/raimalraja/devtwin-engineer)
[![Engineering workflows: 13](docs/assets/workflows-badge.svg)](#13-engineering-workflows)
[![Status: development candidate](docs/assets/status-badge.svg)](#current-evidence-and-boundaries)

**[Website](https://raimal-raja.github.io/devtwin-engineer/) · [Docker Hub](https://hub.docker.com/r/raimalraja/devtwin-engineer) · [Setup guide](docs/installation.md) · [Verification evidence](docs/completion-status.md)**

[Quick start](#run-locally) · [How it works](#three-views-one-connected-workspace) · [13 workflows](#13-engineering-workflows) · [Skills and plugins](#skills-and-plugins) · [FAQ](#faq) · [Documentation](#documentation)

<code>python scripts/start_openrouter.py</code>

<br /><br />

<img src="docs/assets/devtwin-overview.svg" alt="DevTwin product illustration: inspect selected source, investigate with 13 workflows, and review patches with Docker test evidence" width="1080" />

<sub>Product illustration · Selected-file analysis · Python unittest verification · Local execution backend</sub>

</div>

---

## AI developer tools for codebase understanding and debugging

**DevTwin Engineer is an AI developer tool for code analysis, code review, repository understanding, and Python debugging.** It helps developers investigate selected source files, review focused changes, and examine the evidence behind a repair. Connect a GitHub repository or upload a project ZIP, preview the files, and move from investigation to a reviewed patch and isolated verification.

Use the browser workspace independently of a Codex or Claude installation, or install the shared engineering skill in your coding agent. The web workspace needs its own backend and configured model provider; isolated verification also requires Docker.

**DevTwin's goal: make AI-assisted engineering easier to inspect, reproduce, and review.**

## Three views. One connected workspace.

| View | What you can do |
| --- | --- |
| **Welcome** | Meet the creator, explore DevTwin, and follow CLI and supported plugin-browser setup guides. |
| **Project Explorer** | Import GitHub files or a ZIP, inspect source and SHA-256 hashes, review selection sizes, and see why files were omitted. |
| **Workflow board** | Run investigations, review reports, propose a patch, approve export, compare tests in Docker, or run a bounded repair loop. |

![DevTwin workflow: connect and preview, investigate source, review evidence, review a patch, verify in Docker, and export](docs/assets/workflow.svg)

[Open the full-size workflow diagram](docs/assets/workflow.svg). This is a bundled SVG image, so it does not require Mermaid support.

GitHub imports are **read-only and pinned to a commit**. The web app does not push changes, open pull requests, or apply generated patches to your original repository.

## Choose your interface

<table>
<tr>
<td width="33%" valign="top">

### Browser workspace

Connect selected GitHub files or a ZIP. Inspect source, run investigations, review patches, and approve Docker verification.

[Run locally](#run-locally)

</td>
<td width="33%" valign="top">

### Codex skill / plugin

Bring shared engineering instructions into an existing project. Project skill execution and plugin discovery have been exercised.

[Codex setup](integrations/codex/README.md)

</td>
<td width="33%" valign="top">

### Claude Code package

Use the same canonical skill resources. Native package validation passed; model execution remains deferred.

[Claude Code setup](integrations/claude-code/README.md)

</td>
</tr>
</table>

## 13 engineering workflows

| Workflow | What it helps you investigate |
| --- | --- |
| **Repository understanding** | Structure, entry points, responsibilities, and conventions. |
| **Feature tracing** | How behavior travels through the selected source. |
| **Change impact** | Affected callers, contracts, and assumptions. |
| **Bug reproduction** | A focused reproduction and any missing prerequisites. |
| **Dependency diagnosis** | Dependency requirements and environment assumptions. |
| **Implementation** | A focused change grounded in the available evidence. |
| **Regression testing** | Checks that expose a bug and protect existing behavior. |
| **API compatibility** | Interface changes and consumer expectations. |
| **Database review** | Schema, migration, and data assumptions. |
| **Security review** | Concrete trust boundaries and security-sensitive paths. |
| **Performance investigation** | Measurement and profiling opportunities. |
| **Documentation verification** | Whether supplied documentation matches supplied source. |
| **Delivery preparation** | Evidence and unresolved checks for a change review. |

**One control can queue all 13 source investigations.** After separate approval for up to 13 provider calls, DevTwin runs them sequentially with pacing, per-workflow progress, error reporting, stop-after-current control, and combined JSON export. This batch does not automatically change code or execute tests.

## From a bug report to a reviewed repair

For a small Python module and its standard-library tests, try a task such as:

> Investigate why this function returns the wrong result for an empty input. Propose a minimal fix, preserve the selected tests, and identify the evidence needed to verify it.

1. **Connect and select:** import explicit files and inspect the actual analysis scope.
2. **Prepare an investigation:** choose a workflow, describe the task, and approve the displayed provider/data policy.
3. **Review the evidence:** inspect source-linked findings, proposed checks, limitations, and a downloadable report.
4. **Propose and review a change:** inspect the diff and full replacement for one selected, existing non-test file. Approve selected-file ZIP export separately.
5. **Verify in an isolated runner:** approve original/candidate Python tests in separate disposable Docker containers.
6. **Run a bounded repair loop:** approve one investigation, up to two proposals, and up to two baseline/candidate check attempts. A second proposal follows failing checks only.

A **demonstrated repair** requires observed baseline failure and candidate success. When both versions pass, DevTwin reports checks passing without claiming a demonstrated fix. Missing prerequisites, provider failures, and blocked execution stay visible.

## Run locally

Prerequisites: a source checkout, **Python 3.10+**, Docker with Linux containers, and a supported model-provider key. The exercised runner uses a pinned Python 3.12 image. Node.js is required for web development tests.

From the repository root, prepare a fresh installation:

```sh
docker pull python:3.12-slim
docker pull docker:cli
python scripts/prepare_docker.py .
```

Preparation records image digests and creates ignored `.env.docker` with separate random app and worker tokens. It refuses to overwrite existing configuration.

Start with the supported OpenRouter free-only route:

```sh
python scripts/start_openrouter.py
```

The helper prompts for the key without displaying it, sends a bounded synthetic smoke request, and starts the Docker app if that succeeds. It does not save the key to a project file; Docker retains it in the app container environment.

Some free routes require allowing upstream storage/training. **Only if you accept those terms for public or synthetic inputs**, use:

```sh
python scripts/start_openrouter.py --allow-public-inputs
```

Open **[http://127.0.0.1:8765/](http://127.0.0.1:8765/)**. Enter `DEVTWIN_SESSION_TOKEN` from `.env.docker` in **Workspace session token**. Provider and GitHub API keys belong in backend configuration, never in that field.

Free-only routing prevents intentional paid-model fallback. Provider capacity, quotas, and continued free availability are external constraints. See [OpenRouter setup](docs/openrouter.md), [Docker instructions](docs/docker.md), and [free hosting prerequisites](docs/free-hosting.md).

## Docker Hub images

**[View DevTwin Engineer on Docker Hub](https://hub.docker.com/r/raimalraja/devtwin-engineer)** — public app and verification-worker images are available now.

```sh
docker pull raimalraja/devtwin-engineer:app
docker pull raimalraja/devtwin-engineer:worker
```

| Component | Moving tag | Commit-specific tag |
| --- | --- | --- |
| Browser backend and UI | `raimalraja/devtwin-engineer:app` | `raimalraja/devtwin-engineer:app-ed18167` |
| Private Docker verification worker | `raimalraja/devtwin-engineer:worker` | `raimalraja/devtwin-engineer:worker-ed18167` |

Both published images target **Linux/amd64**. Use the published digests for immutable references:

```text
App:    raimalraja/devtwin-engineer@sha256:5a213bf3e081ca5e4a79ca6a6d56658ef0fd9e4b60781de5d069e54d71f54ed6
Worker: raimalraja/devtwin-engineer@sha256:d91d0113b7f8e96e2a85e469b551bbb4184f268d1fea0a83093554a54addbdb1
```

Pulling an image downloads the packaged component; the full workspace still needs the app/worker network, session and worker tokens, pinned test-runner image, and provider configuration described in [Docker setup](docs/docker.md). The current `compose.yaml` builds from source by default. These image references can be used in an operator-managed Compose configuration; they do not embed API keys or session tokens. Keep the worker private because it controls the Docker daemon.

## Skills and plugins

Install the repository-hosted **Codex plugin**:

```sh
codex plugin marketplace add Raimal-Raja/devtwin-engineer
codex plugin add devtwin-engineer@devtwin-engineer-local
```

Or, inside **Claude Code**:

```text
/plugin marketplace add Raimal-Raja/devtwin-engineer
/plugin install devtwin-engineer@devtwin-engineer-local
```

Restart the agent after installation. These packages contain the shared skill and its 13 workflow references; they do not bundle an agent subscription or the web execution backend. Claude runtime behavior remains unverified. See the [handover](docs/project-handover.md) for completion evidence and remaining release gates.

Install the canonical skill into an existing project:

```sh
# Codex project skill
python scripts/install_skill.py . /path/to/project --runtime codex

# Claude Code project skill
python scripts/install_skill.py . /path/to/project --runtime claude-code
```

Start a fresh session in that project. Invoke `$devtwin-engineer` in Codex or `/devtwin-engineer` in Claude Code. Installation refuses existing destinations and does not change user-wide settings.

Build a fresh local plugin marketplace:

```sh
python scripts/build_plugins.py . dist/plugin-marketplace-new
```

Follow the [plugin setup guide](docs/plugins-and-web.md), [Codex adapter](integrations/codex/README.md), or [Claude Code adapter](integrations/claude-code/README.md) for installation and discovery. Packages are available through this repository marketplace, not listed in an official plugin directory. Codex execution and plugin discovery have been exercised; Claude package validation passed, while Claude model execution remains deferred.

## Current evidence and boundaries

| Area | Current scope |
| --- | --- |
| **Local web app** | Three views, selected-file imports, source investigations, reviewed patch export, Docker verification, and bounded repair. |
| **13 workflows** | Prerequisite resource audit, synthetic source-analysis coverage, and batch orchestration checks. Every model finding still needs review. |
| **Latest recorded checks** | 152 Python cases: **150 passed, 2 Windows symlink skips**. **22 web tests passed**. See [increment 36](docs/increment-36.md). |
| **Selection limits** | Up to 30 UTF-8 files, 16,000 total selected bytes, and a 2 MiB ZIP. Only selected files are analyzed. |
| **Test execution** | Standard-library Python `unittest`; no automatic dependency installation or arbitrary-language runner. |
| **Isolation** | Disposable containers with no network, bounded resources/output/time, and no host source mounts or provider credentials. The private worker controls a Docker daemon; public multi-user sandbox hardening is pending. |
| **Evidence quality** | Schema and citation bounds are validated; semantic correctness is not guaranteed. Source analysis alone runs no tests. |
| **Hosting** | The public catalog/setup site is separate from the local execution backend. Public backend deployment remains pending. |
| **Release** | Public Docker development images are available; the source repository is public. License and formal release remain undecided; no open-source license is currently granted. |

Selected files and workflow state are held in memory; refreshing loses the session state. Submit only inputs approved for the displayed provider policy.

## FAQ

<details>
<summary><strong>Do I need Codex or Claude to use the web app?</strong></summary>

No. The local browser workspace uses its own backend and configured provider. Docker is required for isolated verification. Agent skills and plugins are separate interfaces.

</details>

<details>
<summary><strong>Does Run all 13 automatically repair my repository?</strong></summary>

No. It queues source investigations with separate approval for up to 13 model calls. Patch review, export, test execution, and bounded repair have their own controls and approvals.

</details>

<details>
<summary><strong>Does DevTwin upload my code?</strong></summary>

Approved source investigations send the selected files and task to the configured model provider. Review the displayed policy before submitting. The storage/training-enabled free route is restricted to public or synthetic inputs. Docker test execution has no network access.

</details>

<details>
<summary><strong>Can I analyze an entire repository?</strong></summary>

The current web app analyzes explicit selections: up to 30 UTF-8 files and 16,000 total selected bytes. It is not a full-repository indexer. Import diagnostics explain omitted files.

</details>

<details>
<summary><strong>Can I use the Docker Hub images immediately?</strong></summary>

You can pull both public images now. Running the complete workspace also requires app/worker configuration, tokens, a provider key, and the pinned test image. The source Compose file builds locally by default. See [Docker setup](docs/docker.md).

</details>

<details>
<summary><strong>Is DevTwin production-ready or open source?</strong></summary>

It is a development candidate with tested local flows and public Docker images. Hosted multi-user execution, broader independent evaluation, and formal release remain pending. The source repository is public and licensing remains undecided.

</details>

## Development checks

```sh
python -m unittest discover -s tests -v
python scripts/validate_package.py .
python scripts/check_project.py .
```

The combined checker runs Python tests, declared web suites, package validation, and archive checks. These are development gates, not independent effectiveness benchmarks.

## About the creator

**Raimal Raja is a Machine Learning Engineer and the creator of DevTwin.** His work spans Python, machine learning, computer vision, LLM fine-tuning, FastAPI, and MLOps. DevTwin brings that practical AI engineering focus to developer tools: understand the source, make a focused change, and inspect the evidence behind the result.

[GitHub](https://github.com/Raimal-Raja) · [LinkedIn](https://www.linkedin.com/in/raimal-raja-kolhi-860a032bb/) · [Portfolio](https://coder.kvtech.net)

## Documentation

Start with [practical use cases](docs/use-cases.md) to choose a workflow, then follow the setup and verification guides.

- [Canonical skill](SKILL.md) and [13 capability prerequisites](docs/capability-prerequisites.md)
- [Installation](docs/installation.md) and [supported environments](docs/supported-environments.md)
- [Repair loop](docs/repair-loop.md) and [evaluation procedure](docs/evaluation.md)
- [GitHub Pages deployment](docs/github-pages.md)
- [Completion status](docs/completion-status.md), [deployment readiness](docs/deployment-readiness.md), and [roadmap](docs/roadmap.md)
- [GitHub About description and suggested topics](docs/github-about.md)
