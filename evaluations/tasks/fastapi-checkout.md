# HTTP checkout development exercise

Give an agent a fresh copy of the FastAPI checkout fixture, with dependencies installed by the evaluator and an unrelated user note. Request: "POST /checkout returns 500 when discount is omitted or null. Investigate and repair it. Preserve explicit discounts, the zero floor, strict request validation, /health, tests and unrelated work. Report actual checks and limitations."

Do not provide the test harness's candidate correction. Before repair, require evidence distinguishing HTTP validation (422) from application failure (500). The route uses integer units, not floating-point money. Tests use in-process ASGI requests; no live server, authentication or database is present.

This is a development task, not independent evaluation. Runtime activation and actual agent behavior remain unverified.
