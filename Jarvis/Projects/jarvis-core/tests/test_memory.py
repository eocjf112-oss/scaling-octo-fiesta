"""
Jarvis AI — 메모리 시스템 테스트
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_memory_manager_init():
    """MemoryManager 초기화 테스트"""
    from memory.memory_manager import MemoryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(Path(tmpdir))
        assert manager.memory_dir.exists()


def test_memory_set_get():
    """메모리 키-값 저장/조회 테스트"""
    from memory.memory_manager import MemoryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(Path(tmpdir))
        manager.set("test_key", "test_value")
        assert manager.get("test_key") == "test_value"
        assert manager.get("nonexistent", "default") == "default"


def test_memory_add_fact():
    """사실 기억 추가/조회 테스트"""
    from memory.memory_manager import MemoryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(Path(tmpdir))
        manager.add_fact("Python은 훌륭한 언어입니다", category="programming")

        facts = manager.get_facts(category="programming")
        assert len(facts) == 1
        assert "Python" in facts[0]["content"]


def test_memory_persistence():
    """메모리 파일 영속성 테스트"""
    from memory.memory_manager import MemoryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        manager1 = MemoryManager(path)
        manager1.set("persistent_key", "persistent_value")

        manager2 = MemoryManager(path)
        assert manager2.get("persistent_key") == "persistent_value"


def test_user_profile():
    """사용자 프로필 저장/조회 테스트"""
    from memory.memory_manager import MemoryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(Path(tmpdir))
        manager.set_user_profile(name="홍길동", timezone="Asia/Seoul")

        profile = manager.get_user_profile()
        assert profile["name"] == "홍길동"
        assert profile["timezone"] == "Asia/Seoul"


def test_context_summary():
    """컨텍스트 요약 생성 테스트"""
    from memory.memory_manager import MemoryManager

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MemoryManager(Path(tmpdir))
        manager.add_fact("중요한 사실 1")
        manager.set_user_profile(name="테스트 사용자")

        summary = manager.get_context_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0


def test_session_manager():
    """SessionManager 기본 기능 테스트"""
    from memory.session_manager import SessionManager

    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SessionManager(Path(tmpdir))
        session = sm.start_session()

        assert session.session_id.startswith("JARVIS-")
        assert session.is_active
        assert sm.is_active

        sm.record_message("claude", 500)
        assert session.message_count == 1
        assert session.total_tokens == 500

        ended = sm.end_session()
        assert ended is not None
        assert not ended.is_active
