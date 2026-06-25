"""
Jarvis AI 라우터
사용자 메시지를 분석하여 ChatGPT, Claude, Open Interpreter 중 최적의 AI를 선택합니다.
또한 체인 모드(여러 AI를 순서대로 사용)를 지원합니다.
"""
from typing import Iterator, Optional

from core.config import config
from core.logger import get_logger
from core.memory import memory_manager
from agents.openai_agent import OpenAIAgent
from agents.claude_agent import ClaudeAgent
from agents.interpreter_agent import InterpreterAgent

logger = get_logger("router")

# 에이전트 이름 매핑
AI_ALIASES = {
    "chatgpt": "chatgpt",
    "gpt": "chatgpt",
    "openai": "chatgpt",
    "claude": "claude",
    "anthropic": "claude",
    "interpreter": "interpreter",
    "코드": "interpreter",
    "실행": "interpreter",
    "auto": "auto",
    "자동": "auto",
}


class JarvisRouter:
    """
    세 AI를 통합 관리하는 메인 라우터.
    
    사용 방법:
        router = JarvisRouter()
        for chunk in router.chat("파이썬으로 Hello World 출력해줘"):
            print(chunk, end="", flush=True)
    """

    def __init__(self):
        self.chatgpt = OpenAIAgent()
        self.claude = ClaudeAgent()
        self.interpreter = InterpreterAgent()
        self._active_ai: str = config.default_ai
        logger.info(f"Jarvis 라우터 초기화 (기본 AI: {self._active_ai})")

    # ── 공개 API ─────────────────────────────────────────────

    def chat(
        self,
        user_message: str,
        force_ai: Optional[str] = None,
        stream: bool = True,
    ) -> tuple[str, Iterator[str]]:
        """
        메시지를 처리하고 (선택된 AI 이름, 응답 스트림)을 반환합니다.
        
        Args:
            user_message: 사용자 입력
            force_ai: 강제 AI 지정 ('chatgpt' | 'claude' | 'interpreter' | None)
            stream: 스트리밍 여부
            
        Returns:
            (ai_name, response_iterator) 튜플
        """
        # 슬래시 명령어에서 AI 강제 지정 처리
        message, inline_ai = self._parse_inline_command(user_message)
        selected_ai = force_ai or inline_ai or self._active_ai

        if selected_ai == "auto":
            selected_ai = self._route(message)

        agent = self._get_agent(selected_ai)
        if agent is None:
            return "error", iter([f"❌ '{selected_ai}' AI를 사용할 수 없습니다."])

        if not agent.is_available():
            fallback = self._find_available_fallback(selected_ai)
            if fallback:
                logger.warning(
                    f"{selected_ai} 사용 불가 → {fallback}으로 대체합니다."
                )
                selected_ai = fallback
                agent = self._get_agent(selected_ai)
            else:
                return "error", iter(["❌ 사용 가능한 AI가 없습니다. .env 파일에 API 키를 설정해주세요."])

        # 컨텍스트(메모리)를 시스템 프롬프트에 주입
        system_prompt = self._build_system_prompt(selected_ai)

        memory_manager.add_message("user", message, selected_ai)
        logger.info(f"라우팅: '{message[:50]}...' → {selected_ai}")

        return selected_ai, agent.chat(message, system_prompt=system_prompt, stream=stream)

    def set_active_ai(self, ai_name: str) -> bool:
        """기본 AI를 변경합니다. 성공 여부를 반환합니다."""
        normalized = AI_ALIASES.get(ai_name.lower(), ai_name.lower())
        valid = {"chatgpt", "claude", "interpreter", "auto"}
        if normalized not in valid:
            return False
        self._active_ai = normalized
        logger.info(f"기본 AI 변경: {normalized}")
        return True

    def get_active_ai(self) -> str:
        return self._active_ai

    def reset_all(self) -> None:
        """모든 AI의 대화 히스토리를 초기화합니다."""
        self.chatgpt.reset_history()
        self.claude.reset_history()
        self.interpreter.reset_history()
        logger.info("전체 대화 히스토리 초기화")

    def status(self) -> dict:
        """각 AI의 사용 가능 상태를 반환합니다."""
        return {
            "chatgpt": self.chatgpt.is_available(),
            "claude": self.claude.is_available(),
            "interpreter": self.interpreter.is_available(),
            "active": self._active_ai,
        }

    # ── 내부 로직 ────────────────────────────────────────────

    def _route(self, message: str) -> str:
        """
        메시지 내용을 분석하여 가장 적합한 AI를 선택합니다.
        config.yaml의 router.rules를 순서대로 확인합니다.
        """
        msg_lower = message.lower()

        for rule in config.router_rules:
            for keyword in rule.get("keywords", []):
                if keyword in msg_lower:
                    ai = rule.get("ai", config.router_default)
                    logger.debug(f"라우팅 규칙 매치: '{keyword}' → {ai}")
                    return ai

        default = config.router_default
        logger.debug(f"기본 라우팅 → {default}")
        return default

    def _parse_inline_command(self, message: str) -> tuple[str, Optional[str]]:
        """
        메시지 앞의 슬래시 명령어를 파싱합니다.
        예) "/claude 이 코드를 리뷰해줘" → ("이 코드를 리뷰해줘", "claude")
            "/gpt 아이디어 추천" → ("아이디어 추천", "chatgpt")
        """
        parts = message.strip().split(" ", 1)
        if parts[0].startswith("/") and len(parts[0]) > 1:
            cmd = parts[0][1:].lower()
            if cmd in AI_ALIASES:
                ai = AI_ALIASES[cmd]
                remaining = parts[1] if len(parts) > 1 else ""
                return remaining, ai
        return message, None

    def _get_agent(self, ai_name: str):
        """AI 이름으로 에이전트 인스턴스를 반환합니다."""
        return {
            "chatgpt": self.chatgpt,
            "claude": self.claude,
            "interpreter": self.interpreter,
        }.get(ai_name)

    def _find_available_fallback(self, failed_ai: str) -> Optional[str]:
        """사용 불가 AI의 대체 AI를 찾습니다."""
        priority = ["chatgpt", "claude", "interpreter"]
        for ai in priority:
            if ai != failed_ai and self._get_agent(ai).is_available():
                return ai
        return None

    def _build_system_prompt(self, ai_name: str) -> str:
        """메모리 컨텍스트를 포함한 시스템 프롬프트를 구성합니다."""
        base = config.system_prompt
        context = memory_manager.get_context_summary()

        if context:
            return f"{base}\n\n--- 기억 컨텍스트 ---\n{context}\n---"
        return base
