"""
Open Interpreter 에이전트
코드를 실제로 실행하고 파일/시스템을 조작합니다.
Windows 환경에서 Python, PowerShell, CMD를 실행할 수 있습니다.
"""
from typing import Iterator, Optional

from core.config import config
from core.logger import get_logger, log_conversation

logger = get_logger("interpreter_agent")


class InterpreterAgent:
    """Open Interpreter 에이전트 — 코드 실행 및 시스템 자동화"""

    name = "Interpreter"
    label = "🔵 Interpreter"

    def __init__(self):
        self._interpreter = None

    def _get_interpreter(self):
        """지연 초기화: 처음 사용 시 인터프리터를 설정합니다."""
        if self._interpreter is None:
            try:
                import interpreter as oi

                oi.llm.model = config.interpreter_model
                oi.llm.api_key = config.openai_api_key or ""
                oi.auto_run = config.interpreter_auto_run
                oi.safe_mode = config.interpreter_safe_mode

                # 시스템 프롬프트에 한국어 응답 지시 추가
                oi.system_message = (
                    config.system_prompt
                    + "\n\n코드를 실행하기 전에 무엇을 할 것인지 한국어로 설명하세요."
                    + "\n실행 결과도 한국어로 요약해 주세요."
                )

                self._interpreter = oi
                logger.info(
                    f"Open Interpreter 초기화 완료 "
                    f"(모델: {config.interpreter_model}, "
                    f"auto_run: {config.interpreter_auto_run})"
                )
            except ImportError:
                raise ImportError(
                    "open-interpreter 패키지를 설치해주세요: pip install open-interpreter"
                )
        return self._interpreter

    def is_available(self) -> bool:
        """Open Interpreter와 API 키 사용 가능 여부를 확인합니다."""
        try:
            import interpreter  # noqa: F401
            return bool(config.openai_api_key)
        except ImportError:
            return False

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        stream: bool = True,
    ) -> Iterator[str]:
        """
        Open Interpreter에 작업을 요청하고 실행 결과를 스트리밍으로 반환합니다.
        
        Args:
            user_message: 실행할 작업 설명
            system_prompt: 사용하지 않음 (Interpreter는 자체 시스템 프롬프트 사용)
            stream: True이면 청크 단위 출력
            
        Yields:
            실행 과정 및 결과 텍스트
        """
        interp = self._get_interpreter()
        log_conversation("user", user_message, "interpreter")

        full_response = ""
        try:
            for chunk in interp.chat(user_message, stream=True, display=False):
                chunk_type = chunk.get("type", "")
                content = chunk.get("content", "")

                if chunk_type == "message" and content:
                    full_response += content
                    yield content
                elif chunk_type == "code" and content:
                    code_block = f"\n```\n{content}\n```\n"
                    full_response += code_block
                    yield code_block
                elif chunk_type == "output" and content:
                    output_block = f"\n**실행 결과:**\n```\n{content}\n```\n"
                    full_response += output_block
                    yield output_block
                elif chunk_type == "error" and content:
                    error_block = f"\n❌ **오류:**\n```\n{content}\n```\n"
                    full_response += error_block
                    yield error_block

        except Exception as e:
            error_msg = f"Interpreter 오류: {e}"
            logger.error(error_msg)
            yield f"\n❌ {error_msg}"
            return

        log_conversation("assistant", full_response, "interpreter")

    def reset_history(self) -> None:
        """대화 히스토리를 초기화합니다."""
        if self._interpreter:
            self._interpreter.messages = []
        logger.info("Interpreter 대화 히스토리 초기화")
