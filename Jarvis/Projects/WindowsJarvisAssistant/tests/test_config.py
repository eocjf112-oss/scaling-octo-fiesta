import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig


class JarvisConfigTests(unittest.TestCase):
    def test_from_env_uses_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = JarvisConfig.from_env()

        self.assertEqual(config.default_provider, "local")
        self.assertEqual(
            config.provider_priority,
            ("windows_automation", "open_interpreter", "local", "chatgpt", "claude"),
        )
        self.assertEqual(config.openai_model, "gpt-4o-mini")
        self.assertEqual(config.anthropic_model, "claude-3-5-sonnet-latest")
        self.assertEqual(config.memory_db_path, config.workspace_root / "Memory" / "jarvis_memory.sqlite3")
        self.assertEqual(config.open_interpreter_timeout_seconds, 120)
        self.assertFalse(config.open_interpreter_auto_yes)
        self.assertTrue(config.open_interpreter_require_confirmation)

    def test_from_env_reads_overrides(self):
        env = {
            "JARVIS_DEFAULT_PROVIDER": "claude",
            "JARVIS_PROVIDER_PRIORITY": "claude,chatgpt,open_interpreter",
            "JARVIS_WORKSPACE_ROOT": str(Path("/tmp/jarvis-root")),
            "JARVIS_MEMORY_DB_PATH": str(Path("/tmp/jarvis-root/Memory/test.sqlite3")),
            "OPENAI_API_KEY": "openai-key",
            "JARVIS_OPENAI_MODEL": "gpt-test",
            "ANTHROPIC_API_KEY": "anthropic-key",
            "JARVIS_ANTHROPIC_MODEL": "claude-test",
            "JARVIS_OPEN_INTERPRETER_COMMAND": "interpreter",
            "JARVIS_OPEN_INTERPRETER_WORKDIR": str(Path("/tmp/jarvis-root/Temp/OpenInterpreter")),
            "JARVIS_OPEN_INTERPRETER_TIMEOUT_SECONDS": "30",
            "JARVIS_OPEN_INTERPRETER_AUTO_YES": "true",
            "JARVIS_OPEN_INTERPRETER_REQUIRE_CONFIRMATION": "false",
        }

        with patch.dict(os.environ, env, clear=True):
            config = JarvisConfig.from_env()

        self.assertEqual(config.default_provider, "claude")
        self.assertEqual(config.provider_priority, ("claude", "chatgpt", "open_interpreter"))
        self.assertEqual(config.workspace_root, Path("/tmp/jarvis-root"))
        self.assertEqual(config.memory_db_path, Path("/tmp/jarvis-root/Memory/test.sqlite3"))
        self.assertEqual(config.openai_api_key, "openai-key")
        self.assertEqual(config.openai_model, "gpt-test")
        self.assertEqual(config.anthropic_api_key, "anthropic-key")
        self.assertEqual(config.anthropic_model, "claude-test")
        self.assertEqual(config.open_interpreter_workdir, Path("/tmp/jarvis-root/Temp/OpenInterpreter"))
        self.assertEqual(config.open_interpreter_timeout_seconds, 30)
        self.assertTrue(config.open_interpreter_auto_yes)
        self.assertFalse(config.open_interpreter_require_confirmation)

    def test_from_env_loads_env_file_without_overriding_existing_environment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "OPENAI_API_KEY=from-env-file",
                        "ANTHROPIC_API_KEY=from-env-file",
                        "JARVIS_DEFAULT_PROVIDER=claude",
                        "JARVIS_PROVIDER_PRIORITY=claude,chatgpt",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    "JARVIS_ENV_FILE": str(env_path),
                    "OPENAI_API_KEY": "from-process",
                },
                clear=True,
            ):
                config = JarvisConfig.from_env()

        self.assertEqual(config.env_file, env_path)
        self.assertEqual(config.openai_api_key, "from-process")
        self.assertEqual(config.anthropic_api_key, "from-env-file")
        self.assertEqual(config.default_provider, "claude")
        self.assertEqual(config.provider_priority, ("claude", "chatgpt"))


if __name__ == "__main__":
    unittest.main()
