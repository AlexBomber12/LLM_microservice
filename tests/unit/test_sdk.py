from llm_microservice.sdk.models import (
    ChatMessage,
    CompletionRequest,
    CompletionResponse,
    CompletionChoice,
    UsageInfo,
)


def test_serialization_roundtrip():
    req = CompletionRequest(
        model="test", messages=[ChatMessage(role="user", content="hi")]
    )
    data = req.model_dump()
    new_req = CompletionRequest.model_validate(data)
    assert new_req == req

    resp = CompletionResponse(
        id="1",
        object="chat.completion",
        created=0,
        model="test",
        choices=[
            CompletionChoice(
                index=0, message=ChatMessage(role="assistant", content="ok")
            )
        ],
        usage=UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2),
    )
    data = resp.model_dump()
    new_resp = CompletionResponse.model_validate(data)
    assert new_resp == resp
