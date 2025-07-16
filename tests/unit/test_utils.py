from llm_microservice.utils import count_tokens, count_message_tokens


def test_count_tokens():
    assert count_tokens("hello world") == 2


def test_count_message_tokens():
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "world"},
    ]
    assert count_message_tokens(messages) == 2
