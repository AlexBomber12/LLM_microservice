import httpx
import pytest

pytestmark = pytest.mark.integration


def test_health(llm_base_url: str) -> None:
    r = httpx.get(f"{llm_base_url}/health")
    assert r.status_code == 200


def test_chat_completion(llm_base_url: str) -> None:
    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
    }
    r = httpx.post(f"{llm_base_url}/v1/chat/completions", json=payload)
    assert r.status_code == 200
