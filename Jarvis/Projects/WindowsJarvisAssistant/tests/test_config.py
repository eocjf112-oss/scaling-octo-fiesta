import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig


class JarvisConfigTests(unittest.TestCase):
    def test_from_env_uses_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = JarvisConfig.from_env()

        self.assertEqual(config.default_provider, "chatgpt")
        self.assertEqual(config.openai_model, "gpt-4o-mini")
        self.assertEqual(config.anthropic_model, "claude-3-5-sonnet-latest")
        self.assertEqual(config.open_interpreter_timeout_seconds, 120)
        self.assertFalse(config.open_interpreter_auto_yes)

    def test_from_env_reads_overrides(self):
        env = {
            "JARVIS_DEFAULT_PROVIDER": "claude",
            "OPENAI_API_KEY": "openai-key",
            "JARVIS_OPENAI_MODEL": "gpt-test",
            "ANTHROPIC_API_KEY": "anthropic-key",
            "JARVIS_ANTHROPIC_MODEL": "claude-test",
            "JARVIS_OPEN_INTERPRETER_COMMAND": "interpreter",
            "JARVIS_OPEN_INTERPRETER_TIMEOUT_SECONDS": "30",
            "JARVIS_OPEN_INTERPRETER_AUTO_YES": "true",
        }

        with patch.dict(os.environ, env, clear=True):
            config = JarvisConfig.from_env()

        self.assertEqual(config.default_provider, "claude")
        self.assertEqual(config.openai_api_key, "openai-key")
        self.assertEqual(config.openai_model, "gpt-test")
        self.assertEqual(config.anthropic_api_key, "anthropic-key")
        self.assertEqual(config.anthropic_model, "claude-test")
        self.assertEqual(config.open_interpreter_timeout_seconds, 30)
        self.assertTrue(config.open_interpreter_auto_yes)


if __name__ == "__main__":
    unittest.main()
