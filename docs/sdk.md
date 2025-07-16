# SDK Usage

```python
from llm_microservice.sdk import LLMClient, CompletionRequest, ChatMessage

client = LLMClient(base_url="http://localhost:8000")
req = CompletionRequest(model="meta-llama/Meta-Llama-3-8B-Instruct", messages=[ChatMessage(role="user", content="Hi")])
resp = client.chat_completions(req)
print(resp.choices[0].message.content)
```
