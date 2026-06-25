"""
Jarvis AI — 기본 프로바이더 추상 클래스

모든 AI 프로바이더(OpenAI, Claude, Interpreter)가 구현해야 하는 인터페이스를 정의합니다.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Generator


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: MessageRole
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role.value, "content": self.content}

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role=MessageRole.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role=MessageRole.ASSISTANT, content=content)


@dataclass
class ProviderResponse:
    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"
    raw: dict = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class BaseProvider(ABC):
    """AI 프로바이더 기본 추상 클래스"""

    name: str = "base"
    display_name: str = "Base Provider"

    def __init__(self, system_prompt: str = "") -> None:
        self.system_prompt = system_prompt
        self._conversation_history: list[Message] = []

    @property
    def history(self) -> list[Message]:
        return self._conversation_history.copy()

    def add_message(self, message: Message) -> None:
        self._conversation_history.append(message)

    def clear_history(self) -> None:
        self._conversation_history.clear()

    def get_context_messages(self, max_messages: int = 20) -> list[Message]:
        """최근 N개 메시지만 컨텍스트로 반환 (토큰 절약)"""
        return self._conversation_history[-max_messages:]

    @abstractmethod
    def chat(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> ProviderResponse:
        """동기 채팅 (단일 응답)"""
        ...

    @abstractmethod
    def stream(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> Generator[str, None, ProviderResponse]:
        """스트리밍 채팅 (실시간 출력)"""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """프로바이더 사용 가능 여부 확인"""
        ...

    def reset(self) -> None:
        """대화 기록 초기화"""
        self.clear_history()
