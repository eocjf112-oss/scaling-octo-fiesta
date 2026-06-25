"""
Jarvis AI — 세션 관리자

각 대화 세션의 생명주기를 추적하고 기록합니다.
세션 ID, 타임스탬프, 통계, 활성 프로바이더 등을 관리합니다.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from loguru import logger


@dataclass
class SessionRecord:
    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None
    provider_used: list[str] = field(default_factory=list)
    message_count: int = 0
    total_tokens: int = 0
    completed_tasks: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds()

    @property
    def is_active(self) -> bool:
        return self.ended_at is None

    def record_message(self, provider: str, tokens: int = 0) -> None:
        self.message_count += 1
        self.total_tokens += tokens
        if provider not in self.provider_used:
            self.provider_used.append(provider)

    def add_task(self, task: str) -> None:
        self.completed_tasks.append(task)

    def close(self) -> None:
        self.ended_at = datetime.now()


class SessionManager:
    """Jarvis 세션 생명주기 관리"""

    def __init__(self, log_dir: Path) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._sessions: list[SessionRecord] = []
        self._current: SessionRecord | None = None

    @property
    def current(self) -> SessionRecord | None:
        return self._current

    @property
    def is_active(self) -> bool:
        return self._current is not None and self._current.is_active

    def start_session(self) -> SessionRecord:
        """새 세션 시작"""
        session_id = f"JARVIS-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        session = SessionRecord(session_id=session_id)
        self._sessions.append(session)
        self._current = session
        logger.info(f"[Session] 세션 시작: {session_id}")
        return session

    def end_session(self) -> SessionRecord | None:
        """현재 세션 종료"""
        if not self._current:
            return None

        self._current.close()
        ended = self._current
        self._current = None

        self._save_session_log(ended)
        logger.info(
            f"[Session] 세션 종료: {ended.session_id} "
            f"({ended.duration_seconds:.0f}초, {ended.message_count}개 메시지)"
        )
        return ended

    def record_message(self, provider: str, tokens: int = 0) -> None:
        if self._current:
            self._current.record_message(provider, tokens)

    def add_completed_task(self, task: str) -> None:
        if self._current:
            self._current.add_task(task)

    def get_session_summary(self) -> str:
        """현재 세션 요약 문자열 반환"""
        if not self._current:
            return "활성 세션 없음"

        s = self._current
        duration = int(s.duration_seconds)
        providers = ", ".join(s.provider_used) if s.provider_used else "없음"
        return (
            f"세션 ID: {s.session_id}\n"
            f"경과 시간: {duration // 60}분 {duration % 60}초\n"
            f"메시지 수: {s.message_count}개\n"
            f"사용 토큰: {s.total_tokens:,}\n"
            f"사용 AI: {providers}"
        )

    def _save_session_log(self, session: SessionRecord) -> None:
        """세션 로그를 파일로 저장"""
        log_file = self.log_dir / f"session_{session.session_id}.log"
        lines = [
            f"=== Jarvis 세션 로그 ===",
            f"세션 ID: {session.session_id}",
            f"시작: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"종료: {session.ended_at.strftime('%Y-%m-%d %H:%M:%S') if session.ended_at else 'N/A'}",
            f"지속 시간: {int(session.duration_seconds)}초",
            f"메시지 수: {session.message_count}",
            f"총 토큰: {session.total_tokens:,}",
            f"사용 프로바이더: {', '.join(session.provider_used)}",
            "",
            "=== 완료 작업 ===",
            *[f"- {t}" for t in session.completed_tasks],
            "",
            "=== 메모 ===",
            *[f"- {n}" for n in session.notes],
        ]

        try:
            log_file.write_text("\n".join(lines), encoding="utf-8")
            logger.debug(f"[Session] 로그 저장: {log_file}")
        except Exception as e:
            logger.error(f"[Session] 로그 저장 실패: {e}")
