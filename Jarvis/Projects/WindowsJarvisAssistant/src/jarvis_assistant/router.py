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


class JarvisRouter:
    def __init__(self, config: JarvisConfig, registry: ProviderRegistry | None = None):
        self._config = config
        self._registry = registry or ProviderRegistry.from_config(config)

    def dispatch(self, request: ChatRequest) -> ChatResponse:
        provider_name = self.select_provider(request)
        provider = self._registry.get(provider_name)
        return provider.complete(request)

    def select_provider(self, request: ChatRequest) -> ProviderName:
        if request.provider != "auto":
            return request.provider

        available = self._registry.available_names()
        if not available:
            raise ProviderNotAvailableError(
                "No provider is available. Configure OPENAI_API_KEY, ANTHROPIC_API_KEY, "
                "or install Open Interpreter."
            )

        prompt = request.prompt.lower()
        if "open_interpreter" in available and any(keyword in prompt for keyword in LOCAL_ACTION_KEYWORDS):
            return "open_interpreter"

        if self._config.default_provider in available:
            return self._config.default_provider

        for candidate in ("chatgpt", "claude", "open_interpreter"):
            if candidate in available:
                return candidate

        raise ProviderNotAvailableError("No provider could be selected.")

    def available_providers(self) -> list[ProviderName]:
        return self._registry.available_names()
