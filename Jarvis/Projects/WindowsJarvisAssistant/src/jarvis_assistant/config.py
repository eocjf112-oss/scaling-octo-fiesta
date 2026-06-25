from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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
    workspace_root: Path = Path.cwd()
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"
    open_interpreter_command: str = "interpreter"
    open_interpreter_workdir: Path | None = None
    open_interpreter_timeout_seconds: int = 120
    open_interpreter_auto_yes: bool = False
    open_interpreter_require_confirmation: bool = True

    @classmethod
    def from_env(cls) -> "JarvisConfig":
        workspace_root = _get_path("JARVIS_WORKSPACE_ROOT") or _discover_workspace_root()
        return cls(
            default_provider=os.getenv("JARVIS_DEFAULT_PROVIDER", "chatgpt").strip() or "chatgpt",
            workspace_root=workspace_root,
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
            open_interpreter_workdir=(
                _get_path("JARVIS_OPEN_INTERPRETER_WORKDIR")
                or workspace_root / "Temp" / "OpenInterpreter"
            ),
            open_interpreter_timeout_seconds=_get_int("JARVIS_OPEN_INTERPRETER_TIMEOUT_SECONDS", 120),
            open_interpreter_auto_yes=_get_bool("JARVIS_OPEN_INTERPRETER_AUTO_YES", False),
            open_interpreter_require_confirmation=_get_bool(
                "JARVIS_OPEN_INTERPRETER_REQUIRE_CONFIRMATION", True
            ),
        )


def _get_path(name: str) -> Path | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return None
    return Path(value).expanduser().resolve()


def _discover_workspace_root() -> Path:
    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents]
    for candidate in candidates:
        if _looks_like_jarvis_workspace(candidate):
            return candidate
    for candidate in candidates:
        child = candidate / "Jarvis"
        if _looks_like_jarvis_workspace(child):
            return child
    return cwd


def _looks_like_jarvis_workspace(path: Path) -> bool:
    return (path / "MASTER_PROMPT.md").is_file() and (path / "MEMORY.md").is_file()
