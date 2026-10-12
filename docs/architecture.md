# Foundation decisions

The product is a local instruction package, not an application-map platform or hosted agent. Four core workflows load progressively. Python 3.10+ libraries are the initial scope; this increment is checked on Windows with Python's standard-library unittest runner. Other operating systems and FastAPI have not been exercised.

No network, credentials, model calls, or paid services are needed for local fixture checks. Agent runtime costs depend on the user's setup. Evidence stays temporary by default; private source and logs are not collected for telemetry. Fixtures contain synthetic code only.

The broken checkout fixture remains unchanged. Automated checks copy it to temporary directories to reproduce the defect and verify a reference correction. This validates the exercise and checks, not the effectiveness of autonomous skill invocation.
