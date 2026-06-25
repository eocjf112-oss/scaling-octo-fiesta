import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ProviderError
from jarvis_assistant.providers.anthropic_provider import ClaudeProvider
from jarvis_assistant.providers.open_interpreter_provider import OpenInterpreterProvider
from jarvis_assistant.providers.openai_provider import ChatGPTProvider
from jarvis_assistant.providers.windows_automation_provider import WindowsAutomationProvider


class ProviderAvailabilityTests(unittest.TestCase):
    def test_chatgpt_requires_api_key(self):
        self.assertFalse(ChatGPTProvider(JarvisConfig(openai_api_key=None)).is_available())
        self.assertTrue(ChatGPTProvider(JarvisConfig(openai_api_key="key")).is_available())

    def test_claude_requires_api_key(self):
        self.assertFalse(ClaudeProvider(JarvisConfig(anthropic_api_key=None)).is_available())
        self.assertTrue(ClaudeProvider(JarvisConfig(anthropic_api_key="key")).is_available())

    def test_chatgpt_without_api_key_returns_guidance(self):
        response = ChatGPTProvider(JarvisConfig(openai_api_key=None)).complete(ChatRequest(prompt="테스트"))

        self.assertEqual(response.provider, "chatgpt")
        self.assertIn("비활성화", response.content)
        self.assertEqual(response.metadata["missing_api_key"], "OPENAI_API_KEY")

    def test_claude_without_api_key_returns_guidance(self):
        response = ClaudeProvider(JarvisConfig(anthropic_api_key=None)).complete(ChatRequest(prompt="테스트"))

        self.assertEqual(response.provider, "claude")
        self.assertIn("비활성화", response.content)
        self.assertEqual(response.metadata["missing_api_key"], "ANTHROPIC_API_KEY")

    def test_windows_automation_status(self):
        response = WindowsAutomationProvider(JarvisConfig()).complete(ChatRequest(prompt="상태 점검"))

        self.assertEqual(response.provider, "windows_automation")
        self.assertIn("Windows 자동화 Provider 상태", response.content)

    def test_open_interpreter_uses_command_lookup(self):
        provider = OpenInterpreterProvider(JarvisConfig(open_interpreter_command="missing-interpreter"))

        with patch("jarvis_assistant.providers.open_interpreter_provider.shutil.which", return_value=None):
            self.assertFalse(provider.is_available())

        provider = OpenInterpreterProvider(JarvisConfig(open_interpreter_command="interpreter"))
        with patch("jarvis_assistant.providers.open_interpreter_provider.shutil.which", return_value="/bin/interpreter"):
            self.assertTrue(provider.is_available())

    def test_open_interpreter_requires_confirmation_for_local_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            provider = OpenInterpreterProvider(
                JarvisConfig(
                    workspace_root=root,
                    open_interpreter_workdir=root / "Temp" / "OpenInterpreter",
                )
            )

            with self.assertRaises(ProviderError) as context:
                provider.complete(ChatRequest(prompt="파일 목록을 확인해줘"))

        self.assertIn("명시적 확인", str(context.exception))

    def test_open_interpreter_rejects_workdir_outside_workspace(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
            provider = OpenInterpreterProvider(
                JarvisConfig(
                    workspace_root=Path(root_dir),
                    open_interpreter_workdir=Path(outside_dir),
                    open_interpreter_require_confirmation=False,
                )
            )

            with patch.object(provider, "_resolve_executable", return_value="/bin/interpreter"):
                with self.assertRaises(ProviderError) as context:
                    provider.complete(ChatRequest(prompt="프로젝트 구조를 요약해줘"))

        self.assertIn("inside JARVIS_WORKSPACE_ROOT", str(context.exception))


if __name__ == "__main__":
    unittest.main()
