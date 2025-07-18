from __future__ import annotations

import json
import logging
import os
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar, cast
import time
from datetime import datetime
from typing import Any, AsyncGenerator, Dict

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse, Response

from ..sdk.models import (
    ChatMessage,
    CompletionRequest,
    CompletionResponse,
    CompletionChoice,
    UsageInfo,
)
from ..utils import count_message_tokens, count_tokens

try:
    from vllm import LLM, SamplingParams
except Exception:  # pragma: no cover - optional dependency
    LLM = None
    SamplingParams = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct")
GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.85"))
API_KEY = os.getenv("LLM_API_KEY")
# optional quantization method, e.g. "awq" or "gptq"
QUANTIZATION = os.getenv("QUANTIZATION")

app = FastAPI()


async def verify_auth(request: Request) -> None:
    if API_KEY:
        auth = request.headers.get("authorization")
        if auth != f"Bearer {API_KEY}":
            raise HTTPException(status_code=401, detail="Unauthorized")


AUTH_DEP = Depends(verify_auth)

P = ParamSpec("P")
R = TypeVar("R")


def _log(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Typed async logging decorator."""

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("CALL %s args=%s kwargs=%s", func.__qualname__, args, kwargs)
        result: R = await func(*args, **kwargs)
        logger.info("RET  %s → %s", func.__qualname__, result)
        return result

    return wrapper


def log_middleware(app: FastAPI) -> None:
    async def _log(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.time()
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000
        data = {
            "ts": datetime.utcnow().isoformat(),
            "route": request.url.path,
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": getattr(request.state, "prompt_tokens", 0),
            "completion_tokens": getattr(request.state, "completion_tokens", 0),
            "model": getattr(request.state, "model_name", MODEL_NAME),
        }
        logger.info(json.dumps(data))
        return response

    app.middleware("http")(_log)


log_middleware(app)


class LLMEngine:
    def __init__(self) -> None:
        if LLM is None:
            raise RuntimeError("vLLM is not installed")
        kwargs = {
            "model": MODEL_NAME,
            "gpu_memory_utilization": GPU_MEMORY_UTILIZATION,
            "max_model_len": 16384,
        }
        if QUANTIZATION:
            kwargs["quantization"] = QUANTIZATION
        self.llm = LLM(**kwargs)

    def generate(self, prompt: str, params: SamplingParams) -> Any:
        return self.llm.generate([prompt], params)[0]


def get_engine() -> LLMEngine:
    if not hasattr(app.state, "engine"):
        app.state.engine = LLMEngine()
    return cast(LLMEngine, app.state.engine)


ENGINE_DEP = Depends(get_engine)


async def health() -> Dict[str, str]:
    return {"status": "ok"}


app.get("/health", response_model=Dict[str, str])(_log(health))


async def _run_completion(
    req: CompletionRequest,
    engine: LLMEngine,
) -> CompletionResponse:
    prompt = req.prompt or "".join(m.content for m in req.messages or [])
    sampling = SamplingParams(
        n=1,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
        repetition_penalty=req.repetition_penalty,
        presence_penalty=req.presence_penalty,
        frequency_penalty=req.frequency_penalty,
        stop=req.stop,
        seed=req.seed,
    )
    result = engine.generate(prompt, sampling)
    text = result.outputs[0].text
    prompt_tokens = count_tokens(prompt)
    completion_tokens = count_tokens(text)
    choice = CompletionChoice(
        index=0, message=ChatMessage(role="assistant", content=text)
    )
    return CompletionResponse(
        id="cmpl-1",
        object="chat.completion",
        created=int(time.time()),
        model=req.model,
        choices=[choice],
        usage=UsageInfo(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


async def completion_endpoint(
    req: CompletionRequest, engine: LLMEngine
) -> CompletionResponse:
    resp = await _run_completion(req, engine)
    return resp


async def completion_stream(
    req: CompletionRequest, engine: LLMEngine
) -> AsyncGenerator[bytes, None]:
    resp = await _run_completion(req, engine)
    data = resp.model_dump()
    yield json.dumps({"choices": data["choices"], "model": data["model"]}).encode()


async def chat_completions(
    req: CompletionRequest,
    request: Request,
    engine: LLMEngine = ENGINE_DEP,
    _: None = AUTH_DEP,
) -> Any:
    request.state.model_name = req.model
    request.state.prompt_tokens = count_message_tokens(req.messages or [])
    if req.stream:
        return StreamingResponse(
            completion_stream(req, engine), media_type="text/event-stream"
        )
    resp = await completion_endpoint(req, engine)
    request.state.completion_tokens = resp.usage.completion_tokens
    return JSONResponse(resp.model_dump())


app.post("/v1/chat/completions")(_log(chat_completions))


async def completions(
    req: CompletionRequest,
    request: Request,
    engine: LLMEngine = ENGINE_DEP,
    _: None = AUTH_DEP,
) -> Any:
    request.state.model_name = req.model
    request.state.prompt_tokens = count_tokens(req.prompt or "")
    if req.stream:
        return StreamingResponse(
            completion_stream(req, engine), media_type="text/event-stream"
        )
    resp = await completion_endpoint(req, engine)
    request.state.completion_tokens = resp.usage.completion_tokens
    return JSONResponse(resp.model_dump())


app.post("/v1/completions")(_log(completions))


def create_app() -> FastAPI:
    return app


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
