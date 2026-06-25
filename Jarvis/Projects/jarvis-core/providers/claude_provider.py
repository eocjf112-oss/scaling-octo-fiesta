"""
Jarvis AI — Anthropic (Claude) 프로바이더

Claude Opus, Sonnet, Haiku 모델과 연결합니다.
스트리밍 응답 및 대화 기록 관리를 지원합니다.
"""

from __future__ import annotations

from typing import Generator

from loguru import logger

from .base_provider import BaseProvider, Message, MessageRole, ProviderResponse


class ClaudeProvider(BaseProvider):
    """Anthropic Claude 프로바이더"""

    name = "claude"
    display_name = "Claude (Anthropic)"

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-5",
        max_tokens: int = 4096,
        system_prompt: str = "",
    ) -> None:
        super().__init__(system_prompt=system_prompt)
        self._api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        """Anthropic 클라이언트 지연 초기화"""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "anthropic 패키지가 설치되지 않았습니다. "
                    "'pip install anthropic' 를 실행하세요."
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

    def _build_messages(self, user_message: str) -> list[dict]:
        """Claude 형식의 메시지 목록 구성 (system은 별도 파라미터)"""
        messages = []
        for msg in self.get_context_messages():
            if msg.role != MessageRole.SYSTEM:
                messages.append(msg.to_dict())
        messages.append({"role": "user", "content": user_message})
        return messages

    def chat(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> ProviderResponse:
        client = self._get_client()
        messages = self._build_messages(user_message)
        system = system_override or self.system_prompt

        logger.debug(f"[Claude] 요청: {user_message[:100]}...")

        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = client.messages.create(**kwargs)

        content = response.content[0].text if response.content else ""
        finish_reason = response.stop_reason or "end_turn"

        self.add_message(Message.user(user_message))
        self.add_message(Message.assistant(content))

        logger.debug(
            f"[Claude] 응답 (입력 {response.usage.input_tokens} / "
            f"출력 {response.usage.output_tokens} 토큰)"
        )

        return ProviderResponse(
            content=content,
            provider=self.name,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=finish_reason,
        )

    def stream(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> Generator[str, None, None]:
        client = self._get_client()
        messages = self._build_messages(user_message)
        system = system_override or self.system_prompt

        logger.debug(f"[Claude] 스트리밍 요청: {user_message[:100]}...")

        full_content = ""

        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        with client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                full_content += text
                yield text

        self.add_message(Message.user(user_message))
        self.add_message(Message.assistant(full_content))
        logger.debug(f"[Claude] 스트리밍 완료 ({len(full_content)} 글자)")
