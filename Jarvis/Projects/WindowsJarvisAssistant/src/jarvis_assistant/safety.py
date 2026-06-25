from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from jarvis_assistant.models import ChatRequest


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    requires_confirmation: bool
    risk_level: RiskLevel
    reason: str


class OpenInterpreterSafetyPolicy:
    """Open Interpreter 실행 전 Jarvis가 적용하는 최소 안전 정책입니다."""

    BLOCKED_KEYWORDS = (
        "rm -rf /",
        "format c:",
        "format disk",
        "diskpart",
        "delete system32",
        "shutdown /s",
        "shutdown /r",
        "bcdedit",
        "cipher /w",
        "factory reset",
        "wipe disk",
        "시스템32 삭제",
        "디스크 포맷",
        "시스템 초기화",
        "공장 초기화",
    )
    CONFIRMATION_KEYWORDS = (
        "delete",
        "remove",
        "install",
        "uninstall",
        "modify",
        "write",
        "execute",
        "run",
        "powershell",
        "cmd",
        "registry",
        "file",
        "folder",
        "directory",
        "삭제",
        "제거",
        "설치",
        "수정",
        "변경",
        "쓰기",
        "실행",
        "명령",
        "파일",
        "폴더",
        "디렉터리",
        "레지스트리",
    )

    def __init__(self, require_confirmation: bool = True):
        self._require_confirmation = require_confirmation

    def evaluate(self, request: ChatRequest) -> SafetyDecision:
        prompt = request.prompt.lower()
        if any(keyword in prompt for keyword in self.BLOCKED_KEYWORDS):
            return SafetyDecision(
                allowed=False,
                requires_confirmation=False,
                risk_level=RiskLevel.BLOCKED,
                reason="시스템 손상 가능성이 있는 요청은 Jarvis 안전 정책에 의해 차단되었습니다.",
            )

        needs_confirmation = any(keyword in prompt for keyword in self.CONFIRMATION_KEYWORDS)
        confirmed = bool(request.metadata.get("confirm_local_execution"))
        if self._require_confirmation and needs_confirmation and not confirmed:
            return SafetyDecision(
                allowed=False,
                requires_confirmation=True,
                risk_level=RiskLevel.MEDIUM,
                reason="로컬 파일/명령 실행 성격의 요청은 명시적 확인이 필요합니다.",
            )

        if needs_confirmation:
            return SafetyDecision(
                allowed=True,
                requires_confirmation=False,
                risk_level=RiskLevel.MEDIUM,
                reason="사용자가 로컬 실행을 명시적으로 확인했습니다.",
            )

        return SafetyDecision(
            allowed=True,
            requires_confirmation=False,
            risk_level=RiskLevel.LOW,
            reason="읽기 또는 일반 분석 성격의 요청으로 판단되었습니다.",
        )
