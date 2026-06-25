from __future__ import annotations

import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc


@dataclass(frozen=True)
class JarvisConfig:
    default_provider: str = "chatgpt"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"
    open_interpreter_command: str = "interpreter"
    open_interpreter_timeout_seconds: int = 120
    open_interpreter_auto_yes: bool = False

    @classmethod
    def from_env(cls) -> "JarvisConfig":
        return cls(
            default_provider=os.getenv("JARVIS_DEFAULT_PROVIDER", "chatgpt").strip() or "chatgpt",
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("JARVIS_OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
            anthropic_model=(
                os.getenv("JARVIS_ANTHROPIC_MODEL", "claude-3-5-sonnet-latest").strip()
                or "claude-3-5-sonnet-latest"
            ),
            open_interpreter_command=(
                os.getenv("JARVIS_OPEN_INTERPRETER_COMMAND", "interpreter").strip() or "interpreter"
            ),
            open_interpreter_timeout_seconds=_get_int("JARVIS_OPEN_INTERPRETER_TIMEOUT_SECONDS", 120),
            open_interpreter_auto_yes=_get_bool("JARVIS_OPEN_INTERPRETER_AUTO_YES", False),
        )
