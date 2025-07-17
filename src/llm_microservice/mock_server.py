"""
Minimal OpenAI-compatible stub used ONLY for integration-mock tests.
Run with ``python -m llm_microservice.mock_server`` or uvicorn.

Routes:
  GET  /health                       → {"status":"ok"}
  POST /v1/chat/completions          → {"id": "...", "choices": [...]}
  POST /v1/completions               → {"id": "...", "choices": [...]}
"""

import time
import uuid
from typing import Any, Dict, List

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()

COMPLETION_BODY = Body(...)


def health() -> Dict[str, str]:  # pragma: no cover
    return {"status": "ok"}


app.get("/health")(health)


class Message(BaseModel):  # echo schema
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: int


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int


def _response(content: str) -> Dict[str, Any]:
    return {
        "id": f"cmpl-{uuid.uuid4().hex}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": "mock",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}}],
    }


def chat_completions(req: ChatRequest) -> Dict[str, Any]:  # pragma: no cover
    return _response("pong")


app.post("/v1/chat/completions")(chat_completions)


def completions(
    req: CompletionRequest = COMPLETION_BODY,
) -> Dict[str, Any]:  # pragma: no cover
    return _response("pong")


app.post("/v1/completions")(completions)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
