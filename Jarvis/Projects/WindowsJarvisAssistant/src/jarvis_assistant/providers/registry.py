from __future__ import annotations

from collections.abc import Iterable

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatProvider, ProviderName, ProviderNotAvailableError
from jarvis_assistant.providers.anthropic_provider import ClaudeProvider
from jarvis_assistant.providers.open_interpreter_provider import OpenInterpreterProvider
from jarvis_assistant.providers.openai_provider import ChatGPTProvider


class ProviderRegistry:
    def __init__(self, providers: Iterable[ChatProvider]):
        self._providers = {provider.name: provider for provider in providers}

    @classmethod
    def from_config(cls, config: JarvisConfig) -> "ProviderRegistry":
        return cls(
            [
                ChatGPTProvider(config),
                ClaudeProvider(config),
                OpenInterpreterProvider(config),
            ]
        )

    def names(self) -> list[ProviderName]:
        return list(self._providers)

    def available_names(self) -> list[ProviderName]:
        return [name for name, provider in self._providers.items() if provider.is_available()]

    def get(self, name: ProviderName) -> ChatProvider:
        provider = self._providers.get(name)
        if provider is None:
            raise ProviderNotAvailableError(f"Unknown provider: {name}")
        if not provider.is_available():
            raise ProviderNotAvailableError(f"Provider is not available: {name}")
        return provider
