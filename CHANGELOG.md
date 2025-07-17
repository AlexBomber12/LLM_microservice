# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.0] - YYYY-MM-DD
- Added: stand-alone FastAPI + vLLM micro-service for Meta Llama-3-8B-Instruct.
- Added: Python SDK (`llm_microservice.sdk`), async & sync.
- Added: Dockerfile (CUDA 12.4) and `docker-compose.yaml` with GPU override.
- Added: MkDocs site (`docs/**`) and ADR directory.
- **Breaking**: All consumer apps must set `LLM_BASE_URL`; local LLM path removed.
- Migration: step-by-step guide (env vars, SDK install, old API removal).
- CI: new jobs `integration-mock` & `integration-real`; skip logic via `USE_REAL_LLM`.
