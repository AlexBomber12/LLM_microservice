# Quickstart

## Run with GPU
```bash
cp .env.example .env && docker compose up -d --build
```

## Run without GPU (mock)
```bash
USE_MOCK_LLM=1 pytest -k integration
```
