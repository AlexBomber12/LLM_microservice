import os
import shutil
import subprocess
import time

import httpx
import pytest

pytestmark = pytest.mark.integration

DOCKER_AVAILABLE = shutil.which("docker") is not None


@pytest.fixture(scope="session")
def llm_base_url() -> str:
    if not DOCKER_AVAILABLE:
        pytest.skip("docker not available")
    if os.getenv("USE_MOCK_LLM") == "1":
        url = "http://localhost:5001"
        container = subprocess.Popen(
            ["docker", "run", "--rm", "-p", "5001:80", "lambdatest/openai-mock:latest"]
        )
        time.sleep(5)
        yield url
        container.terminate()
        container.wait()
    else:
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        url = "http://localhost:8000"
        for _ in range(30):
            try:
                r = httpx.get(f"{url}/health")
                if r.status_code == 200:
                    break
            except Exception:
                time.sleep(1)
        yield url
        subprocess.run(["docker", "compose", "down"], check=True)


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
