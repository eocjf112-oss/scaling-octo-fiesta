"""
Jarvis 설정 관리 모듈
.env 파일과 config.yaml을 통합하여 단일 설정 객체로 제공
"""
import os
import sys
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv


def _find_root() -> Path:
    """프로젝트 루트 디렉토리를 찾습니다."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "config.yaml").exists():
            return current
        current = current.parent
    return Path(__file__).parent.parent


ROOT_DIR = _find_root()
load_dotenv(ROOT_DIR / ".env", override=False)


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class _Config:
    """환경변수 + config.yaml 통합 설정 클래스"""

    def __init__(self):
        self._yaml = _load_yaml(ROOT_DIR / "config.yaml")

    # ── OpenAI ──────────────────────────────────────────────
    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")

    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL") or self._get("ai.chatgpt.model", "gpt-4o")

    @property
    def openai_max_tokens(self) -> int:
        return int(os.getenv("OPENAI_MAX_TOKENS") or self._get("ai.chatgpt.max_tokens", 4096))

    @property
    def openai_temperature(self) -> float:
        return float(self._get("ai.chatgpt.temperature", 0.7))

    # ── Anthropic (Claude) ───────────────────────────────────
    @property
    def anthropic_api_key(self) -> Optional[str]:
        return os.getenv("ANTHROPIC_API_KEY")

    @property
    def anthropic_model(self) -> str:
        return os.getenv("ANTHROPIC_MODEL") or self._get(
            "ai.claude.model", "claude-3-5-sonnet-20241022"
        )

    @property
    def anthropic_max_tokens(self) -> int:
        return int(os.getenv("ANTHROPIC_MAX_TOKENS") or self._get("ai.claude.max_tokens", 8192))

    @property
    def anthropic_temperature(self) -> float:
        return float(self._get("ai.claude.temperature", 0.7))

    # ── Open Interpreter ────────────────────────────────────
    @property
    def interpreter_model(self) -> str:
        return os.getenv("INTERPRETER_MODEL") or self._get("ai.interpreter.model", "gpt-4o")

    @property
    def interpreter_auto_run(self) -> bool:
        return self._get("ai.interpreter.auto_run", False)

    @property
    def interpreter_safe_mode(self) -> str:
        return self._get("ai.interpreter.safe_mode", "ask")

    # ── Jarvis 시스템 ────────────────────────────────────────
    @property
    def default_ai(self) -> str:
        return os.getenv("JARVIS_DEFAULT_AI") or self._get("ai.default", "auto")

    @property
    def language(self) -> str:
        return os.getenv("JARVIS_LANGUAGE") or self._get("jarvis.language", "ko")

    @property
    def workspace(self) -> Path:
        raw = os.getenv("JARVIS_WORKSPACE") or self._get("jarvis.workspace", str(ROOT_DIR.parent.parent))
        return Path(raw)

    @property
    def log_level(self) -> str:
        return os.getenv("JARVIS_LOG_LEVEL") or self._get("logging.level", "INFO")

    @property
    def log_dir(self) -> Path:
        return self.workspace / self._get("logging.log_dir", "Logs")

    # ── 메모리 ───────────────────────────────────────────────
    @property
    def memory_auto_save(self) -> bool:
        val = os.getenv("JARVIS_MEMORY_AUTO_SAVE", "").lower()
        if val in ("true", "1"):
            return True
        if val in ("false", "0"):
            return False
        return bool(self._get("memory.auto_save", True))

    @property
    def memory_file(self) -> Path:
        return self.workspace / self._get("memory.memory_file", "MEMORY.md")

    @property
    def memory_max_sessions(self) -> int:
        return int(
            os.getenv("JARVIS_MEMORY_MAX_SESSIONS") or self._get("memory.max_sessions", 50)
        )

    # ── 라우터 ───────────────────────────────────────────────
    @property
    def router_rules(self) -> list[dict]:
        return self._get("router.rules", [])

    @property
    def router_default(self) -> str:
        return self._get("router.default", "chatgpt")

    # ── CLI ─────────────────────────────────────────────────
    @property
    def system_prompt(self) -> str:
        return self._get("system_prompt", "당신은 Jarvis, 개인 AI 어시스턴트입니다.")

    @property
    def cli_show_ai_label(self) -> bool:
        return bool(self._get("cli.show_ai_label", True))

    # ── 내부 유틸 ────────────────────────────────────────────
    def _get(self, dotted_key: str, default: Any = None) -> Any:
        """점(.) 구분자로 중첩 YAML 값을 가져옵니다."""
        parts = dotted_key.split(".")
        node = self._yaml
        for part in parts:
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node if node is not None else default

    def validate(self) -> list[str]:
        """필수 API 키 존재 여부를 확인하고 경고 목록을 반환합니다."""
        warnings = []
        if not self.openai_api_key:
            warnings.append("OPENAI_API_KEY 가 설정되지 않았습니다. ChatGPT를 사용할 수 없습니다.")
        if not self.anthropic_api_key:
            warnings.append("ANTHROPIC_API_KEY 가 설정되지 않았습니다. Claude를 사용할 수 없습니다.")
        return warnings


config = _Config()
