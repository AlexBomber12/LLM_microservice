from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx

from .models import CompletionRequest, CompletionResponse


def _build_headers(api_key: Optional[str]) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


class AsyncLLMClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=2.0, read=30.0),
            headers=_build_headers(api_key),
        )

    async def _post(self, path: str, data: Dict[str, Any]) -> httpx.Response:
        for _ in range(3):
            try:
                return await self._client.post(f"{self._base_url}{path}", json=data)
            except httpx.HTTPError:
                await asyncio.sleep(0.5)
        raise httpx.HTTPError("Failed after retries")

    async def chat_completions(self, req: CompletionRequest) -> CompletionResponse:
        resp = await self._post("/v1/chat/completions", req.model_dump())
        resp.raise_for_status()
        return CompletionResponse.model_validate(resp.json())

    async def completions(self, req: CompletionRequest) -> CompletionResponse:
        resp = await self._post("/v1/completions", req.model_dump())
        resp.raise_for_status()
        return CompletionResponse.model_validate(resp.json())

    async def aclose(self) -> None:
        await self._client.aclose()


class LLMClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        self._async = AsyncLLMClient(base_url, api_key)

    def chat_completions(self, req: CompletionRequest) -> CompletionResponse:
        return asyncio.run(self._async.chat_completions(req))

    def completions(self, req: CompletionRequest) -> CompletionResponse:
        return asyncio.run(self._async.completions(req))

    def close(self) -> None:
        asyncio.run(self._async.aclose())
