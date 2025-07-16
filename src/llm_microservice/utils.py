from __future__ import annotations

from typing import Any, Iterable


def count_tokens(text: str) -> int:
    """Naively count tokens using whitespace split."""
    return len(text.split())


def count_message_tokens(messages: Iterable[Any]) -> int:
    contents = []
    for m in messages:
        if isinstance(m, dict):
            contents.append(m.get("content", ""))
        else:
            contents.append(getattr(m, "content", ""))
    return sum(count_tokens(c) for c in contents)
