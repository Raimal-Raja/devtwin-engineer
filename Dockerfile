ARG PYTHON_IMAGE=python:3.12-slim
ARG DOCKER_CLI_IMAGE=docker:cli
FROM ${DOCKER_CLI_IMAGE} AS docker-cli
FROM ${PYTHON_IMAGE} AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/ backend/
COPY references/ references/
ENTRYPOINT ["python", "-B", "-m", "backend.server"]

FROM base AS app
USER 65532:65532
EXPOSE 8765
CMD ["--listen", "0.0.0.0", "--port", "8765"]

FROM base AS worker
COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
USER 0:0
EXPOSE 8766
CMD ["--worker", "--listen", "0.0.0.0", "--port", "8766"]
