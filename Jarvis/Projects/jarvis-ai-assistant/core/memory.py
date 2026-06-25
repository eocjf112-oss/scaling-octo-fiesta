"""
Jarvis 메모리 시스템
MEMORY.md 파일을 읽고 쓰며 AI의 장기 기억을 유지합니다.
세션 기록, 사용자 선호도, 컨텍스트를 지속적으로 관리합니다.
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.config import config
from core.logger import get_logger

logger = get_logger("memory")


class MemoryManager:
    """MEMORY.md 기반 장기 기억 관리자"""

    def __init__(self, memory_path: Optional[Path] = None):
        self.memory_path = memory_path or config.memory_file
        self._session_counter = self._get_next_session_counter()
        self._current_session_id = self._generate_session_id()
        self._session_messages: list[dict] = []
        self._turn_count = 0

    # ── 읽기 ────────────────────────────────────────────────

    def read(self) -> str:
        """MEMORY.md 전체 내용을 읽어 반환합니다."""
        if not self.memory_path.exists():
            logger.warning(f"MEMORY.md 파일을 찾을 수 없습니다: {self.memory_path}")
            return ""
        return self.memory_path.read_text(encoding="utf-8")

    def get_context_summary(self) -> str:
        """현재 기억에서 AI에게 전달할 컨텍스트 요약을 추출합니다."""
        content = self.read()
        if not content:
            return ""

        sections = []

        # 사용자 프로필 섹션 추출
        profile = self._extract_section(content, "사용자 프로필")
        if profile:
            sections.append(f"[사용자 프로필]\n{profile.strip()}")

        # 학습된 선호도 섹션 추출
        prefs = self._extract_section(content, "학습된 선호도")
        if prefs:
            sections.append(f"[사용자 선호도]\n{prefs.strip()}")

        # 현재 진행 중인 프로젝트 추출
        projects = self._extract_section(content, "프로젝트 현황")
        if projects:
            sections.append(f"[현재 프로젝트]\n{projects.strip()}")

        # 최근 세션 기록 (마지막 3개)
        recent = self._extract_recent_sessions(content, n=3)
        if recent:
            sections.append(f"[최근 세션 요약]\n{recent.strip()}")

        return "\n\n".join(sections)

    # ── 쓰기 ────────────────────────────────────────────────

    def add_message(self, role: str, content: str, ai: str = "") -> None:
        """현재 세션에 메시지를 추가합니다."""
        self._session_messages.append({
            "role": role,
            "content": content,
            "ai": ai,
            "time": datetime.now().strftime("%H:%M"),
        })
        self._turn_count += 1

        if config.memory_auto_save and self._turn_count % 10 == 0:
            self.save_session()

    def save_session(self, summary: str = "", learned: str = "") -> None:
        """현재 세션을 MEMORY.md에 기록합니다."""
        if not self._session_messages:
            return

        today = datetime.now().strftime("%Y년 %m월 %d일")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 세션 요약 자동 생성
        if not summary:
            user_msgs = [m["content"] for m in self._session_messages if m["role"] == "user"]
            summary = f"총 {len(self._session_messages)}개 메시지 교환"
            if user_msgs:
                first = user_msgs[0][:60].replace("\n", " ")
                summary += f" | 첫 질문: \"{first}...\""

        # 사용한 AI 목록
        used_ais = list({m["ai"] for m in self._session_messages if m.get("ai")})
        ai_label = ", ".join(used_ais) if used_ais else "미지정"

        session_block = f"""
### {self._current_session_id} — {today}
**요약:** {summary}  
**사용 AI:** {ai_label}  
**메시지 수:** {len(self._session_messages)}개  
**기록 시간:** {now}
"""
        if learned:
            session_block += f"**학습 내용:** {learned}\n"

        self._append_to_section("세션 기록", session_block)
        self._update_last_modified()
        logger.info(f"세션 저장 완료: {self._current_session_id}")

    def update_profile(self, key: str, value: str) -> None:
        """사용자 프로필 항목을 업데이트합니다."""
        content = self.read()
        if not content:
            return

        pattern = rf"({re.escape(key)}:\s*)\[.*?\]"
        replacement = rf"\g<1>{value}"
        new_content = re.sub(pattern, replacement, content)

        if new_content != content:
            self.memory_path.write_text(new_content, encoding="utf-8")
            logger.info(f"프로필 업데이트: {key} = {value}")

    def add_note(self, note: str, tag: str = "") -> None:
        """메모 및 아이디어 섹션에 새 항목을 추가합니다."""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        tag_str = f" `{tag}`" if tag else ""
        note_entry = f"\n### {today} — 메모{tag_str}\n**내용:** {note}\n"
        self._append_to_section("메모 및 아이디어", note_entry)

    # ── 내부 유틸 ────────────────────────────────────────────

    def _extract_section(self, content: str, section_name: str) -> str:
        """마크다운에서 특정 섹션의 내용을 추출합니다."""
        pattern = rf"## [^\n]*{re.escape(section_name)}[^\n]*\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else ""

    def _extract_recent_sessions(self, content: str, n: int = 3) -> str:
        """최근 N개 세션 항목을 추출합니다."""
        section = self._extract_section(content, "세션 기록")
        if not section:
            return ""
        blocks = re.split(r"\n(?=### )", section.strip())
        recent = blocks[-n:] if len(blocks) >= n else blocks
        return "\n".join(recent)

    def _append_to_section(self, section_name: str, text: str) -> None:
        """특정 섹션의 끝에 텍스트를 추가합니다."""
        content = self.read()
        if not content:
            return

        pattern = rf"(## [^\n]*{re.escape(section_name)}[^\n]*\n)(.*?)((?=\n---\n)|\Z)"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            updated = (
                content[: match.start()]
                + match.group(1)
                + match.group(2)
                + text
                + content[match.end():]
            )
        else:
            updated = content + f"\n\n## 🗓️ {section_name}\n{text}"

        self.memory_path.write_text(updated, encoding="utf-8")

    def _update_last_modified(self) -> None:
        """마지막 업데이트 날짜를 현재 날짜로 갱신합니다."""
        content = self.read()
        today = datetime.now().strftime("%Y년 %m월 %d일")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        content = re.sub(
            r"\*\*날짜:\*\* .*",
            f"**날짜:** {today}",
            content,
        )
        self.memory_path.write_text(content, encoding="utf-8")

    def _get_next_session_counter(self) -> int:
        """기존 세션 기록을 분석하여 다음 세션 번호를 결정합니다."""
        content = self.read()
        if not content:
            return 1
        matches = re.findall(r"JARVIS-\d{8}-(\d{3})", content)
        if not matches:
            return 1
        return max(int(m) for m in matches) + 1

    def _generate_session_id(self) -> str:
        date_str = datetime.now().strftime("%Y%m%d")
        return f"JARVIS-{date_str}-{self._session_counter:03d}"

    @property
    def session_id(self) -> str:
        return self._current_session_id


memory_manager = MemoryManager()
