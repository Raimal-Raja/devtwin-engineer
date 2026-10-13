# Increment 18: private completion candidate — 2026-10-13

The user asked to complete the project before release, then chose to keep the repository private with licensing undecided and to defer Claude execution. Later, after Sites reported existing public website access, the user explicitly confirmed keeping that access. No repository visibility change, public marketplace submission or license selection was performed.

## Codex runtime evidence

Used the existing default model/configuration with Codex CLI 0.162.0-alpha.17.2, ephemeral sessions and workspace-write sandbox. No bypass flags or model overrides were used. Skill resources were installed into fresh synthetic targets. Raw logs remain ignored/private.

- Library repair: successful reads of SKILL.md and core references; five existing tests initially failed in the two omitted/None cases. The agent added three separate boundary tests, demonstrated failure and then passed eight tests after a focused repair. Parent evaluator passed the candidate suite plus three acceptance methods; protected tests and user note retained their hashes. An unscoped Git check picked up parent-repository metadata. That limitation is recorded; subsequent targets were initialized as their own repositories to bound Git discovery.
- HTTP repair: the agent reproduced two HTTP 500 failures, repaired optional discount handling and passed all five existing HTTP methods. Parent TestClient checks passed with unchanged test, requirements and user-note hashes. The first parent host-sandbox attempt timed out; approved execution outside that host sandbox completed in 0.219 seconds. The pinned fixture stack emitted an httpx deprecation warning, retained as a test-environment limitation rather than a product-runtime claim.
- Blocked reproduction: the supplied interpreter path intentionally did not exist. The agent attempted that executable, reported no Python/tests executed, labelled the predicted TypeError unverified, substituted no interpreter and edited no files. Parent hashes confirmed source/tests/user note unchanged.
- Plugin loader: in a separate temporary CLI home, the real `plugin marketplace add` and `plugin add` commands both exited 0. The installed cache path and skill description appeared in `debug prompt-input`. Existing user configuration/credentials were not copied or changed. This proves installation/discovery separately from project-skill inference; it is not a full authentication test of every registered-plugin surface.
- Automatic selection: a fresh ordinary tracing/impact request did not name the skill. Its transcript shows successful SKILL.md/reference reads, six passing order tests, and temporary in-memory contract checks. Fixture source bytes remained unchanged. This is one development selection example, not a recall/precision or cross-runtime benchmark.

## Expanded workflow exercise

Prepared seven fresh synthetic fixture directories with a realistic combined review request covering tracing, impact, API compatibility, dependency diagnosis, migrations, ownership, performance, documentation and delivery. No intended answers, evaluator reports or candidate correction instructions were provided to the fresh agent. The fixture source itself includes worked candidate examples where appropriate; this is not held-out or blinded evaluation.

The bounded session exited 0 after 145.672 seconds. It executed 24 supplied tests (6 order, 4 contract, 5 migration, 6 ownership, 3 performance), an offline resolver conflict/candidate comparison, CLI example checks, profiling/measurement and temporary edge-case experiments. The report distinguished strict-client alias rejection, trusted-actor assumptions, SQLite scope, resolution versus installation, validated-input dependence of aggregation and uninspected external consumers. All input fixture hashes remained unchanged; only permitted temporary experiments were added.

Measured synthetic sales samples yielded 16.181 ms baseline and 0.3446 ms candidate medians with 450,000 versus 3,000 row visits. These are shared-machine development observations, not agent improvements or production performance claims. The report found different behavior on malformed unrequested rows; equivalence requires the validated-input contract. No packages were installed by the review exercise.

## Claude and hosting

Claude Code 2.1.263 is now installed. Its real plugin validator initially passed with an attribution warning. Added project author metadata; the rebuilt plugin passed without warnings. Authentication status was `loggedIn: false`; the user explicitly chose to leave Claude execution pending. Manifest validation is not model invocation evidence.

Retried the matching increment-16 Site archive/source after the previous upload transport failures; deployment succeeded. The updated candidate archive was built from pushed Site commit `3af2b865580f0076968f99a5107031685eaa4cd7`. Private deployment then refused because the current Site audience was public; no deployment started through that operation. The user explicitly confirmed preserving public access. Deploying the saved version `appgprj_6acdcff2b9708191a7e29e6d372ee59d~appgver_7883b767ca208191a36066c4ec2f2e23` succeeded as deployment `appgdep_6ace57d1c2f48191b2e17f011ebdada5`. URL: https://devtwin-engineer-workspace.royalskunk16.chatgpt.site. Browser reload confirmed the updated Codex/Claude status, all thirteen workflows and the plugin download link. No access policy was changed by this increment.

Final local gates passed: 62 Python tests ran, 60 passed and two symlink-creation cases skipped because this Windows environment cannot create them. All six web tests passed, package validation passed and the 28-file skill archive verified with SHA-256 `18b92ccd1ee0ab9839375ac406822f8cbfdcd1fd2a99663c16532f7a5f8abc76`.

Remaining release work includes deferred Claude execution, broader independent baseline comparisons/pilot feedback, license selection and public-release review. These gates are not marked complete by development smokes.
