from __future__ import annotations

import platform

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse
from jarvis_assistant.windows_actions import run_windows_action


class WindowsAutomationProvider:
    name = "windows_automation"

    def __init__(self, config: JarvisConfig):
        self._config = config

    def is_available(self) -> bool:
        return True

    def complete(self, request: ChatRequest) -> ChatResponse:
        prompt = request.prompt.lower()
        if any(keyword in prompt for keyword in ("status", "상태", "점검", "check")):
            return self._status_response()
        if any(keyword in prompt for keyword in ("env", ".env", "환경", "api 키", "api key")):
            return self._env_response()
        action_result = run_windows_action(request.prompt, self._config)
        if action_result.action != "help":
            return ChatResponse(
                provider=self.name,
                content=action_result.message,
                metadata={
                    "action": action_result.action,
                    "success": action_result.success,
                    "path": str(action_result.path) if action_result.path else None,
                },
            )
        return self._help_response()

    def _status_response(self) -> ChatResponse:
        lines = [
            "Windows 자동화 Provider 상태",
            f"- 현재 OS: {platform.system()} {platform.release()}",
            f"- Jarvis 워크스페이스: {self._config.workspace_root}",
            "- 안전 정책: 로컬 파일/명령 실행은 명시적 확인 후 수행",
            "- 현재 단계: 안전한 상태 점검과 실행 가이드 제공",
            "- 다음 확장: 앱 실행, 폴더 열기, 작업 스케줄러, 음성 명령 연결",
        ]
        return ChatResponse(provider=self.name, content="\n".join(lines))

    def _env_response(self) -> ChatResponse:
        lines = [
            ".env 설정 안내",
            "- Windows에서는 `Jarvis.bat env`를 실행해 .env 파일을 열 수 있습니다.",
            "- 현재 목표는 API 없이 동작하는 구조이므로 OPENAI_API_KEY와 ANTHROPIC_API_KEY는 비워 두어도 됩니다.",
            "- 나중에 키를 넣으면 ChatGPT/Claude Provider가 자동으로 활성화됩니다.",
        ]
        return ChatResponse(provider=self.name, content="\n".join(lines))

    def _help_response(self) -> ChatResponse:
        lines = [
            "Windows 자동화 Provider 사용 예시",
            "- Jarvis.bat windows status",
            "- Jarvis.bat excel \"월간 계획\"",
            "- Jarvis.bat word \"회의록\"",
            "- Jarvis.bat pdf \"보고서\"",
            "- Jarvis.bat search \"계획\"",
            "- Jarvis.bat organize",
            "- Jarvis.bat run notepad",
            "- Jarvis.bat web \"오늘 날씨\"",
            "- Jarvis.bat env",
            "- Jarvis.bat providers",
            "- Jarvis.bat oi \"현재 폴더를 요약해줘\"",
            "",
            "현재 구현은 안전한 자동화 준비 단계입니다. 위험한 시스템 변경은 실행하지 않습니다.",
        ]
        return ChatResponse(provider=self.name, content="\n".join(lines))
