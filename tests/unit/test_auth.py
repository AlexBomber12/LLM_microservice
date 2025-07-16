import importlib

import pytest
from fastapi import Depends, FastAPI
from starlette.testclient import TestClient


@pytest.fixture
def app_with_auth(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "secret")
    module = importlib.reload(importlib.import_module("llm_microservice.server.main"))
    test_app = FastAPI()

    @test_app.get("/")
    async def root(_: None = Depends(module.verify_auth)):
        return {"ok": True}

    return TestClient(test_app)


def test_auth_required(app_with_auth):
    client = app_with_auth
    resp = client.get("/")
    assert resp.status_code == 401
    resp = client.get("/", headers={"Authorization": "Bearer secret"})
    assert resp.status_code == 200
