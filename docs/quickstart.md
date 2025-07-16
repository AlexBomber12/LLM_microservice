# Quickstart

## Run with GPU
```bash
docker compose up -d
```

## Run without GPU (mock)
```bash
USE_MOCK_LLM=1 pytest -k integration
```
