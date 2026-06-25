"""
Jarvis AI — OpenAI (ChatGPT) 프로바이더

GPT-4o, GPT-4-turbo 등 OpenAI 모델과 연결합니다.
스트리밍 응답 및 대화 기록 관리를 지원합니다.
"""

from __future__ import annotations

from typing import Generator

from loguru import logger

from .base_provider import BaseProvider, Message, MessageRole, ProviderResponse


class OpenAIProvider(BaseProvider):
    """OpenAI ChatGPT 프로바이더"""

    name = "openai"
    display_name = "ChatGPT (OpenAI)"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str = "",
    ) -> None:
        super().__init__(system_prompt=system_prompt)
        self._api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    def _get_client(self):
        """OpenAI 클라이언트 지연 초기화"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "openai 패키지가 설치되지 않았습니다. "
                    "'pip install openai' 를 실행하세요."
                )
        return self._client

    def is_available(self) -> bool:
        if not self._api_key:
            return False
        try:
            self._get_client()
            return True
        except Exception:
            return False

    def _build_messages(
        self, user_message: str, system_override: str | None = None
    ) -> list[dict]:
        messages = []

        system = system_override or self.system_prompt
        if system:
            messages.append({"role": "system", "content": system})

        for msg in self.get_context_messages():
            messages.append(msg.to_dict())

        messages.append({"role": "user", "content": user_message})
        return messages

    def chat(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> ProviderResponse:
        client = self._get_client()
        messages = self._build_messages(user_message, system_override)

        logger.debug(f"[OpenAI] 요청: {user_message[:100]}...")

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        content = response.choices[0].message.content or ""
        finish_reason = response.choices[0].finish_reason or "stop"

        self.add_message(Message.user(user_message))
        self.add_message(Message.assistant(content))

        logger.debug(f"[OpenAI] 응답 ({response.usage.total_tokens} 토큰)")

        return ProviderResponse(
            content=content,
            provider=self.name,
            model=self.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            finish_reason=finish_reason,
        )

    def stream(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> Generator[str, None, None]:
        client = self._get_client()
        messages = self._build_messages(user_message, system_override)

        logger.debug(f"[OpenAI] 스트리밍 요청: {user_message[:100]}...")

        full_content = ""

        with client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_content += delta
                    yield delta

        self.add_message(Message.user(user_message))
        self.add_message(Message.assistant(full_content))
        logger.debug(f"[OpenAI] 스트리밍 완료 ({len(full_content)} 글자)")
