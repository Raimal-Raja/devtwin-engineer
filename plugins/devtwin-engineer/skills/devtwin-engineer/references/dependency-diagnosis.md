# Dependency diagnosis (draft workflow)

Activation: failed installation, incompatible package upgrade, import failure or environment drift in a Python repository.

Required evidence: interpreter/platform, active environment, declared and locked requirements, resolver/import error, package metadata and indexes involved. Do not print registry credentials or full private logs.

Investigation: distinguish unsatisfiable constraints, missing artifacts, unavailable networks, unsupported Python/platform, build failure and import incompatibility. Identify the conflicting constraints before changing a pin. Use official package metadata/changelogs when compatibility facts need verification; local synthetic metadata is sufficient only for a synthetic exercise.

Actions: select a focused candidate based on the conflicting edges. Use an isolated environment or an offline synthetic wheelhouse when appropriate. Do not upgrade every package, discard lockfiles, change indexes or disable integrity checks to make an installation succeed. Established task authorization governs installation; never install arbitrary artifacts from untrusted repositories merely to investigate.

Verification: reproduce the resolver failure, check the candidate resolution, then test actual installation/imports and relevant behavior when possible. A successful dry run establishes resolution only, not import or application correctness. Preserve lockfile conventions and record the environment used.

Failure handling: absent artifacts or network access must be reported without guessing package availability. Missing build/test tooling limits the verified scope; never claim the candidate is fully compatible from metadata alone.

Example: a synthetic add-on requires core `<2` while the project pins core `==2`. The evidence supports testing a core `==1` candidate, not an unrelated environment overhaul.

Failure case: the resolver succeeds but an import or behavior check fails. Report the candidate incomplete and investigate the runtime incompatibility.

Expected output: conflict evidence, focused candidate, commands/outcomes, checks not run and remaining uncertainty. Broader independent and Claude evaluation remain pending.
