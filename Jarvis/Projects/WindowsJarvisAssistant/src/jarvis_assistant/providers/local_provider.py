from __future__ import annotations

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse


class LocalJarvisProvider:
    name = "local"

    def __init__(self, config: JarvisConfig):
        self._config = config

    def is_available(self) -> bool:
        return True

    def complete(self, request: ChatRequest) -> ChatResponse:
        lines = [
            "Jarvis 로컬 모드가 실행 중입니다.",
            "",
            "현재 API 키 없이 사용할 수 있는 기능:",
            "- Open Interpreter 연동 준비 및 안전 실행",
            "- Windows 자동화 명령 라우팅",
            "- 음성 입출력 모듈 준비 상태 점검",
            "- SQLite 장기 기억 자동 로드 및 작업 기록 저장",
        ]

        memory_context = request.metadata.get("memory_context")
        if memory_context is not None:
            lines.extend(
                [
                    "",
                    "장기 기억 상태:",
                    f"- 사용자 정보: {len(getattr(memory_context, 'user_profile', {}))}개 로드됨",
                    f"- 프로젝트 상태: {len(getattr(memory_context, 'project_statuses', []))}개 로드됨",
                    f"- 최근 작업 기록: {len(getattr(memory_context, 'recent_work', []))}개 로드됨",
                ]
            )

        lines.extend(
            [
                "",
                "사용 예시:",
                "- Jarvis.bat test",
                "- Jarvis.bat providers",
                "- Jarvis.bat voice",
                "- Jarvis.bat memory",
                "- Jarvis.bat startup install",
                "- Jarvis.bat windows status",
                "- Jarvis.bat excel \"월간 계획\"",
                "- Jarvis.bat word \"회의록\"",
                "- Jarvis.bat pdf \"보고서\"",
                "- Jarvis.bat search \"계획\"",
                "- Jarvis.bat organize",
                "- Jarvis.bat run notepad",
                "- Jarvis.bat web \"오늘 날씨\"",
                "- Jarvis.bat oi \"현재 폴더를 요약해줘\"",
                "",
                "추후 OpenAI/Anthropic API 키를 .env에 넣으면 ChatGPT/Claude Provider가 자동으로 활성화됩니다.",
            ]
        )
        content = "\n".join(lines)
        return ChatResponse(
            provider=self.name,
            content=content,
            metadata={"workspace_root": str(self._config.workspace_root)},
        )
