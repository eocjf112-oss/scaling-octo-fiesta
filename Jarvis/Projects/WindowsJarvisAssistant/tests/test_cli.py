import sys
import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.cli import main


class CliTests(unittest.TestCase):
    def test_prompt_tokens_are_joined(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env = {
                "JARVIS_ENV_FILE": str(Path(temp_dir) / "missing.env"),
                "JARVIS_WORKSPACE_ROOT": temp_dir,
                "JARVIS_MEMORY_DB_PATH": str(Path(temp_dir) / "memory.sqlite3"),
            }
            with patch.dict(os.environ, env, clear=True), patch("builtins.print") as printed:
                exit_code = main(["--provider", "windows_automation", "web", "오늘", "날씨"])

        self.assertEqual(exit_code, 0)
        output = "\n".join(str(call.args[0]) for call in printed.call_args_list)
        self.assertIn("https://www.google.com/search", output)


if __name__ == "__main__":
    unittest.main()
