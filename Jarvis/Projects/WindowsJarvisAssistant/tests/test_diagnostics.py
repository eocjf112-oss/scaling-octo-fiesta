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

        self.assertEqual(checks[0].provider, "chatgpt")
        self.assertEqual(checks[0].status, "건너뜀")
        self.assertIn("OPENAI_API_KEY", checks[0].message)
        self.assertEqual(checks[1].provider, "claude")
        self.assertEqual(checks[1].status, "건너뜀")
        self.assertIn("ANTHROPIC_API_KEY", checks[1].message)

    def test_format_provider_checks_outputs_korean_summary(self):
        config = JarvisConfig(openai_api_key=None, anthropic_api_key=None)

        with patch(
            "jarvis_assistant.providers.open_interpreter_provider.OpenInterpreterProvider.is_available",
            return_value=True,
        ):
            output = format_provider_checks(run_provider_checks(config, "테스트"))

        self.assertIn("Jarvis Provider 연결 테스트 결과", output)
        self.assertIn("chatgpt: 건너뜀", output)
        self.assertIn("claude: 건너뜀", output)
        self.assertIn("open_interpreter: 준비됨", output)


if __name__ == "__main__":
    unittest.main()
