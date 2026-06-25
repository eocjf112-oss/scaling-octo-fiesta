import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse
from jarvis_assistant.providers.registry import ProviderRegistry
from jarvis_assistant.router import JarvisRouter


class FakeProvider:
    def __init__(self, name, available=True):
        self.name = name
        self._available = available

    def is_available(self):
        return self._available

    def complete(self, request):
        return ChatResponse(provider=self.name, content=f"{self.name}: {request.prompt}")


class JarvisRouterTests(unittest.TestCase):
    def test_selects_explicit_provider(self):
        registry = ProviderRegistry([FakeProvider("chatgpt"), FakeProvider("claude")])
        router = JarvisRouter(JarvisConfig(default_provider="chatgpt"), registry)

        selected = router.select_provider(ChatRequest(prompt="hello", provider="claude"))

        self.assertEqual(selected, "claude")

    def test_auto_uses_default_provider_when_available(self):
        registry = ProviderRegistry([FakeProvider("chatgpt"), FakeProvider("claude")])
        router = JarvisRouter(JarvisConfig(default_provider="claude"), registry)

        selected = router.select_provider(ChatRequest(prompt="문서를 요약해줘"))

        self.assertEqual(selected, "claude")

    def test_auto_routes_local_actions_to_open_interpreter(self):
        registry = ProviderRegistry(
            [
                FakeProvider("chatgpt"),
                FakeProvider("claude"),
                FakeProvider("open_interpreter"),
            ]
        )
        router = JarvisRouter(JarvisConfig(default_provider="chatgpt"), registry)

        selected = router.select_provider(ChatRequest(prompt="현재 폴더 파일을 확인해줘"))

        self.assertEqual(selected, "open_interpreter")

    def test_dispatch_calls_selected_provider(self):
        registry = ProviderRegistry([FakeProvider("chatgpt")])
        router = JarvisRouter(JarvisConfig(default_provider="chatgpt"), registry)

        response = router.dispatch(ChatRequest(prompt="hello"))

        self.assertEqual(response.provider, "chatgpt")
        self.assertEqual(response.content, "chatgpt: hello")


if __name__ == "__main__":
    unittest.main()
