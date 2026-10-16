# DevTwin use cases: AI code review, repository analysis, and Python debugging

DevTwin combines selected-source investigation with reviewed patches and isolated Python test verification. Choose a focused question and include the files needed to answer it. The web workspace currently accepts up to 30 UTF-8 files and 16,000 total selected bytes; it does not index an entire repository.

## Understand an unfamiliar GitHub repository

Import a repository selection, preview entry points and related modules, and choose **Repository understanding** or **Feature tracing**.

Example task:

> Explain how a request reaches this handler. Identify the relevant entry points, dependencies, and missing context, with references to the selected source.

The report provides source-linked findings and proposed checks. Missing files limit conclusions; include the relevant helpers and documentation before assuming a dependency is absent from the repository.

## Investigate a Python bug with regression tests

Select a small Python module and its standard-library `unittest` files. Use **Bug reproduction** or **Regression testing** to investigate the failure. Review a focused proposal, then separately approve Docker verification.

Example task:

> Investigate the empty-input failure. Preserve the selected tests and propose the smallest source change consistent with the expected behavior.

Original and candidate tests run in separate constrained containers. A demonstrated repair needs baseline failure and candidate success. Dependency installation and non-Python test runners are not supported by the current verification worker.

## Review API compatibility before a change

Select the interface, its callers, relevant documentation, and tests. Choose **API compatibility** and **Change impact**.

Example task:

> Review changing this return field from an integer to a string. Identify affected selected callers, compatibility assumptions, and regression checks.

This is a source investigation, not proof that every external consumer remains compatible.

## Run a broader source review with all 13 workflows

Use the workflow board's batch control after reviewing the provider policy and approving up to 13 model calls. It runs sequential source analyses, records individual errors, and supports combined JSON export. Database, security, and performance investigations need relevant source and context; missing evidence should remain an explicit limitation.

The batch does not automatically modify files, run tests, or certify the repository as secure or production-ready.

## Bring the guidance into Codex or Claude Code

Install the shared project skill or build the local plugin package. The agent runtime provides its own account, tools, and authorization model. Codex project execution has been exercised; Claude Code package validation passed, with runtime execution pending.

## Start here

- [Local browser quick start](../README.md#run-locally)
- [Public Docker images](https://hub.docker.com/r/raimalraja/devtwin-engineer)
- [Codex setup](../integrations/codex/README.md) and [Claude Code setup](../integrations/claude-code/README.md)
- [Provider policy and OpenRouter configuration](openrouter.md)
- [Verification evidence and remaining work](completion-status.md)
