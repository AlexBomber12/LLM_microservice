from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    model: str
    prompt: Optional[str] = None
    messages: Optional[List[ChatMessage]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    repetition_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logprobs: Optional[int] = None
    stop: Optional[List[str] | str] = None
    seed: Optional[int] = None
    stream: bool = False


class CompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: UsageInfo


class LogProbResult(BaseModel):
    token: str
    logprob: float
    top_logprobs: Optional[List[dict[str, Any]]] = None
