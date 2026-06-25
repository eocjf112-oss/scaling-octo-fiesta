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


def _get_tuple(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    values = tuple(item.strip() for item in value.split(",") if item.strip())
    return values or default


@dataclass(frozen=True)
class JarvisConfig:
    default_provider: str = "local"
    provider_priority: tuple[str, ...] = (
        "windows_automation",
        "open_interpreter",
        "local",
        "chatgpt",
        "claude",
    )
    workspace_root: Path = Path.cwd()
    env_file: Path | None = None
    memory_db_path: Path | None = None
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
        env_file = load_env_file()
        workspace_root = _get_path("JARVIS_WORKSPACE_ROOT") or _discover_workspace_root()
        return cls(
            default_provider=os.getenv("JARVIS_DEFAULT_PROVIDER", "local").strip() or "local",
            provider_priority=_get_tuple(
                "JARVIS_PROVIDER_PRIORITY",
                ("windows_automation", "open_interpreter", "local", "chatgpt", "claude"),
            ),
            workspace_root=workspace_root,
            env_file=env_file,
            memory_db_path=_get_path("JARVIS_MEMORY_DB_PATH") or workspace_root / "Memory" / "jarvis_memory.sqlite3",
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


def load_env_file() -> Path | None:
    env_file = _find_env_file()
    if env_file is None:
        return None

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = _clean_env_value(value)

    return env_file


def _find_env_file() -> Path | None:
    explicit = _get_path("JARVIS_ENV_FILE")
    if explicit is not None:
        return explicit if explicit.is_file() else None

    project_root = Path(__file__).resolve().parents[2]
    candidates = (
        Path.cwd().resolve() / ".env",
        project_root / ".env",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _clean_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


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
