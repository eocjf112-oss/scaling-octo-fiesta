"""
Claude (Anthropic) 에이전트
Claude 3.5 Sonnet과 대화하며 스트리밍 응답을 지원합니다.
긴 문서 분석, 깊은 추론, 코드 리뷰에 특화되어 있습니다.
"""
from typing import Iterator, Optional

from core.config import config
from core.logger import get_logger, log_conversation

logger = get_logger("claude_agent")


class ClaudeAgent:
    """Anthropic Claude 에이전트"""

    name = "Claude"
    label = "🟠 Claude"

    def __init__(self):
        self._client = None
        self._history: list[dict] = []

    def _get_client(self):
        """지연 초기화: 처음 사용 시 클라이언트를 생성합니다."""
        if self._client is None:
            try:
                import anthropic
                if not config.anthropic_api_key:
                    raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
                self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)
                logger.info(f"Anthropic 클라이언트 초기화 완료 (모델: {config.anthropic_model})")
            except ImportError:
                raise ImportError("anthropic 패키지를 설치해주세요: pip install anthropic")
        return self._client

    def is_available(self) -> bool:
        """API 키가 설정되어 있는지 확인합니다."""
        return bool(config.anthropic_api_key)

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        stream: bool = True,
    ) -> Iterator[str]:
        """
        Claude에 메시지를 보내고 응답을 스트리밍으로 반환합니다.
        
        Args:
            user_message: 사용자 메시지
            system_prompt: 시스템 프롬프트 (None이면 기본값 사용)
            stream: True이면 토큰 단위 스트리밍
            
        Yields:
            응답 텍스트 청크
        """
        client = self._get_client()
        sys_prompt = system_prompt or config.system_prompt

        messages = list(self._history)
        messages.append({"role": "user", "content": user_message})

        log_conversation("user", user_message, "claude")
        logger.debug(f"Claude 요청: {user_message[:100]}...")

        full_response = ""
        try:
            if stream:
                with client.messages.stream(
                    model=config.anthropic_model,
                    max_tokens=config.anthropic_max_tokens,
                    system=sys_prompt,
                    messages=messages,
                ) as stream_response:
                    for text in stream_response.text_stream:
                        full_response += text
                        yield text
            else:
                response = client.messages.create(
                    model=config.anthropic_model,
                    max_tokens=config.anthropic_max_tokens,
                    system=sys_prompt,
                    messages=messages,
                )
                full_response = response.content[0].text
                yield full_response

        except Exception as e:
            error_msg = f"Claude 오류: {e}"
            logger.error(error_msg)
            yield f"\n❌ {error_msg}"
            return

        self._history.append({"role": "user", "content": user_message})
        self._history.append({"role": "assistant", "content": full_response})
        log_conversation("assistant", full_response, "claude")
        self._trim_history()

    def reset_history(self) -> None:
        """대화 히스토리를 초기화합니다."""
        self._history.clear()
        logger.info("Claude 대화 히스토리 초기화")

    def _trim_history(self, max_pairs: int = 15) -> None:
        """토큰 절약을 위해 오래된 대화 기록을 제거합니다."""
        if len(self._history) > max_pairs * 2:
            self._history = self._history[-(max_pairs * 2):]
