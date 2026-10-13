# Free-tier provider integrations

Checked official resources on 2026-10-13. Added explicit Groq and Gemini adapters to the existing NVIDIA backend. These are API integrations, not newly created accounts or unlimited free compute. Public execution remains unfinished.

The user's discovery sources were consulted: [public-apis](https://github.com/public-apis/public-apis), [Free APIs browse](https://free-apis.github.io/#/browse), [free-llm-api topics](https://github.com/topics/free-llm-api) and [public-api-lists](https://github.com/public-api-lists/public-api-lists). The browse page requires JavaScript; its contents were not available in the text fetch. Directory entries are leads, not a guarantee of price, terms or availability. Provider decisions above use official documentation. General-purpose directory APIs do not supply a repository execution sandbox.

| Provider | Fixed model | Backend environment | Limits and data considerations |
| --- | --- | --- | --- |
| Groq | `openai/gpt-oss-120b` | `DEVTWIN_PROVIDER=groq`, `GROQ_API_KEY` | Free Plan quotas apply. Do not upgrade to Developer billing for the no-cost setup. |
| Google Gemini | `gemini-3.8-flash` | `DEVTWIN_PROVIDER=gemini`, `GEMINI_API_KEY` | Selected model has unpaid input/output quotas. Use a project without paid billing; no confidential/personal inputs on unpaid services. |
| NVIDIA | `nvidia/nemotron-3-ultra-550b-a55b` | `DEVTWIN_PROVIDER=nvidia`, `NVIDIA_API_KEY` | Existing internal trial integration; not the public production provider. |

The default remains NVIDIA for compatibility. Set `DEVTWIN_PROVIDER` before starting the backend to choose a free-tier alternative. Keys stay in the server environment, never source control or browser assets. No account creation, terms acceptance, billing upgrades or provider-key storage was performed. The application cannot determine the billing tier from a key: model allowlisting and token limits are not a guarantee against charges if an operator supplies a paid account. Configure and confirm a Free Plan/unpaid project at the provider first.

Groq's [Free Plan policy](https://community.groq.com/t/do-i-get-charged-for-anything-on-the-groq-free-plan/832) states excess usage returns rate-limit errors instead of charges. Its [limits](https://console.groq.com/docs/rate-limits) are model/organization-specific; actual account limits may differ. [Data controls](https://console.groq.com/docs/your-data) describe retention exceptions and account settings. Groq is the first candidate for this engineering workspace; account/model access and service suitability still need live validation.

Gemini's [pricing](https://ai.google.dev/gemini-api/docs/pricing) lists free input/output for the selected Flash model. Its [unpaid-service terms](https://ai.google.dev/gemini-api/terms) say inputs/outputs may support product improvement and human review; do not submit sensitive, confidential or personal information. Geographic exceptions and usage requirements also apply. Use approved nonconfidential examples until the intended public service has been reviewed against the current terms.

The shared provider client uses fixed HTTPS endpoints, environment-only credentials, no redirects, bounded requests/responses and no automatic retry/fallback. Quota exhaustion stops the request; it never silently switches providers or purchases credits. Gemini uses a credential header rather than a URL query key and excludes thought parts. Both providers normalize final responses to the existing investigation schema. The browser preview displays the server-selected provider/model and notice before consent. Submission must name that provider, so a stale/different provider is rejected.

After configuring one provider in the backend environment, run a bounded synthetic test:

```powershell
python -m backend.providers --smoke
python -m backend.server --port 8765
```

The local server additionally requires `DEVTWIN_SESSION_TOKEN`; see [local workspace setup](local-workspace.md). The smoke sends only a fixed development prompt. Neither Groq nor Gemini credentials were configured during this increment, so their live account checks remain pending. Automated adapter tests use simulated responses.

OpenRouter was evaluated but not added: free routing can select different model providers, and low quotas plus provider-specific data policies add complexity. The first implementation favors direct providers with explicit destinations. Additional providers can follow once these are live-tested.
