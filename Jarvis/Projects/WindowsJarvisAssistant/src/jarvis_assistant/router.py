from __future__ import annotations

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse, ProviderName, ProviderNotAvailableError
from jarvis_assistant.providers.registry import ProviderRegistry


LOCAL_ACTION_KEYWORDS = (
    "file",
    "folder",
    "directory",
    "powershell",
    "cmd",
    "windows",
    "local",
    "execute",
    "run command",
    "파일",
    "폴더",
    "디렉터리",
    "윈도우",
    "명령",
    "실행",
    "로컬",
)

WINDOWS_AUTOMATION_KEYWORDS = (
    "automation",
    "windows status",
    "system status",
    "excel",
    "word",
    "pdf",
    "search file",
    "file search",
    "organize",
    "launch",
    "open program",
    "internet",
    "browser",
    "윈도우 자동화",
    "자동화",
    "상태 점검",
    "시스템 상태",
    "엑셀",
    "워드",
    "피디에프",
    "파일 검색",
    "파일 정리",
    "프로그램 실행",
    "인터넷",
    "웹 검색",
)


class JarvisRouter:
    def __init__(self, config: JarvisConfig, registry: ProviderRegistry | None = None):
        self._config = config
        self._registry = registry or ProviderRegistry.from_config(config)

    def dispatch(self, request: ChatRequest) -> ChatResponse:
        provider_name = self.select_provider(request)
        provider = self._registry.get(provider_name, require_available=request.provider == "auto")
        return provider.complete(request)

    def select_provider(self, request: ChatRequest) -> ProviderName:
        if request.provider != "auto":
            return request.provider

        available = self._registry.available_names()
        if not available:
            return "local"

        prompt = request.prompt.lower()
        if "windows_automation" in available and any(
            keyword in prompt for keyword in WINDOWS_AUTOMATION_KEYWORDS
        ):
            return "windows_automation"
        if "open_interpreter" in available and any(keyword in prompt for keyword in LOCAL_ACTION_KEYWORDS):
            return "open_interpreter"

        if self._config.default_provider in available:
            return self._config.default_provider

        for candidate in self._config.provider_priority:
            if candidate in available:
                return candidate

        return "local"

    def available_providers(self) -> list[ProviderName]:
        return self._registry.available_names()
