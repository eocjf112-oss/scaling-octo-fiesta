"""
Jarvis AI — 메모리 관리자

MEMORY.md 파일과 JSON 스토어를 통해 Jarvis의 장기 기억을 관리합니다.
새로운 세션에서도 이전 컨텍스트를 유지할 수 있도록 지원합니다.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


MEMORY_JSON = "jarvis_memory.json"


class MemoryManager:
    """Jarvis 장기 기억 관리자"""

    def __init__(self, memory_dir: Path) -> None:
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self._json_path = self.memory_dir / MEMORY_JSON
        self._md_path = self.memory_dir.parent.parent / "MEMORY.md"

        self._store: dict[str, Any] = self._load_json()
        logger.debug(f"[Memory] 메모리 디렉토리: {self.memory_dir}")

    # ──────────────────────────────────────────────
    # JSON 스토어 (구조화된 데이터)
    # ──────────────────────────────────────────────

    def _load_json(self) -> dict[str, Any]:
        if self._json_path.exists():
            try:
                return json.loads(self._json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.warning("[Memory] JSON 파일 손상, 초기화합니다.")
        return {
            "user_profile": {},
            "facts": [],
            "preferences": {},
            "projects": {},
            "notes": [],
            "last_updated": None,
        }

    def _save_json(self) -> None:
        self._store["last_updated"] = datetime.now().isoformat()
        self._json_path.write_text(
            json.dumps(self._store, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.debug("[Memory] JSON 저장 완료")

    def set(self, key: str, value: Any) -> None:
        """키-값 메모리 저장"""
        self._store[key] = value
        self._save_json()

    def get(self, key: str, default: Any = None) -> Any:
        """키로 메모리 조회"""
        return self._store.get(key, default)

    def add_fact(self, fact: str, category: str = "general") -> None:
        """중요 사실 기억 추가"""
        entry = {
            "content": fact,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        facts = self._store.setdefault("facts", [])
        facts.append(entry)
        if len(facts) > 200:
            facts.pop(0)
        self._save_json()
        logger.info(f"[Memory] 사실 기억: {fact[:60]}...")

    def add_note(self, note: str, tags: list[str] | None = None) -> None:
        """메모 추가"""
        entry = {
            "content": note,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
        }
        notes = self._store.setdefault("notes", [])
        notes.append(entry)
        self._save_json()

    def get_facts(self, category: str | None = None, limit: int = 10) -> list[dict]:
        """저장된 사실 목록 반환"""
        facts = self._store.get("facts", [])
        if category:
            facts = [f for f in facts if f.get("category") == category]
        return facts[-limit:]

    def set_user_profile(self, **kwargs) -> None:
        """사용자 프로필 업데이트"""
        profile = self._store.setdefault("user_profile", {})
        profile.update(kwargs)
        self._save_json()

    def get_user_profile(self) -> dict:
        return self._store.get("user_profile", {})

    def set_preference(self, key: str, value: Any) -> None:
        """사용자 선호도 저장"""
        prefs = self._store.setdefault("preferences", {})
        prefs[key] = value
        self._save_json()

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self._store.get("preferences", {}).get(key, default)

    def update_project(self, project_name: str, status: str, notes: str = "") -> None:
        """프로젝트 상태 업데이트"""
        projects = self._store.setdefault("projects", {})
        projects[project_name] = {
            "status": status,
            "notes": notes,
            "updated": datetime.now().isoformat(),
        }
        self._save_json()

    def get_context_summary(self) -> str:
        """현재 메모리 상태 요약 (AI 컨텍스트 주입용)"""
        parts = []

        profile = self.get_user_profile()
        if profile:
            profile_str = ", ".join(f"{k}: {v}" for k, v in profile.items())
            parts.append(f"사용자 프로필: {profile_str}")

        facts = self.get_facts(limit=5)
        if facts:
            fact_strs = [f["content"] for f in facts]
            parts.append("최근 기억:\n" + "\n".join(f"- {f}" for f in fact_strs))

        projects = self._store.get("projects", {})
        if projects:
            proj_strs = [
                f"{name}: {info['status']}"
                for name, info in list(projects.items())[-3:]
            ]
            parts.append("프로젝트 현황:\n" + "\n".join(f"- {p}" for p in proj_strs))

        return "\n\n".join(parts) if parts else "저장된 기억 없음"

    # ──────────────────────────────────────────────
    # MEMORY.md 동기화
    # ──────────────────────────────────────────────

    def append_to_memory_md(self, section: str, content: str) -> None:
        """MEMORY.md에 새로운 기록 추가"""
        if not self._md_path.exists():
            logger.warning(f"[Memory] MEMORY.md를 찾을 수 없습니다: {self._md_path}")
            return

        timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        entry = f"\n### [{timestamp}] — {section}\n{content}\n"

        with open(self._md_path, "a", encoding="utf-8") as f:
            f.write(entry)

        logger.debug(f"[Memory] MEMORY.md 업데이트: {section}")

    def update_session_in_md(
        self, session_id: str, goals: list[str], completed: list[str], learned: list[str]
    ) -> None:
        """세션 기록을 MEMORY.md에 추가"""
        now = datetime.now().strftime("%Y년 %m월 %d일")
        goals_str = "\n".join(f"- {g}" for g in goals)
        completed_str = "\n".join(f"- {c}" for c in completed)
        learned_str = "\n".join(f"- {l}" for l in learned)

        content = (
            f"**목표:** {goals_str}\n\n"
            f"**완료 작업:**\n{completed_str}\n\n"
            f"**학습 내용:**\n{learned_str}"
        )

        self.append_to_memory_md(f"세션 {session_id} — {now}", content)
