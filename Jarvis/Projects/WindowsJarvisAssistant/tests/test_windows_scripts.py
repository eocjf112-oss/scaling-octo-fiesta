import unittest
from pathlib import Path


class WindowsScriptsTests(unittest.TestCase):
    def test_gui_and_tray_scripts_exist(self):
        root = Path(__file__).resolve().parents[1]

        self.assertTrue((root / "scripts" / "windows" / "jarvis-gui.ps1").is_file())
        self.assertTrue((root / "scripts" / "windows" / "jarvis-tray.ps1").is_file())
        self.assertTrue((root / "scripts" / "windows" / "test-jarvis.ps1").is_file())

    def test_tray_script_uses_ascii_menu_labels(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "scripts" / "windows" / "jarvis-tray.ps1").read_text(encoding="ascii")

        self.assertIn("Open Control Panel", content)
        self.assertIn("Test Menu", content)
        self.assertIn("Open Calculator", content)
        self.assertIn("Exit Jarvis", content)
        self.assertNotIn("메모장", content)
        self.assertNotIn("자비스", content)

    def test_jarvis_bat_exposes_gui_commands(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "Jarvis.bat").read_text(encoding="utf-8")

        self.assertIn('if /I "%~1"=="gui" goto gui_start', content)
        self.assertIn('if /I "%~1"=="settings" goto settings_start', content)
        self.assertIn('if "%~1"=="자비스" goto gui_start', content)
        self.assertIn('if /I "%~1"=="calc" goto action_calc', content)
        self.assertIn("jarvis-gui.ps1", content)
        self.assertIn("tray_fallback", content)
        self.assertIn("cli_fallback", content)
        self.assertIn(":join_args", content)
        self.assertIn('"%JARVIS_PROMPT%"', content)
        self.assertIn("pip install -e .", content)

    def test_gui_exposes_all_api_less_buttons(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "scripts" / "windows" / "jarvis-gui.ps1").read_text(encoding="utf-8")

        for label in (
            "Jarvis Control Panel",
            "Open Notepad",
            "Open Calculator",
            "Create PDF",
            "Create Excel",
            "Create Word",
            "Organize Downloads",
            "Web Search",
            "Memory Status",
            "Save Memory Test",
            "Command:",
        ):
            self.assertIn(label, content)

    def test_gui_script_has_no_utf8_bom(self):
        root = Path(__file__).resolve().parents[1]
        data = (root / "scripts" / "windows" / "jarvis-gui.ps1").read_bytes()

        self.assertFalse(data.startswith(b"\xef\xbb\xbf"))


if __name__ == "__main__":
    unittest.main()
