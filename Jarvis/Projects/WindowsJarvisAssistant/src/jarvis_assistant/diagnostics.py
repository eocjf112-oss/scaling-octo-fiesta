from __future__ import annotations

from dataclasses import dataclass

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ProviderError
from jarvis_assistant.providers.anthropic_provider import ClaudeProvider
from jarvis_assistant.providers.local_provider import LocalJarvisProvider
from jarvis_assistant.providers.open_interpreter_provider import OpenInterpreterProvider
from jarvis_assistant.providers.openai_provider import ChatGPTProvider
from jarvis_assistant.providers.windows_automation_provider import WindowsAutomationProvider


@dataclass(frozen=True)
class ProviderCheck:
    provider: str
    status: str
    message: str


def run_provider_checks(config: JarvisConfig, prompt: str) -> list[ProviderCheck]:
    checks = [
        _check_always_available(LocalJarvisProvider(config), "API 없이 기본 응답을 제공합니다."),
        _check_always_available(WindowsAutomationProvider(config), "Windows 자동화 준비 기능을 제공합니다."),
        _check_open_interpreter(OpenInterpreterProvider(config)),
        _check_chat_provider(ChatGPTProvider(config), prompt, "OPENAI_API_KEY"),
        _check_chat_provider(ClaudeProvider(config), prompt, "ANTHROPIC_API_KEY"),
    ]
    return checks


def format_provider_checks(checks: list[ProviderCheck]) -> str:
    lines = ["Jarvis Provider 연결 테스트 결과"]
    for check in checks:
        lines.append(f"- {check.provider}: {check.status} - {check.message}")
    return "\n".join(lines)


def _check_chat_provider(provider, prompt: str, api_key_name: str) -> ProviderCheck:
    if not provider.is_available():
        return ProviderCheck(
            provider=provider.name,
            status="선택 기능",
            message=f"{api_key_name}가 비어 있어 비활성화되어 있습니다. API 없이도 Jarvis는 계속 동작합니다.",
        )

    try:
        response = provider.complete(
            ChatRequest(
                prompt=prompt,
                provider=provider.name,
                system_prompt="당신은 Jarvis 연결 테스트에 응답하는 AI입니다. 한 문장으로만 답하세요.",
                temperature=0,
            )
        )
    except ProviderError as exc:
        return ProviderCheck(provider=provider.name, status="실패", message=str(exc))
    except Exception as exc:  # 외부 SDK 오류를 사용자에게 짧게 전달합니다.
        return ProviderCheck(provider=provider.name, status="실패", message=f"{type(exc).__name__}: {exc}")

    preview = response.content.strip().replace("\n", " ")
    if len(preview) > 120:
        preview = f"{preview[:117]}..."
    return ProviderCheck(provider=provider.name, status="성공", message=preview or "응답이 비어 있습니다.")


def _check_open_interpreter(provider: OpenInterpreterProvider) -> ProviderCheck:
    if provider.is_available():
        return ProviderCheck(
            provider=provider.name,
            status="준비됨",
            message="Open Interpreter CLI를 찾았습니다. 로컬 실행은 별도 확인 후 수행합니다.",
        )
    return ProviderCheck(
        provider=provider.name,
        status="건너뜀",
        message="Open Interpreter CLI를 찾지 못했습니다.",
    )


def _check_always_available(provider, message: str) -> ProviderCheck:
    return ProviderCheck(provider=provider.name, status="준비됨", message=message)
