"""
ChatGPT (OpenAI) 에이전트
GPT-4o와 대화하며 스트리밍 응답을 지원합니다.
"""
from typing import Generator, Iterator, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import config
from core.logger import get_logger, log_conversation

logger = get_logger("openai_agent")


class OpenAIAgent:
    """OpenAI GPT 에이전트"""

    name = "ChatGPT"
    label = "🟢 ChatGPT"

    def __init__(self):
        self._client = None
        self._history: list[dict] = []

    def _get_client(self):
        """지연 초기화: 처음 사용 시 클라이언트를 생성합니다."""
        if self._client is None:
            try:
                import openai
                if not config.openai_api_key:
                    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
                self._client = openai.OpenAI(api_key=config.openai_api_key)
                logger.info(f"OpenAI 클라이언트 초기화 완료 (모델: {config.openai_model})")
            except ImportError:
                raise ImportError("openai 패키지를 설치해주세요: pip install openai")
        return self._client

    def is_available(self) -> bool:
        """API 키가 설정되어 있는지 확인합니다."""
        return bool(config.openai_api_key)

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        stream: bool = True,
    ) -> Iterator[str]:
        """
        ChatGPT에 메시지를 보내고 응답을 스트리밍으로 반환합니다.
        
        Args:
            user_message: 사용자 메시지
            system_prompt: 시스템 프롬프트 (None이면 기본값 사용)
            stream: True이면 토큰 단위 스트리밍
            
        Yields:
            응답 텍스트 청크
        """
        client = self._get_client()
        sys_prompt = system_prompt or config.system_prompt

        messages = [{"role": "system", "content": sys_prompt}]
        messages.extend(self._history)
        messages.append({"role": "user", "content": user_message})

        log_conversation("user", user_message, "chatgpt")
        logger.debug(f"ChatGPT 요청: {user_message[:100]}...")

        full_response = ""
        try:
            response = client.chat.completions.create(
                model=config.openai_model,
                messages=messages,
                max_tokens=config.openai_max_tokens,
                temperature=config.openai_temperature,
                stream=stream,
            )

            if stream:
                for chunk in response:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta
                        yield delta
            else:
                full_response = response.choices[0].message.content
                yield full_response

        except Exception as e:
            error_msg = f"ChatGPT 오류: {e}"
            logger.error(error_msg)
            yield f"\n❌ {error_msg}"
            return

        self._history.append({"role": "user", "content": user_message})
        self._history.append({"role": "assistant", "content": full_response})
        log_conversation("assistant", full_response, "chatgpt")
        self._trim_history()

    def reset_history(self) -> None:
        """대화 히스토리를 초기화합니다."""
        self._history.clear()
        logger.info("ChatGPT 대화 히스토리 초기화")

    def _trim_history(self, max_pairs: int = 20) -> None:
        """토큰 절약을 위해 오래된 대화 기록을 제거합니다."""
        if len(self._history) > max_pairs * 2:
            self._history = self._history[-(max_pairs * 2):]
