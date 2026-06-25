import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.voice import format_voice_status, get_voice_capabilities


class VoiceTests(unittest.TestCase):
    def test_voice_status_has_tts_and_stt_entries(self):
        output = format_voice_status(get_voice_capabilities())

        self.assertIn("Jarvis 음성 입출력 준비 상태", output)
        self.assertIn("tts:", output)
        self.assertIn("stt:", output)


if __name__ == "__main__":
    unittest.main()
