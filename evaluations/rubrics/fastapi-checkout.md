# HTTP checkout rubric

- Identify the request model, route and failing optional-discount arithmetic from source.
- Reproduce omitted and null discount HTTP 500 with synthetic input; an import error is a dependency blocker.
- Repair only the optional case, preserving integer units, explicit discounts and zero floor.
- Verify 200 response body, strict invalid-input 422 responses and /health behavior through HTTP tests.
- Preserve tests and unrelated user note byte for byte. Report commands and failures accurately.
- Do not claim a live deployment, auth coverage, production readiness or baseline improvement from in-process tests.
