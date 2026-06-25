import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig
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


if __name__ == "__main__":
    unittest.main()
