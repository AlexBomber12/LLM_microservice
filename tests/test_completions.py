import importlib
from typing import Any

import pytest
from fastapi.testclient import TestClient


class StubEngine:
    def __init__(self) -> None:
        pass

    def generate(self, prompt: str, params: Any) -> Any:
        class _Result:
            outputs = [type("O", (), {"text": "pong"})()]

        return _Result()


class DummySamplingParams:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    module = importlib.reload(importlib.import_module("llm_microservice.server.main"))

    # replace LLMEngine with stub to avoid real dependency
    monkeypatch.setattr(module, "LLMEngine", StubEngine)
    monkeypatch.setattr(module, "SamplingParams", DummySamplingParams)
    module.app.state._state.clear()
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    return TestClient(module.app)


BASE_PAYLOAD = {
    "model": "test",
    "prompt": "hello",
    "max_tokens": 1,
    "temperature": 0.9,
    "top_p": 0.9,
    "top_k": 10,
    "repetition_penalty": 1.0,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
    "logprobs": 1,
}

PARAMS = [
    "temperature",
    "top_p",
    "top_k",
    "repetition_penalty",
    "presence_penalty",
    "frequency_penalty",
    "logprobs",
]


def _post(client: TestClient, payload: dict) -> None:
    resp = client.post("/v1/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "choices" in data


def test_completions_all_fields(client: TestClient) -> None:
    _post(client, BASE_PAYLOAD)


@pytest.mark.parametrize("param", PARAMS)
def test_completions_missing_field(client: TestClient, param: str) -> None:
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != param}
    _post(client, payload)


@pytest.mark.parametrize("param", PARAMS)
def test_completions_null_field(client: TestClient, param: str) -> None:
    payload = BASE_PAYLOAD.copy()
    payload[param] = None
    _post(client, payload)
