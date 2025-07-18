# LLM Microservice 2.0.0

## Project Overview

This project packages an OpenAI compatible LLM server built with **vLLM** and **FastAPI**. It exposes `/v1/completions` and `/v1/chat/completions` endpoints that accept the standard OpenAI API schema. Models such as **Llama‑3.1‑8B‑Instruct** can be loaded and served on a GPU. Typical use cases include local inference, model fine‑tuning validation, or acting as a drop‑in replacement for the OpenAI API in development environments.

## Getting the Code

```bash
git clone https://github.com/<user>/LLM_microservice.git
cd LLM_microservice
```

To fetch the release tag and check out version **v2.0.0**:

```bash
git fetch --tags
git checkout tags/v2.0.0 -b v2.0.0
```

Cloning retrieves the source code, `docker-compose.yaml`, `.env.example`, and this README. If the directory already exists, update it instead of cloning again:

```bash
git pull
```

A git repository contains only the project files. Docker images for the microservice are downloaded separately when you run `docker compose pull`.

## Quick Start

### Prerequisites

- **Docker** and **docker-compose** installed
- A machine with an NVIDIA GPU and up‑to‑date drivers
- Optional: a HuggingFace access token if the model requires gated access

### Configuration

1. Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Key variables in `.env`:

- `LLM_TAG=v2.0.0` – container image tag
- `MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct`
- `GPU_MEMORY_UTILIZATION=0.85` – fraction of GPU memory to allocate
- `HF_HOME=/models/.cache` – where models are cached on the host
- `HF_TOKEN=` – your HuggingFace token (if required)
- `QUANTIZATION=` – optional, e.g. `awq` or `gptq`
- `LLM_API_KEY=` – set to require bearer auth

2. Adjust `docker-compose.yaml` if necessary and ensure the `llm-microservice` service references the variables above.

### Launch Steps

```bash
# Pull the Docker image
docker compose pull

# Start the service in the background
docker compose up -d

# Verify the container is running
docker compose ps
curl http://localhost:8000/health
```

Test a request using `curl`:

```bash
curl -X POST http://localhost:8000/v1/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"meta-llama/Meta-Llama-3-8B-Instruct","prompt":"Hello","max_tokens":1}'
```

Or with Python:

```python
from llm_microservice.sdk import LLMClient, CompletionRequest

client = LLMClient(base_url="http://localhost:8000")
req = CompletionRequest(model="meta-llama/Meta-Llama-3-8B-Instruct", prompt="Hello", max_tokens=1)
print(client.completions(req).choices[0].message.content)
```

## Configuration Reference

Environment variables consumed by the service:

| Variable | Description |
|----------|-------------|
| `MODEL_NAME` | Name or path of the model to load |
| `HF_TOKEN` | HuggingFace token for gated models |
| `GPU_MEMORY_UTILIZATION` | Fraction of GPU memory to allocate (0–1) |
| `HF_HOME` | Cache directory mounted from the host |
| `QUANTIZATION` | `awq`, `gptq`, or leave empty for full precision |
| `LLM_API_KEY` | If set, API requests must include `Authorization: Bearer <key>` |

Change values in `.env` and re‑create the container to switch models or alter parameters.

## Updating and Restarting

```bash
# Pull updated container images
docker compose pull

# Recreate the service using the new image and any .env changes
docker compose up -d --force-recreate
```

If you modify `docker-compose.yaml` or `.env`, rerun `docker compose up -d --force-recreate` for changes to take effect.

## API Usage

### `POST /v1/completions`

- **URL:** `http://localhost:8000/v1/completions`
- **Headers:** `Content-Type: application/json`
- **Body:**

```json
{
  "model": "meta-llama/Meta-Llama-3-8B-Instruct",
  "prompt": "Hello",
  "max_tokens": 1
}
```

- **Response:**

```json
{
  "id": "cmpl-1",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "meta-llama/Meta-Llama-3-8B-Instruct",
  "choices": [
    {"index": 0, "message": {"role": "assistant", "content": "world"}}
  ],
  "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
}
```

The API is compatible with OpenAI clients. Interactive documentation is available at `http://localhost:8000/docs`.

## Troubleshooting

- **Cannot access gated repo** – ensure `HF_TOKEN` is set and that your account has permission to download the model.
- **CUDA out of memory** – free GPU memory, reduce `max_tokens`, or use a quantized model via `QUANTIZATION`.
- **TypeError: '<' not supported between int and NoneType** – always provide numeric parameters or upgrade to the latest stable image.
- **Healthcheck fails** – inspect logs with `docker compose logs -f` to diagnose startup issues.
- **Lint/styling issues in CI** – run `ruff --fix` and `black src tests` locally before committing.

Logs from the FastAPI server can also be viewed via `docker compose logs llm-microservice`.

## Additional Info / Best Practices

- Remove cached models by deleting files under `/opt/llm_models` (host path from the compose file).
- GPUs with at least 16 GB VRAM are recommended for Llama‑3‑8B. Larger models require more memory.
- Tests can be added under `tests/` (for example `tests/test_completions.py`). Run `make test` to execute the unit suite.
- This project is released under the terms of the [MIT License](LICENSE). Contributions are welcome via pull requests.

