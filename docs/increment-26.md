# Increment 26 — local Docker deployment

Validated on Windows on 2026-10-14. Docker Desktop was installed from its signed official installer without automatic agreement acceptance. The user confirmed the Linux engine was running after first-start setup.

The app and verification-only worker build from recorded official repository digests. Compose publishes only the app on 127.0.0.1:8765. Separate random tokens are in ignored `.env.docker`, with its local Windows ACL restricted to the operator. Build context excludes credentials, Git metadata and evaluation workspaces. Only the private worker receives the Docker daemon socket; project jobs receive no socket, host source mount or provider credentials.

Live checks passed:

- Direct isolated checkout verification: original five tests had two errors; the focused candidate passed all five.
- Real HTTP flow through the Dockerized app: preview, NVIDIA proposal, approval, worker baseline/candidate execution and ZIP export. Original five tests had two errors, candidate five passed, and exported selected test bytes were preserved.
- Both Compose services reached healthy status and the browser loaded the local workspace.
- Project gates: 120 Python tests, 118 passed and two Windows symlink checks skipped; six web tests passed; package, capability-resource and archive gates passed.

Simulation coverage includes missing Docker, invalid image configuration, approval boundaries, process/output deadlines, failed cleanup, malformed reports, zero/all-skipped tests and worker authentication/route separation. Live execution is evidence of basic functionality, not a containment audit. Only small selected-file Python standard-library unittest suites are supported. The daemon-authorized worker is for dedicated local development; public multi-user hosting, autonomous repair iteration, independent benchmark comparisons, licensing and formal release remain pending. Claude execution remains deferred by user choice.

See [Docker setup](docker.md) and [runner boundaries](isolated-runner.md).
