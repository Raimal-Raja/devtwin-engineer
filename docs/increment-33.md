# Increment 33 — Fresh local acceptance run

Checked on 2026-10-15. Docker Desktop was initially stopped. It was launched, and the existing app/worker configuration was preserved while both services were rebuilt and started. Both reported healthy. No keys were printed or committed.

The full project gate passed: 148 Python cases (146 passed, two Windows symlink skips), 13 web tests, package validation, 13 capability-resource checks and archive integrity.

Fresh real HTTP checks passed for static modules, public GitHub default-branch browse and commit-pinned selected import, ZIP preview, 13 workflow availability, authentication/selection rejection, provider consent rejection, free OpenRouter investigation, patch proposal, approval-gated selected ZIP export and test preservation. Manual Docker verification reproduced the synthetic checkout baseline failure and passed five candidate tests. Source fixture files were not modified.

The combined bounded repair acceptance assertion failed; that first harness did not preserve the returned repair object, so its exact outcome is unknown. A diagnostic request was rejected by the shared model-call rate limit. After the allowance reset, one final diagnostic returned an OpenRouter upstream generation error. No paid fallback or automatic transport retry occurred. Fresh live repair acceptance is therefore not established by this run; earlier repair regression evidence remains separate.

Chrome successfully navigated to `http://127.0.0.1:8765/`; its accessibility tree and screenshot showed the local workspace. An offscreen control action encountered unavailable coordinate geometry; after state refresh, complete click-through acceptance was still not established. Do not equate navigation and rendering with a full browser workflow pass. Existing browser extensions also injected unrelated overlay content; their claims are not DevTwin output.

Claude execution remains deferred. Capability-resource checks do not certify semantic correctness of all 13 workflows. The local services are ready for hands-on use, while free-provider availability, full browser acceptance and broader runtime coverage remain explicit limits.
