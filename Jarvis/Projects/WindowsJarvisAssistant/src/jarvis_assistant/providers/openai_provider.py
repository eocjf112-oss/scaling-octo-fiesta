from __future__ import annotations

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse, ProviderError


class ChatGPTProvider:
    name = "chatgpt"

    def __init__(self, config: JarvisConfig):
        self._config = config

    def is_available(self) -> bool:
        return bool(self._config.openai_api_key)

    def complete(self, request: ChatRequest) -> ChatResponse:
        if not self.is_available():
            raise ProviderError("OPENAI_API_KEY is required for ChatGPT provider.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderError("Install the OpenAI SDK with: pip install -e '.[ai]'") from exc

        client = OpenAI(api_key=self._config.openai_api_key)
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        response = client.chat.completions.create(
            model=self._config.openai_model,
            messages=messages,
            temperature=request.temperature,
        )
        content = response.choices[0].message.content or ""
        return ChatResponse(
            provider=self.name,
            content=content,
            metadata={"model": self._config.openai_model},
        )
