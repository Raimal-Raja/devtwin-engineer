# OpenRouter Free setup and testing

The backend supports `DEVTWIN_PROVIDER=openrouter` with `OPENROUTER_API_KEY` in the app environment. Only `openrouter/free` and `nvidia/nemotron-3-ultra-550b-a55b:free` are allowlisted; the browser cannot select a paid model or alter routing controls. Set `DEVTWIN_OPENROUTER_MODEL` explicitly to choose between them. The app requests maximum prompt/completion/per-request prices of zero, required parameter support and disabled upstream fallback. Data collection is denied by default; the operator-approved public/synthetic mode is explained below. No paid plugins or fallback model list are sent. Client requests do not retry or switch to another service.

The public OpenRouter catalog was checked on 2026-10-14: the unsuffixed Nemotron Ultra ID has paid prompt/completion prices, while its `:free` variant has zero prices. The free variant does not advertise `response_format`, so that variant receives JSON instructions without an unsupported JSON-mode parameter. Strict schema and citation validation still apply. Reasoning is disabled for its bounded development requests. Reports distinguish requested and actual returned model IDs.

OpenRouter's [Free Models Router](https://openrouter.ai/docs/guides/routing/routers/free-router) selects an available free model, including filtering for requested features. Each report records the actual model returned by OpenRouter. The consent notice covers forwarding to an upstream model/provider; submit only nonconfidential synthetic or public source. [Provider data policy](https://openrouter.ai/docs/guides/privacy/provider-logging) and [routing controls](https://openrouter.ai/docs/guides/routing/provider-selection) still need review for the intended service. Privacy/parameter filters can leave no eligible free route; an error then stops the request.

## Local setup

Create a key yourself at [OpenRouter keys](https://openrouter.ai/settings/keys). Do not buy credits or enable billing for this project. No key is supplied with the app and the NVIDIA key cannot authenticate to OpenRouter.

From the project directory in your terminal:

```powershell
python scripts/start_openrouter.py
```

The helper uses an existing `OPENROUTER_API_KEY` or asks for it with a hidden prompt. It defaults to the free Nemotron Ultra variant unless another allowlisted selection is already configured. It sends one bounded synthetic smoke request and starts the localhost Docker app only if that succeeds. It does not write the key to a file. It removes unrelated provider keys from the Compose process environment. Docker still holds the selected key in the app container environment; do not share container environments or resolved Compose configuration. The private verification worker receives no model key.

The default denies upstream data collection. A live 404 diagnostic confirmed that this filter excludes the free Nemotron endpoint. The user approved providers that may store/train on **public or synthetic inputs only**. To select that policy explicitly:

```powershell
python scripts/start_openrouter.py --allow-public-inputs
```

This sets `DEVTWIN_OPENROUTER_DATA_POLICY=allow`. The preview discloses possible upstream storage/training and requires public/synthetic confirmation; the API enforces that confirmation before any model call. Keep confidential/private inputs out of this mode. Omit the flag and leave the environment policy unset to retain denial.

Visit http://127.0.0.1:8765. Enter the workspace session token from `.env.docker`, never the OpenRouter key. Preview selected files and confirm the provider says **OpenRouter Free**. Approve provider submission and, separately, the bounded repair loop. Review the reports, actual model, test evidence and complete replacement before exporting a candidate.

If you configure the key in your own environment instead:

```powershell
$env:DEVTWIN_PROVIDER = 'openrouter'
$env:DEVTWIN_OPENROUTER_MODEL = 'nvidia/nemotron-3-ultra-550b-a55b:free'
$env:OPENROUTER_API_KEY = Read-Host -MaskInput 'OpenRouter API key'
python -m backend.providers --smoke
python scripts/evaluate_web_workflows.py --approve-provider --output .workspaces/openrouter-workflows.json
```

The workflow command makes at most thirteen synthetic source-analysis calls and stops at the first provider or validation error. Preserve existing output files. Passing schema and citation bounds is development evidence, not a semantic or production certificate. The repair loop reserves at most three calls per run; provider quotas may be smaller than the app budget. See [current API limits](https://openrouter.ai/docs/api/reference/limits) for account-specific ceilings. A 401, 402, 429 or 503 stops work; the app does not purchase credits to recover.

## Readiness

Offline tests cover fixed free routing, zero-price controls, required JSON parameters, actual-model reporting, key redaction, missing credentials, nonzero reported cost, incomplete answers, and error/quota termination. With the operator-approved public/synthetic policy, all thirteen synthetic workflow analyses passed schema/citation validation and the Dockerized repair loop passed its five candidate tests. This is local development evidence; public backend hosting and hosted job security validation remain separate.
