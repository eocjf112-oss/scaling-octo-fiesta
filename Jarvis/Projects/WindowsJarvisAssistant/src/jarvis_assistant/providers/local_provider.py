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
        content = "\n".join(
            [
                "Jarvis 로컬 모드가 실행 중입니다.",
                "",
                "현재 API 키 없이 사용할 수 있는 기능:",
                "- Open Interpreter 연동 준비 및 안전 실행",
                "- Windows 자동화 명령 라우팅",
                "- 음성 입출력 모듈 준비 상태 점검",
                "",
                "사용 예시:",
                "- Jarvis.bat test",
                "- Jarvis.bat providers",
                "- Jarvis.bat voice",
                "- Jarvis.bat windows status",
                "- Jarvis.bat oi \"현재 폴더를 요약해줘\"",
                "",
                "추후 OpenAI/Anthropic API 키를 .env에 넣으면 ChatGPT/Claude Provider가 자동으로 활성화됩니다.",
            ]
        )
        return ChatResponse(
            provider=self.name,
            content=content,
            metadata={"workspace_root": str(self._config.workspace_root)},
        )
