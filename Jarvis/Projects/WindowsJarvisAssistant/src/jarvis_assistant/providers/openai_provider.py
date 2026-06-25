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
            return ChatResponse(
                provider=self.name,
                content=(
                    "ChatGPT Provider는 현재 비활성화되어 있습니다. "
                    ".env의 OPENAI_API_KEY를 비워 둔 상태이므로 실제 API 호출을 하지 않았습니다. "
                    "나중에 키를 입력하면 같은 구조에서 바로 사용할 수 있습니다."
                ),
                metadata={"missing_api_key": "OPENAI_API_KEY"},
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderError("Install the OpenAI SDK with: pip install -e '.[ai]'") from exc

        client = OpenAI(api_key=self._config.openai_api_key)
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        kwargs = {
            "model": self._config.openai_model,
            "messages": messages,
        }
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature

        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        return ChatResponse(
            provider=self.name,
            content=content,
            metadata={"model": self._config.openai_model},
        )
