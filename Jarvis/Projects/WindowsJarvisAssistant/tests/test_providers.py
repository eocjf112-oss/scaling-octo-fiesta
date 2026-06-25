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


class ProviderAvailabilityTests(unittest.TestCase):
    def test_chatgpt_requires_api_key(self):
        self.assertFalse(ChatGPTProvider(JarvisConfig(openai_api_key=None)).is_available())
        self.assertTrue(ChatGPTProvider(JarvisConfig(openai_api_key="key")).is_available())

    def test_claude_requires_api_key(self):
        self.assertFalse(ClaudeProvider(JarvisConfig(anthropic_api_key=None)).is_available())
        self.assertTrue(ClaudeProvider(JarvisConfig(anthropic_api_key="key")).is_available())

    def test_open_interpreter_uses_command_lookup(self):
        provider = OpenInterpreterProvider(JarvisConfig(open_interpreter_command="interpreter"))

        with patch("jarvis_assistant.providers.open_interpreter_provider.shutil.which", return_value=None):
            self.assertFalse(provider.is_available())

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
