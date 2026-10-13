# Incremental roadmap

- Implemented: local foundation, four core references, templates, five development requests, broken checkout fixture, automated fixture checks and package validation; repeatable exercise preparation, evaluator-side contract checks and core rubric.
- Helper development: bounded metadata inventory implemented independently of the open runtime evaluation gate; real Windows symlink checks remain unverified where creation is restricted.
- Helper development: read-only Git status summary implemented with staged/unstaged, rename, untracked and preservation checks, including suppression of repository content filters.
- Helper development: package validation expanded to documentation links, bounded UTF-8 reads, explicit scalar metadata and unsafe-path rejection. It remains a documented subset of YAML and Markdown validation.
- Packaging: explicit-allowlist private ZIP builder validates selected resources in isolation, records file hashes, and passes clean-extraction checks. Runtime discovery and public release remain unverified.
- Local verification: one command checks source metadata/links, executed tests and skips, archive integrity and clean extraction without hosted CI or publication.
- Capability development: feature tracing and conservative change-impact references are drafts with an order-flow fixture, realistic requests, failure cases and rubrics; agent-level evaluation remains pending.
- Capability development: API compatibility and dependency diagnosis are drafts with permissive/strict JSON consumers and an offline synthetic resolver exercise; agent-level and real-project behavior remain unverified.
- Capability development: database/security reviews are drafts with existing-data SQLite migration checks and synthetic ownership/access cases. Production engine, concurrency and authentication integration remain unverified.
- Capability development: all thirteen references are present; final three drafts cover performance, documentation verification and delivery. Local measurements and examples are development evidence, not a passed agent-evaluation/release gate.
- Runtime adapters: official project layouts are documented and an explicit-project installer is checked in temporary projects. Discovery and activation remain unverified; no global agent configuration is changed.
- Runtime evaluation: a fresh explicit Codex CLI session started in increment 14, but Windows sandbox helper setup blocked shell and JavaScript access. The agent reported the blocker; successful resource reads and repair remain unverified. See the [repeatable smoke procedure](runtime-smoke-test.md).
- HTTP development: optional FastAPI checkout fixture covers application 500 failures, strict request 422 validation, explicit discounts, zero floor and health preservation with in-process HTTP tests. Independent agent behavior remains unverified.
- Updated product scope: Codex/Claude plugin packages share the canonical skills; the initial web application is the user-selected plugin catalog and setup dashboard. Package generation, setup instructions, workflow search and task handoff export are implemented; live runtime installation remains unverified.
- Verification audit: the unified project gate now includes every declared web suite and rejects missing Node, empty suites and all-skipped runs. Synthetic failing JavaScript tests verify that the overall project check fails correctly.
- Next: independent core agent evaluation, blocked reproduction and preservation scenarios in clean sessions; HTTP fixture agent evaluation.
- Evaluation status: two independent contexts were dispatched in increment 3 but returned no results before interruption. This gate remains open; see [recorded limitations](../evaluations/results/increment-3.md).
- Then: evaluate all workflows against their tasks and rubrics, extend filesystem/platform coverage, and establish independent held-out tasks.
- Then: tested Codex and Claude Code adapters.
- Then: 15–20 independent baseline comparisons and authorized pilot testing.
- Finally: reviewed license/security contact, static site, authorized hosting and release.

Private source repository: [Raimal-Raja/devtwin-engineer](https://github.com/Raimal-Raja/devtwin-engineer). Completed increments are committed and pushed after verification, as requested. Licensing, public publication, and release gates remain pending. No benchmark improvement or runtime compatibility is claimed.
