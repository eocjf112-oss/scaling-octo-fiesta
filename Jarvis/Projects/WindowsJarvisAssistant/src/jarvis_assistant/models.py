from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


ProviderName = str


@dataclass(frozen=True)
class ChatRequest:
    """Provider에 전달되는 공통 요청 모델입니다."""

    prompt: str
    provider: ProviderName = "auto"
    system_prompt: str | None = None
    temperature: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChatResponse:
    """Provider에서 반환되는 공통 응답 모델입니다."""

    provider: ProviderName
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ChatProvider(Protocol):
    """ChatGPT, Claude, Open Interpreter가 구현해야 하는 공통 계약입니다."""

    name: ProviderName

    def is_available(self) -> bool:
        """현재 환경에서 Provider를 사용할 수 있으면 True를 반환합니다."""

    def complete(self, request: ChatRequest) -> ChatResponse:
        """요청을 처리하고 공통 응답 모델로 반환합니다."""


class ProviderError(RuntimeError):
    """Provider 호출 중 발생한 오류입니다."""


class ProviderNotAvailableError(ProviderError):
    """요청한 Provider가 현재 환경에서 사용 불가능할 때 발생합니다."""
