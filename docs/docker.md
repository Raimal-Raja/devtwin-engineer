# Dockerized local workspace

Docker Desktop is installed on the development computer and its Linux engine has been exercised. The Compose app is reachable at http://127.0.0.1:8765. This is a local development deployment; the public catalog does not host this backend.

On another computer, install Docker with Linux containers enabled and review its agreement yourself. Preload official images and generate the local configuration:

```powershell
docker pull python:3.12-slim
docker pull docker:cli
python scripts/prepare_docker.py .
docker compose --env-file .env.docker -p devtwin-engineer build
docker compose --env-file .env.docker -p devtwin-engineer up -d --wait
```

Preparation records the actual downloaded repository digests and creates separate random app and worker tokens. It refuses to overwrite `.env.docker`. Keep that ignored file private; on Windows restrict its ACL to your user. Enter its `DEVTWIN_SESSION_TOKEN` value in the browser's workspace-token field. Never enter provider keys there. Provider keys and an optional GitHub token are passed from the operator's process environment to the app; they are not saved by preparation or copied into images. Review your provider's account limits and data terms before submitting source.

Only the app publishes a port, bound to 127.0.0.1. The worker has no published port and accepts only authenticated verification requests. The worker mounts the Docker daemon socket and therefore has substantial authority over that daemon: run this arrangement on a dedicated development engine, never as an audited public multi-user sandbox. The app and project test containers have no daemon socket. Test jobs have no network, host source mounts or provider credentials, and use a pinned preloaded Python image with process, output, time and resource limits.

Select a small Python project and its standard-library unittest files, preview it, request a focused patch, review the replacement, and separately approve execution. Original and candidate tests run in different disposable containers. Existing selected tests are preserved on export. Other languages, dependency installation are not implemented by this runner. The app also supports an explicitly approved bounded repair loop; see [repair loop](repair-loop.md).

```powershell
docker compose --env-file .env.docker -p devtwin-engineer ps
docker compose --env-file .env.docker -p devtwin-engineer stop
docker compose --env-file .env.docker -p devtwin-engineer down
```

Do not print resolved Compose configuration or container environment variables when collecting diagnostics; those contain credentials. Docker installation and local execution do not establish a free public hosting plan.

For free-only OpenRouter inference, use the hidden-key [OpenRouter setup helper](openrouter.md). It selects the provider explicitly and keeps the key out of project files.
