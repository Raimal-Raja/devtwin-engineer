# No-cost hosting prerequisites

Checked official documentation on 2026-10-14. The user selected hosted deployment only if free and currently has no free Linux cloud account. The local Docker app and worker work; a full public backend is not deployed.

## Compute

[Oracle Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) include VM options suitable for evaluating a small authenticated deployment. The current documentation lists two AMD micro instances or an Arm allowance equivalent to 2 OCPUs and 12 GB for an Always Free tenancy. Availability depends on the home region; idle instances may be reclaimed. [Signup](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm) generally requires phone and credit-card verification. The operator must create the account, accept its terms and provision only resources marked Always Free; do not upgrade to paid billing or rely on temporary trial credits. No cloud account or VM has been created by this project.

[Hugging Face Spaces](https://huggingface.co/docs/hub/en/spaces-overview) offers free CPU hosting that sleeps when idle. Hosting a Docker image is not evidence that the privileged Docker worker/job strategy is supported; nested job execution must not be assumed. A static site or sleeping source-analysis demo does not complete the isolated engineering service.

## Inference

The existing NVIDIA key remains for internal evaluation. [NVIDIA trial terms](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf) exclude production use. Do not use it for public visitor jobs.

[Groq](https://console.groq.com/docs/rate-limits) lists a Free plan for the configured model, but account access must be confirmed. If account setup requires payment, leave it unconfigured. Groq and xAI's Grok are different services.

[Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) currently lists free input/output for the configured `gemini-3.8-flash`. Use an unpaid project and review current [terms](https://ai.google.dev/gemini-api/terms); unpaid inputs may be used for improvement and must not contain confidential or personal information. Account/location availability and actual quotas require live verification.

## Deployment gates

OpenRouter Free is now integrated and live-tested with an authenticated operator key; see [setup](openrouter.md). The unsuffixed Nemotron Ultra model is paid, so only its `:free` variant and the general free router are allowed. Initial routing/availability failures are preserved in the increment evidence. After approval of public/synthetic-only upstream storage/training, thirteen source analyses and the Docker repair loop passed. Hosted-service validation remains a separate gate.

After the operator supplies a confirmed free VM and a securely configured compatible provider, validate transport authentication, HTTPS, bounded user access and job usage, architecture-compatible pinned images, worker isolation, cleanup and credential boundaries. The current Compose configuration is for dedicated local development and must not be exposed unchanged as a public multi-user service. Do not publish a tunnel to this computer to bypass those requirements.

Provider quotas stop jobs; the application does not buy credits or switch services. Free allowances can change, and the code cannot determine billing status from an API key. Keep licensing undecided and the repository private until the user makes the release decision.
