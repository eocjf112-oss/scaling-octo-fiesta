"""
Jarvis AI Assistant — 설정 관리 모듈

.env 파일 및 환경 변수에서 설정을 로드하고 검증합니다.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# 프로젝트 루트 기준으로 .env 로드
_PROJECT_ROOT = Path(__file__).parent
_ENV_FILE = _PROJECT_ROOT / ".env"

if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)
else:
    load_dotenv()  # 환경 변수에서 직접 로드


# ─────────────────────────────────────────────
# 설정 모델
# ─────────────────────────────────────────────

class OpenAIConfig(BaseModel):
    api_key: str = Field(default="", description="OpenAI API 키")
    model: str = Field(default="gpt-4o", description="사용할 GPT 모델")
    max_tokens: int = Field(default=4096, ge=1, le=32768)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("sk-proj-xxx"))


class AnthropicConfig(BaseModel):
    api_key: str = Field(default="", description="Anthropic API 키")
    model: str = Field(default="claude-opus-4-5", description="사용할 Claude 모델")
    max_tokens: int = Field(default=4096, ge=1, le=32768)

    @classmethod
    def from_env(cls) -> "AnthropicConfig":
        return cls(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            model=os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5"),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("sk-ant-xxx"))


class InterpreterConfig(BaseModel):
    safe_mode: bool = Field(default=False)
    auto_run: bool = Field(default=False)
    model: str = Field(default="gpt-4o")
    offline: bool = Field(default=False)

    @classmethod
    def from_env(cls) -> "InterpreterConfig":
        return cls(
            safe_mode=os.getenv("INTERPRETER_SAFE_MODE", "false").lower() == "true",
            auto_run=os.getenv("INTERPRETER_AUTO_RUN", "false").lower() == "true",
            model=os.getenv("INTERPRETER_MODEL", "gpt-4o"),
            offline=os.getenv("INTERPRETER_OFFLINE", "false").lower() == "true",
        )


class JarvisConfig(BaseModel):
    """Jarvis 시스템 전체 설정"""

    language: str = Field(default="ko")
    default_provider: Literal["openai", "claude", "interpreter", "auto"] = Field(
        default="auto"
    )
    memory_path: Path = Field(default_factory=lambda: Path("../../Memory"))
    log_path: Path = Field(default_factory=lambda: Path("../../Logs"))
    log_level: str = Field(default="INFO")
    user_name: str = Field(default="사용자")
    user_timezone: str = Field(default="Asia/Seoul")
    max_context_messages: int = Field(default=20, ge=1, le=100)
    session_timeout_minutes: int = Field(default=60, ge=1)
    enable_voice: bool = Field(default=False)
    enable_auto_memory: bool = Field(default=True)
    debug_mode: bool = Field(default=False)

    openai: OpenAIConfig = Field(default_factory=OpenAIConfig.from_env)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig.from_env)
    interpreter: InterpreterConfig = Field(default_factory=InterpreterConfig.from_env)

    @classmethod
    def from_env(cls) -> "JarvisConfig":
        project_root = Path(__file__).parent
        memory_path = project_root / os.getenv("JARVIS_MEMORY_PATH", "../../Memory")
        log_path = project_root / os.getenv("JARVIS_LOG_PATH", "../../Logs")

        return cls(
            language=os.getenv("JARVIS_LANGUAGE", "ko"),
            default_provider=os.getenv("JARVIS_DEFAULT_PROVIDER", "auto"),  # type: ignore
            memory_path=memory_path.resolve(),
            log_path=log_path.resolve(),
            log_level=os.getenv("JARVIS_LOG_LEVEL", "INFO"),
            user_name=os.getenv("USER_NAME", "사용자"),
            user_timezone=os.getenv("USER_TIMEZONE", "Asia/Seoul"),
            max_context_messages=int(os.getenv("MAX_CONTEXT_MESSAGES", "20")),
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "60")),
            enable_voice=os.getenv("ENABLE_VOICE", "false").lower() == "true",
            enable_auto_memory=os.getenv("ENABLE_AUTO_MEMORY", "true").lower() == "true",
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            openai=OpenAIConfig.from_env(),
            anthropic=AnthropicConfig.from_env(),
            interpreter=InterpreterConfig.from_env(),
        )

    def get_available_providers(self) -> list[str]:
        """설정이 완료된 프로바이더 목록 반환"""
        available = []
        if self.openai.is_configured:
            available.append("openai")
        if self.anthropic.is_configured:
            available.append("claude")
        return available

    def get_best_provider(self) -> str:
        """가장 적합한 프로바이더 선택"""
        if self.default_provider != "auto":
            return self.default_provider

        available = self.get_available_providers()
        if "claude" in available:
            return "claude"
        if "openai" in available:
            return "openai"
        return "none"


# 싱글턴 설정 인스턴스
_config: JarvisConfig | None = None


def get_config() -> JarvisConfig:
    """전역 설정 인스턴스 반환 (싱글턴)"""
    global _config
    if _config is None:
        _config = JarvisConfig.from_env()
    return _config


def reload_config() -> JarvisConfig:
    """설정 강제 재로드"""
    global _config
    _config = None
    return get_config()
