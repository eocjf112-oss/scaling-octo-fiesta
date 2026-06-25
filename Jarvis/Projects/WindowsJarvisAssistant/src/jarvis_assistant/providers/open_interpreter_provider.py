from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse, ProviderError
from jarvis_assistant.safety import OpenInterpreterSafetyPolicy


class OpenInterpreterProvider:
    name = "open_interpreter"

    def __init__(self, config: JarvisConfig):
        self._config = config
        self._safety_policy = OpenInterpreterSafetyPolicy(
            require_confirmation=config.open_interpreter_require_confirmation
        )

    def is_available(self) -> bool:
        command = self._command_parts()
        return bool(command and self._resolve_executable(command[0]))

    def complete(self, request: ChatRequest) -> ChatResponse:
        decision = self._safety_policy.evaluate(request)
        if not decision.allowed:
            if decision.requires_confirmation:
                raise ProviderError(
                    f"{decision.reason} 다시 실행하려면 --confirm-local-execution 옵션을 사용하세요."
                )
            raise ProviderError(decision.reason)

        command = self._command_parts()
        if not command:
            raise ProviderError("JARVIS_OPEN_INTERPRETER_COMMAND is empty.")
        executable = self._resolve_executable(command[0])
        if not executable:
            raise ProviderError(
                "Open Interpreter CLI was not found. Install it with: pip install open-interpreter"
            )

        workdir = self._safe_workdir()
        args = [executable, *command[1:], "--stdin", "--plain", "--disable_telemetry", "--safe_mode", "ask"]
        if request.system_prompt:
            args.extend(["--custom_instructions", request.system_prompt])
        if request.temperature is not None:
            args.extend(["--temperature", str(request.temperature)])
        if self._config.open_interpreter_auto_yes:
            args.append("--auto_run")

        try:
            result = subprocess.run(
                args,
                input=request.prompt,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._config.open_interpreter_timeout_seconds,
                cwd=workdir,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderError("Open Interpreter command timed out.") from exc

        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise ProviderError(stderr or "Open Interpreter command failed.")

        return ChatResponse(
            provider=self.name,
            content=result.stdout.strip(),
            metadata={
                "command": executable,
                "risk_level": decision.risk_level.value,
                "workdir": str(workdir),
            },
        )

    def _command_parts(self) -> list[str]:
        return shlex.split(self._config.open_interpreter_command, posix=os.name != "nt")

    def _resolve_executable(self, command_name: str) -> str | None:
        resolved = shutil.which(command_name)
        if resolved:
            return resolved

        candidate = Path(sys.executable).with_name(command_name)
        if candidate.is_file():
            return str(candidate)

        if os.name == "nt":
            windows_candidate = Path(sys.executable).with_name(f"{command_name}.exe")
            if windows_candidate.is_file():
                return str(windows_candidate)

        return None

    def _safe_workdir(self) -> Path:
        workspace_root = self._config.workspace_root.resolve()
        workdir = (self._config.open_interpreter_workdir or workspace_root / "Temp" / "OpenInterpreter").resolve()
        if workdir != workspace_root and not workdir.is_relative_to(workspace_root):
            raise ProviderError("Open Interpreter workdir must be inside JARVIS_WORKSPACE_ROOT.")
        workdir.mkdir(parents=True, exist_ok=True)
        return workdir
