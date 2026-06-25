import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.diagnostics import format_provider_checks, run_provider_checks


class DiagnosticsTests(unittest.TestCase):
    def test_provider_checks_skip_missing_api_keys(self):
        config = JarvisConfig(openai_api_key=None, anthropic_api_key=None)

        with patch(
            "jarvis_assistant.providers.open_interpreter_provider.OpenInterpreterProvider.is_available",
            return_value=False,
        ):
            checks = run_provider_checks(config, "테스트")

        by_provider = {check.provider: check for check in checks}

        self.assertEqual(by_provider["local"].status, "준비됨")
        self.assertEqual(by_provider["windows_automation"].status, "준비됨")
        self.assertEqual(by_provider["chatgpt"].status, "선택 기능")
        self.assertIn("OPENAI_API_KEY", by_provider["chatgpt"].message)
        self.assertEqual(by_provider["claude"].status, "선택 기능")
        self.assertIn("ANTHROPIC_API_KEY", by_provider["claude"].message)

    def test_format_provider_checks_outputs_korean_summary(self):
        config = JarvisConfig(openai_api_key=None, anthropic_api_key=None)

        with patch(
            "jarvis_assistant.providers.open_interpreter_provider.OpenInterpreterProvider.is_available",
            return_value=True,
        ):
            output = format_provider_checks(run_provider_checks(config, "테스트"))

        self.assertIn("Jarvis Provider 연결 테스트 결과", output)
        self.assertIn("local: 준비됨", output)
        self.assertIn("windows_automation: 준비됨", output)
        self.assertIn("chatgpt: 선택 기능", output)
        self.assertIn("claude: 선택 기능", output)
        self.assertIn("open_interpreter: 준비됨", output)


if __name__ == "__main__":
    unittest.main()
