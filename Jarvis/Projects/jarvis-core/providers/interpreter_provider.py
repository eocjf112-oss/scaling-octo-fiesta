"""
Jarvis AI — Open Interpreter 프로바이더

Open Interpreter를 통해 로컬 코드 실행, 파일 조작,
시스템 명령 등을 자연어로 처리합니다.

Windows 호환: PowerShell 및 cmd 지원
"""

from __future__ import annotations

import sys
from typing import Generator

from loguru import logger

from .base_provider import BaseProvider, Message, ProviderResponse


class InterpreterProvider(BaseProvider):
    """Open Interpreter 프로바이더"""

    name = "interpreter"
    display_name = "Open Interpreter"

    def __init__(
        self,
        llm_api_key: str = "",
        model: str = "gpt-4o",
        safe_mode: bool = False,
        auto_run: bool = False,
        offline: bool = False,
        system_prompt: str = "",
    ) -> None:
        super().__init__(system_prompt=system_prompt)
        self._llm_api_key = llm_api_key
        self.model = model
        self.safe_mode = safe_mode
        self.auto_run = auto_run
        self.offline = offline
        self._interpreter = None

    def _get_interpreter(self):
        """Open Interpreter 인스턴스 지연 초기화"""
        if self._interpreter is None:
            try:
                from interpreter import interpreter as oi

                oi.llm.model = self.model
                if self._llm_api_key:
                    oi.llm.api_key = self._llm_api_key

                oi.auto_run = self.auto_run
                oi.offline = self.offline

                if self.safe_mode:
                    oi.safe_mode = "auto"

                if self.system_prompt:
                    oi.system_message = self.system_prompt

                # Windows 호환성: 기본 언어 설정
                if sys.platform == "win32":
                    oi.computer.terminal.languages = ["powershell", "python", "javascript"]

                self._interpreter = oi
                logger.info("[Interpreter] Open Interpreter 초기화 완료")

            except ImportError:
                raise ImportError(
                    "open-interpreter 패키지가 설치되지 않았습니다. "
                    "'pip install open-interpreter' 를 실행하세요."
                )
        return self._interpreter

    def is_available(self) -> bool:
        try:
            import interpreter  # noqa: F401
            return True
        except ImportError:
            return False

    def chat(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> ProviderResponse:
        oi = self._get_interpreter()

        logger.info(f"[Interpreter] 실행 요청: {user_message[:100]}...")

        collected_output = []

        for chunk in oi.chat(user_message, display=False, stream=True):
            if isinstance(chunk, dict):
                chunk_type = chunk.get("type", "")
                content = chunk.get("content", "")
                if chunk_type == "message" and content:
                    collected_output.append(content)

        full_response = "".join(collected_output)

        self.add_message(Message.user(user_message))
        self.add_message(Message.assistant(full_response))

        return ProviderResponse(
            content=full_response,
            provider=self.name,
            model=self.model,
            finish_reason="complete",
        )

    def stream(
        self,
        user_message: str,
        system_override: str | None = None,
    ) -> Generator[str, None, None]:
        oi = self._get_interpreter()

        logger.info(f"[Interpreter] 스트리밍 실행: {user_message[:100]}...")

        full_content = ""
        in_code_block = False

        for chunk in oi.chat(user_message, display=False, stream=True):
            if not isinstance(chunk, dict):
                continue

            chunk_type = chunk.get("type", "")
            content = chunk.get("content", "")
            role = chunk.get("role", "")

            if chunk_type == "message" and role == "assistant" and content:
                full_content += content
                yield content

            elif chunk_type == "code" and content:
                if not in_code_block:
                    language = chunk.get("format", "python")
                    header = f"\n```{language}\n"
                    full_content += header
                    yield header
                    in_code_block = True
                full_content += content
                yield content

            elif chunk_type == "confirmation":
                in_code_block = False
                footer = "\n```\n"
                full_content += footer
                yield footer

            elif chunk_type == "console" and role == "computer" and content:
                result = f"\n**[실행 결과]**\n```\n{content}\n```\n"
                full_content += result
                yield result

        self.add_message(Message.user(user_message))
        self.add_message(Message.assistant(full_content))

    def reset(self) -> None:
        """대화 기록 초기화 (Interpreter 내부 기록 포함)"""
        super().reset()
        if self._interpreter is not None:
            self._interpreter.messages = []
        logger.debug("[Interpreter] 대화 기록 초기화")
