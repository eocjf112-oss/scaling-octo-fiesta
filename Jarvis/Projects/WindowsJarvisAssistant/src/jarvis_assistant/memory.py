from __future__ import annotations

import json
import platform
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jarvis_assistant.config import JarvisConfig


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class WorkHistoryItem:
    timestamp: str
    provider: str
    prompt: str
    status: str


@dataclass(frozen=True)
class ProjectStatus:
    project_name: str
    status: str
    summary: str
    updated_at: str


@dataclass(frozen=True)
class MemoryContext:
    user_profile: dict[str, str]
    project_statuses: list[ProjectStatus]
    recent_work: list[WorkHistoryItem]


class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    @classmethod
    def from_config(cls, config: JarvisConfig) -> "MemoryStore":
        if config.memory_db_path is None:
            return cls(config.workspace_root / "Memory" / "jarvis_memory.sqlite3")
        return cls(config.memory_db_path)

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    source TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS project_status (
                    project_name TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS work_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response_preview TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error TEXT,
                    metadata_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS memory_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                """
            )
            self._upsert_metadata(connection, "schema_version", str(SCHEMA_VERSION))

    def bootstrap_defaults(self, config: JarvisConfig) -> None:
        self.remember_user_info("language_preference", "한국어", "default")
        self.remember_user_info("communication_style", "구조화된 한국어 설명", "default")
        self.remember_user_info("workspace_root", str(config.workspace_root), "runtime")
        self.remember_user_info("operating_system", platform.platform(), "runtime")
        self.record_project_progress(
            "Windows Jarvis AI Assistant",
            "진행 중",
            "API 없이 Open Interpreter, Windows 자동화, 음성 입출력 준비를 중심으로 구축 중",
        )

    def remember_user_info(self, key: str, value: str, source: str = "runtime") -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_profile (key, value, source, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (key, value, source, _now()),
            )

    def record_project_progress(self, project_name: str, status: str, summary: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO project_status (project_name, status, summary, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_name) DO UPDATE SET
                    status = excluded.status,
                    summary = excluded.summary,
                    updated_at = excluded.updated_at
                """,
                (project_name, status, summary, _now()),
            )

    def record_work(
        self,
        provider: str,
        prompt: str,
        response_preview: str,
        status: str,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO work_history
                    (timestamp, provider, prompt, response_preview, status, error, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _now(),
                    provider,
                    _truncate(prompt, 2000),
                    _truncate(response_preview, 2000),
                    status,
                    error,
                    json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
                ),
            )

    def record_event(
        self,
        event_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memory_events (timestamp, event_type, content, metadata_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    _now(),
                    event_type,
                    _truncate(content, 2000),
                    json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
                ),
            )

    def load_context(self, recent_limit: int = 5) -> MemoryContext:
        with self._connect() as connection:
            profile_rows = connection.execute(
                "SELECT key, value FROM user_profile ORDER BY key"
            ).fetchall()
            project_rows = connection.execute(
                """
                SELECT project_name, status, summary, updated_at
                FROM project_status
                ORDER BY updated_at DESC
                """
            ).fetchall()
            work_rows = connection.execute(
                """
                SELECT timestamp, provider, prompt, status
                FROM work_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (recent_limit,),
            ).fetchall()

        return MemoryContext(
            user_profile={row["key"]: row["value"] for row in profile_rows},
            project_statuses=[
                ProjectStatus(
                    project_name=row["project_name"],
                    status=row["status"],
                    summary=row["summary"],
                    updated_at=row["updated_at"],
                )
                for row in project_rows
            ],
            recent_work=[
                WorkHistoryItem(
                    timestamp=row["timestamp"],
                    provider=row["provider"],
                    prompt=row["prompt"],
                    status=row["status"],
                )
                for row in work_rows
            ],
        )

    def counts(self) -> dict[str, int]:
        with self._connect() as connection:
            return {
                "user_profile": self._count(connection, "user_profile"),
                "project_status": self._count(connection, "project_status"),
                "work_history": self._count(connection, "work_history"),
                "memory_events": self._count(connection, "memory_events"),
            }

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _upsert_metadata(self, connection: sqlite3.Connection, key: str, value: str) -> None:
        connection.execute(
            """
            INSERT INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (key, value, _now()),
        )

    def _count(self, connection: sqlite3.Connection, table_name: str) -> int:
        row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
        return int(row["count"])


def format_memory_status(store: MemoryStore) -> str:
    context = store.load_context()
    counts = store.counts()
    lines = [
        "Jarvis 장기 기억 상태",
        f"- DB 경로: {store.db_path}",
        f"- 사용자 정보: {counts['user_profile']}개",
        f"- 프로젝트 상태: {counts['project_status']}개",
        f"- 작업 기록: {counts['work_history']}개",
        f"- 메모리 이벤트: {counts['memory_events']}개",
    ]

    if context.project_statuses:
        lines.append("")
        lines.append("최근 프로젝트 상태:")
        for project in context.project_statuses[:3]:
            lines.append(f"- {project.project_name}: {project.status} - {project.summary}")

    if context.recent_work:
        lines.append("")
        lines.append("최근 작업 기록:")
        for item in context.recent_work[:3]:
            lines.append(f"- {item.timestamp} [{item.provider}/{item.status}] {item.prompt}")

    return "\n".join(lines)


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 3]}..."
