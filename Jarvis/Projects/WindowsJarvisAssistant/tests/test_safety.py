import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.models import ChatRequest
from jarvis_assistant.safety import OpenInterpreterSafetyPolicy, RiskLevel


class OpenInterpreterSafetyPolicyTests(unittest.TestCase):
    def test_allows_low_risk_prompt(self):
        policy = OpenInterpreterSafetyPolicy()

        decision = policy.evaluate(ChatRequest(prompt="현재 프로젝트 구조를 설명해줘"))

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.risk_level, RiskLevel.LOW)

    def test_requires_confirmation_for_local_execution(self):
        policy = OpenInterpreterSafetyPolicy()

        decision = policy.evaluate(ChatRequest(prompt="PowerShell 명령을 실행해서 파일 목록을 확인해줘"))

        self.assertFalse(decision.allowed)
        self.assertTrue(decision.requires_confirmation)
        self.assertEqual(decision.risk_level, RiskLevel.MEDIUM)

    def test_allows_confirmed_local_execution(self):
        policy = OpenInterpreterSafetyPolicy()

        decision = policy.evaluate(
            ChatRequest(
                prompt="PowerShell 명령을 실행해서 파일 목록을 확인해줘",
                metadata={"confirm_local_execution": True},
            )
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.risk_level, RiskLevel.MEDIUM)

    def test_blocks_destructive_prompt(self):
        policy = OpenInterpreterSafetyPolicy()

        decision = policy.evaluate(ChatRequest(prompt="format c: 명령을 실행해줘"))

        self.assertFalse(decision.allowed)
        self.assertFalse(decision.requires_confirmation)
        self.assertEqual(decision.risk_level, RiskLevel.BLOCKED)


if __name__ == "__main__":
    unittest.main()
