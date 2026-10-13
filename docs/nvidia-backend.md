# NVIDIA development integration

This is the first backend increment toward the requested standalone web agent. It adds a real NVIDIA HTTP client and a fixed synthetic smoke command. It does not yet connect the public dashboard to inference, run repository tools or provide a hosted execution sandbox.

The supplied key was exposed in conversation. Revoke it and configure a replacement as `NVIDIA_API_KEY` in the server process environment. Do not commit credentials, pass them in command-line arguments, paste them in chat or put them in static JavaScript. This implementation does not load `.env` automatically.

From the repository root, after configuring the environment:

```powershell
python -m backend.nvidia --smoke
```

The command sends one fixed synthetic development prompt to the NVIDIA endpoint and prints the final answer or a redacted failure. No repository files are submitted. The client uses the requested `nvidia/nemotron-3-ultra-550b-a55b` model, non-streamed responses and thinking disabled by default. Requests have a bounded prompt, response size, timeout and output token allowance. It refuses redirects and does not retry, switch providers, enable billing or execute generated code. Unfinished answers fail explicitly. These bounds reduce usage; they do not establish the account's billing tier or available credits.

Tests simulate success, invalid configuration, unfinished/malformed responses, quota/auth/network errors, response limits, secret reflection and redirect rejection. Live account/model availability is a separate gate; simulated responses do not prove inference works.

NVIDIA's [model reference](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-ultra-550b-a55b) identifies this endpoint/model and its governing trial terms. The [API trial terms](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf) restrict hosted trial use to internal evaluation and exclude confidential inputs. Keep this adapter for synthetic internal development; do not attach the trial key to the public production dashboard.

Next increments need a provider allowed for the intended public service, authenticated request routing with abuse/usage limits, selected project ingestion, an evidence-based agent loop, patch review and isolated execution. A public endpoint must never expose the provider secret or offer unrestricted shell access.
