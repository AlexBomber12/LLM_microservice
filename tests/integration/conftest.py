import contextlib
import os
import pathlib
import socket
import subprocess
import sys
import time

import pytest

PORT = 5001
BASE = f"http://localhost:{PORT}"


def _is_up() -> bool:
    with socket.socket() as s:
        return s.connect_ex(("localhost", PORT)) == 0


@pytest.fixture(scope="session")
def llm_base_url() -> str:
    if os.getenv("USE_MOCK_LLM") == "1":
        # spawn the stub in a subprocess
        root = pathlib.Path(__file__).parents[2]
        env = {**os.environ, "PYTHONPATH": str(root / "src")}
        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "llm_microservice.mock_server:app",
                "--port",
                str(PORT),
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # wait until port is open
        for _ in range(20):
            if _is_up():
                break
            time.sleep(0.5)
        else:
            proc.kill()
            pytest.skip("mock server failed to start")
        yield BASE
        proc.terminate()
        with contextlib.suppress(Exception):
            proc.wait()
    else:
        # real server / external URL defined elsewhere
        yield os.getenv("LLM_BASE_URL", BASE)
