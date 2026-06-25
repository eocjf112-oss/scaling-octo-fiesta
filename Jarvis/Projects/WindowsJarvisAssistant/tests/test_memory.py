import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.memory import MemoryStore, format_memory_status


class MemoryStoreTests(unittest.TestCase):
    def test_initialize_creates_sqlite_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "memory.sqlite3"
            store = MemoryStore(db_path)

            store.initialize()

            self.assertTrue(db_path.is_file())
            self.assertEqual(store.counts()["work_history"], 0)

    def test_bootstrap_defaults_records_user_and_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = MemoryStore(root / "Memory" / "memory.sqlite3")
            store.initialize()

            store.bootstrap_defaults(JarvisConfig(workspace_root=root, memory_db_path=store.db_path))
            context = store.load_context()

            self.assertEqual(context.user_profile["language_preference"], "한국어")
            self.assertTrue(any(project.project_name == "Windows Jarvis AI Assistant" for project in context.project_statuses))

    def test_work_history_persists_after_reopening_store(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "memory.sqlite3"
            store = MemoryStore(db_path)
            store.initialize()
            store.record_work("local", "테스트 요청", "테스트 응답", "success")

            reopened = MemoryStore(db_path)
            reopened.initialize()
            context = reopened.load_context()

            self.assertEqual(reopened.counts()["work_history"], 1)
            self.assertEqual(context.recent_work[0].provider, "local")
            self.assertEqual(context.recent_work[0].prompt, "테스트 요청")

    def test_memory_status_contains_counts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = MemoryStore(Path(temp_dir) / "memory.sqlite3")
            store.initialize()
            store.remember_user_info("language_preference", "한국어")

            output = format_memory_status(store)

            self.assertIn("Jarvis 장기 기억 상태", output)
            self.assertIn("사용자 정보: 1개", output)


if __name__ == "__main__":
    unittest.main()
