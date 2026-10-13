# Optional FastAPI development fixture

The [fixture](../evaluations/fixtures/fastapi_checkout/app.py) exposes integer-unit `POST /checkout` and `GET /health`. Omitted/null discounts deliberately produce HTTP 500. Existing discounts and request validation work. Keep the canonical fixture broken; repairs belong in fresh copies.

Create an isolated environment from the source root:

```sh
python -m venv .workspaces/fastapi-env
.workspaces/fastapi-env/Scripts/python.exe -m pip install -r evaluations/fixtures/fastapi_checkout/requirements.txt
.workspaces/fastapi-env/Scripts/python.exe -B -m unittest discover -s tests -p test_fastapi_fixture.py -v
```

Windows commands are shown; on Linux/macOS use the environment's `bin/python`. Those platforms are not exercised. Installing dependencies requires package-index access; the checks themselves use no network server. The requirements snapshot records the tested environment, not a cross-platform lockfile or security audit.

The harness copies the fixture, observes two expected HTTP failures, rejects a candidate that ignores every discount, applies a supplied reference candidate only to that copy, reruns five HTTP tests and checks byte preservation of tests/user note. It does not invoke an agent. Without FastAPI/httpx, its optional project test is visibly skipped. Run it explicitly in the environment above before claiming HTTP coverage.

Testing follows [official FastAPI TestClient guidance](https://fastapi.tiangolo.com/tutorial/testing/). These are in-process ASGI requests. No live listener, authentication, database, deployment or production workload is covered. Use the [task](../evaluations/tasks/fastapi-checkout.md) and [rubric](../evaluations/rubrics/fastapi-checkout.md) for future independent agent checks.
