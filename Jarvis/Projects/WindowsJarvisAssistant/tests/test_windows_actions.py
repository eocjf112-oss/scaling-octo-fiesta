import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.windows_actions import (
    create_excel_document,
    create_pdf_document,
    create_word_document,
    internet_search,
    organize_files,
    run_windows_action,
    search_files,
)


class WindowsActionsTests(unittest.TestCase):
    def test_create_excel_word_and_pdf_documents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = JarvisConfig(workspace_root=Path(temp_dir))

            excel = create_excel_document(config, "월간 계획")
            word = create_word_document(config, "회의록")
            pdf = create_pdf_document(config, "보고서")

            self.assertTrue(excel.path.is_file())
            self.assertTrue(word.path.is_file())
            self.assertTrue(pdf.path.is_file())
            with ZipFile(excel.path) as archive:
                self.assertIn("xl/workbook.xml", archive.namelist())
            with ZipFile(word.path) as archive:
                self.assertIn("word/document.xml", archive.namelist())
            self.assertTrue(pdf.path.read_bytes().startswith(b"%PDF-1.4"))

    def test_search_files_finds_matching_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "Documents" / "project-plan.txt"
            target.parent.mkdir()
            target.write_text("test", encoding="utf-8")

            result = search_files(JarvisConfig(workspace_root=root), "plan")

            self.assertTrue(result.success)
            self.assertIn("project-plan.txt", result.message)

    def test_organize_files_groups_downloads_by_extension(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            downloads = root / "Downloads"
            downloads.mkdir()
            (downloads / "report.pdf").write_text("pdf", encoding="utf-8")
            (downloads / "data.csv").write_text("csv", encoding="utf-8")

            result = organize_files(JarvisConfig(workspace_root=root))

            self.assertTrue(result.success)
            self.assertTrue((downloads / "Documents" / "report.pdf").is_file())
            self.assertTrue((downloads / "Spreadsheets" / "data.csv").is_file())

    def test_organize_files_uses_configured_downloads_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            downloads = root / "CustomDownloads"
            downloads.mkdir()
            (downloads / "note.txt").write_text("txt", encoding="utf-8")

            result = organize_files(JarvisConfig(workspace_root=root, downloads_dir=downloads))

            self.assertTrue(result.success)
            self.assertTrue((downloads / "Documents" / "note.txt").is_file())

    def test_internet_search_builds_google_url_without_api(self):
        with patch("jarvis_assistant.windows_actions.platform.system", return_value="Windows"), patch(
            "jarvis_assistant.windows_actions.webbrowser.open", return_value=True
        ) as opened:
            result = internet_search("자비스 자동화")

        self.assertTrue(result.success)
        self.assertIn("https://www.google.com/search?q=", result.message)
        opened.assert_called_once()

    def test_internet_search_does_not_open_browser_outside_windows(self):
        with patch("jarvis_assistant.windows_actions.platform.system", return_value="Linux"), patch(
            "jarvis_assistant.windows_actions.webbrowser.open", return_value=True
        ) as opened:
            result = internet_search("자비스 자동화")

        self.assertTrue(result.success)
        self.assertIn("브라우저를 열지 않았습니다", result.message)
        opened.assert_not_called()

    def test_run_windows_action_dispatches_excel(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_windows_action("엑셀 월간 계획", JarvisConfig(workspace_root=Path(temp_dir)))

            self.assertEqual(result.action, "excel")
            self.assertTrue(result.path.is_file())

    def test_korean_voice_phrases_dispatch_to_local_actions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = JarvisConfig(workspace_root=Path(temp_dir))

            excel = run_windows_action("엑셀 만들어", config)
            pdf = run_windows_action("PDF 만들어", config)
            organize = run_windows_action("다운로드 정리해", config)
            with patch("jarvis_assistant.windows_actions.platform.system", return_value="Linux"):
                notepad = run_windows_action("메모장 열어줘", config)
                web = run_windows_action("인터넷 검색해", config)

            self.assertEqual(excel.action, "excel")
            self.assertTrue(excel.path.is_file())
            self.assertEqual(pdf.action, "pdf")
            self.assertTrue(pdf.path.is_file())
            self.assertEqual(organize.action, "organize")
            self.assertEqual(notepad.action, "run")
            self.assertIn("notepad", notepad.message)
            self.assertEqual(web.action, "web")
            self.assertIn("https://www.google.com/search", web.message)


if __name__ == "__main__":
    unittest.main()
