import unittest
from pathlib import Path


class WindowsScriptsTests(unittest.TestCase):
    def test_gui_and_tray_scripts_exist(self):
        root = Path(__file__).resolve().parents[1]

        self.assertTrue((root / "scripts" / "windows" / "jarvis-gui.ps1").is_file())
        self.assertTrue((root / "scripts" / "windows" / "jarvis-tray.ps1").is_file())
        self.assertTrue((root / "scripts" / "windows" / "test-jarvis.ps1").is_file())

    def test_jarvis_bat_exposes_gui_commands(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "Jarvis.bat").read_text(encoding="utf-8")

        self.assertIn('if /I "%~1"=="gui" goto gui_start', content)
        self.assertIn('if /I "%~1"=="settings" goto settings_start', content)
        self.assertIn("jarvis-gui.ps1", content)
        self.assertIn("pip install -e .", content)


if __name__ == "__main__":
    unittest.main()
