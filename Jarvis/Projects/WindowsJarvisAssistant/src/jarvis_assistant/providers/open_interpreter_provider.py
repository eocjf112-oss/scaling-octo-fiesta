from __future__ import annotations

import os
import shlex
import shutil
import subprocess

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.models import ChatRequest, ChatResponse, ProviderError


class OpenInterpreterProvider:
    name = "open_interpreter"

    def __init__(self, config: JarvisConfig):
        self._config = config

    def is_available(self) -> bool:
        command = self._command_parts()
        return bool(command and shutil.which(command[0]))

    def complete(self, request: ChatRequest) -> ChatResponse:
        command = self._command_parts()
        if not command:
            raise ProviderError("JARVIS_OPEN_INTERPRETER_COMMAND is empty.")
        if not shutil.which(command[0]):
            raise ProviderError(
                "Open Interpreter CLI was not found. Install it with: pip install open-interpreter"
            )

        args = [*command]
        if self._config.open_interpreter_auto_yes:
            args.append("--yes")
        args.extend(["--message", request.prompt])

        try:
            result = subprocess.run(
                args,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._config.open_interpreter_timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderError("Open Interpreter command timed out.") from exc

        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise ProviderError(stderr or "Open Interpreter command failed.")

        return ChatResponse(
            provider=self.name,
            content=result.stdout.strip(),
            metadata={"command": command[0]},
        )

    def _command_parts(self) -> list[str]:
        return shlex.split(self._config.open_interpreter_command, posix=os.name != "nt")
