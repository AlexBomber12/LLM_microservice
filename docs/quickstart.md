# Quickstart

## Run with GPU
```bash
cp .env.example .env            # edit LLM_TAG when upgrading
docker compose pull llm-microservice
docker compose up -d --force-recreate
```

## Run without GPU (mock)
```bash
USE_MOCK_LLM=1 pytest -k integration
```
