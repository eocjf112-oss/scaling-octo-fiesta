from __future__ import annotations

from typing import Any

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse, ProviderError


class ClaudeProvider:
    name = "claude"

    def __init__(self, config: JarvisConfig):
        self._config = config

    def is_available(self) -> bool:
        return bool(self._config.anthropic_api_key)

    def complete(self, request: ChatRequest) -> ChatResponse:
        if not self.is_available():
            return ChatResponse(
                provider=self.name,
                content=(
                    "Claude Provider는 현재 비활성화되어 있습니다. "
                    ".env의 ANTHROPIC_API_KEY를 비워 둔 상태이므로 실제 API 호출을 하지 않았습니다. "
                    "나중에 키를 입력하면 같은 구조에서 바로 사용할 수 있습니다."
                ),
                metadata={"missing_api_key": "ANTHROPIC_API_KEY"},
            )

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ProviderError("Install the Anthropic SDK with: pip install -e '.[ai]'") from exc

        client = Anthropic(api_key=self._config.anthropic_api_key)
        kwargs: dict[str, Any] = {
            "model": self._config.anthropic_model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        if request.system_prompt:
            kwargs["system"] = request.system_prompt
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature

        response = client.messages.create(**kwargs)
        content = "\n".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        return ChatResponse(
            provider=self.name,
            content=content,
            metadata={"model": self._config.anthropic_model},
        )
