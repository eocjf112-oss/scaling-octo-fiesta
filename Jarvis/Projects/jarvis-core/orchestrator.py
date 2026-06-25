"""
Jarvis AI — 오케스트레이터

세 가지 AI 시스템(OpenAI, Claude, Open Interpreter)을 하나의
인터페이스로 통합하고, 요청 유형에 따라 최적의 AI로 라우팅합니다.

라우팅 전략:
  - 코드 실행 요청      → Open Interpreter
  - 창의적/장문 작업    → Claude
  - 일반 질문/분석      → 설정된 기본 프로바이더 (Claude 우선)
  - 명시적 프로바이더   → 해당 프로바이더로 직접 전달
"""

from __future__ import annotations

import re
from typing import Generator

from loguru import logger

from config import JarvisConfig, get_config
from memory.memory_manager import MemoryManager
from memory.session_manager import SessionManager
from providers.base_provider import BaseProvider, ProviderResponse
from providers.claude_provider import ClaudeProvider
from providers.openai_provider import OpenAIProvider
from providers.interpreter_provider import InterpreterProvider


# 코드 실행을 요청하는 키워드 패턴
_CODE_EXECUTION_PATTERNS = [
    r"실행\s*해",
    r"코드\s*를?\s*(써|작성|만들|실행)",
    r"파일\s*(만들|생성|삭제|이동|복사)",
    r"스크립트",
    r"명령\s*(어|줄|창|프롬프트)",
    r"터미널",
    r"powershell",
    r"cmd",
    r"bash",
    r"폴더\s*(만들|생성)",
    r"설치\s*해",
    r"run\s+",
    r"execute",
    r"install",
    r"create\s+file",
    r"delete\s+file",
]

_CODE_EXECUTION_RE = re.compile(
    "|".join(_CODE_EXECUTION_PATTERNS), re.IGNORECASE
)

# Jarvis 기본 시스템 프롬프트
JARVIS_SYSTEM_PROMPT = """당신은 Jarvis입니다. 개인 AI 엔지니어 겸 수석 보좌관입니다.

핵심 원칙:
- 한국어로 명확하고 친근하게 소통합니다
- 복잡한 문제를 체계적으로 분석하고 해결합니다
- 코드와 기술적 설명에서 정확성을 최우선으로 합니다
- 사용자의 요구사항을 완전히 파악한 후 작업을 시작합니다
- 중요한 결정은 사용자의 확인을 받고 진행합니다
- 최선의 방법을 제시하되, 대안도 함께 설명합니다

당신은 단순한 도구가 아니라, 사용자의 생각을 확장하고 행동을 가속화하는 AI 파트너입니다."""


class Orchestrator:
    """Jarvis AI 통합 오케스트레이터"""

    def __init__(self, config: JarvisConfig | None = None) -> None:
        self.config = config or get_config()
        self._providers: dict[str, BaseProvider] = {}
        self._memory: MemoryManager | None = None
        self._session: SessionManager | None = None
        self._initialized = False

    def initialize(self) -> None:
        """프로바이더 및 시스템 초기화"""
        if self._initialized:
            return

        logger.info("[Orchestrator] Jarvis 초기화 중...")

        # 메모리 시스템
        self._memory = MemoryManager(self.config.memory_path)
        self._session = SessionManager(self.config.log_path)
        self._session.start_session()

        # AI 프로바이더 초기화
        self._init_providers()
        self._initialized = True

        available = list(self._providers.keys())
        logger.info(f"[Orchestrator] 초기화 완료. 사용 가능한 프로바이더: {available}")

    def _init_providers(self) -> None:
        """설정에 따라 AI 프로바이더 초기화"""
        system_prompt = self._build_system_prompt()

        if self.config.openai.is_configured:
            self._providers["openai"] = OpenAIProvider(
                api_key=self.config.openai.api_key,
                model=self.config.openai.model,
                max_tokens=self.config.openai.max_tokens,
                temperature=self.config.openai.temperature,
                system_prompt=system_prompt,
            )
            logger.info(f"[Orchestrator] OpenAI 프로바이더 준비 ({self.config.openai.model})")

        if self.config.anthropic.is_configured:
            self._providers["claude"] = ClaudeProvider(
                api_key=self.config.anthropic.api_key,
                model=self.config.anthropic.model,
                max_tokens=self.config.anthropic.max_tokens,
                system_prompt=system_prompt,
            )
            logger.info(f"[Orchestrator] Claude 프로바이더 준비 ({self.config.anthropic.model})")

        # Open Interpreter — OpenAI 키로 동작
        interpreter_key = (
            self.config.openai.api_key if self.config.openai.is_configured
            else ""
        )
        self._providers["interpreter"] = InterpreterProvider(
            llm_api_key=interpreter_key,
            model=self.config.interpreter.model,
            safe_mode=self.config.interpreter.safe_mode,
            auto_run=self.config.interpreter.auto_run,
            offline=self.config.interpreter.offline,
            system_prompt=system_prompt,
        )
        logger.info("[Orchestrator] Open Interpreter 프로바이더 준비")

    def _build_system_prompt(self) -> str:
        """메모리 컨텍스트가 포함된 시스템 프롬프트 생성"""
        prompt = JARVIS_SYSTEM_PROMPT

        if self._memory:
            context = self._memory.get_context_summary()
            if context and context != "저장된 기억 없음":
                prompt += f"\n\n=== 장기 기억 (Memory) ===\n{context}"

        user_name = self.config.user_name
        if user_name and user_name != "사용자":
            prompt += f"\n\n사용자 이름: {user_name}"

        return prompt

    def _select_provider(self, message: str, explicit_provider: str | None = None) -> str:
        """메시지 분석 후 적절한 프로바이더 선택"""
        if explicit_provider and explicit_provider in self._providers:
            return explicit_provider

        # 코드 실행 요청 감지
        if _CODE_EXECUTION_RE.search(message):
            if "interpreter" in self._providers:
                logger.debug("[Router] 코드 실행 요청 → Open Interpreter")
                return "interpreter"

        # 기본 프로바이더 선택
        best = self.config.get_best_provider()
        if best in self._providers:
            return best

        # 사용 가능한 첫 번째 프로바이더
        available = [k for k in ["claude", "openai", "interpreter"] if k in self._providers]
        if available:
            return available[0]

        raise RuntimeError("사용 가능한 AI 프로바이더가 없습니다. .env 파일에 API 키를 설정하세요.")

    def chat(
        self,
        message: str,
        provider: str | None = None,
    ) -> ProviderResponse:
        """단일 응답 채팅"""
        if not self._initialized:
            self.initialize()

        selected = self._select_provider(message, provider)
        logger.info(f"[Orchestrator] '{selected}' 프로바이더로 전달")

        response = self._providers[selected].chat(message)

        if self._session:
            self._session.record_message(selected, response.total_tokens)

        if self.config.enable_auto_memory and self._memory:
            self._auto_save_memory(message, response.content)

        return response

    def stream(
        self,
        message: str,
        provider: str | None = None,
    ) -> tuple[str, Generator[str, None, None]]:
        """스트리밍 채팅. (선택된_프로바이더, 청크_제너레이터) 반환"""
        if not self._initialized:
            self.initialize()

        selected = self._select_provider(message, provider)
        logger.info(f"[Orchestrator] 스트리밍: '{selected}' 프로바이더로 전달")

        gen = self._providers[selected].stream(message)

        if self._session:
            self._session.record_message(selected, 0)

        return selected, gen

    def _auto_save_memory(self, user_msg: str, ai_response: str) -> None:
        """중요한 내용을 자동으로 메모리에 저장"""
        if not self._memory:
            return

        keywords = ["기억해", "저장해", "중요한", "잊지마", "remember", "note"]
        if any(kw in user_msg.lower() for kw in keywords):
            self._memory.add_fact(
                f"사용자 요청: {user_msg[:200]}",
                category="user_request",
            )

    def switch_provider(self, provider_name: str) -> bool:
        """기본 프로바이더 전환"""
        if provider_name not in self._providers:
            return False
        self.config.default_provider = provider_name  # type: ignore
        logger.info(f"[Orchestrator] 기본 프로바이더 변경: {provider_name}")
        return True

    def get_provider_status(self) -> dict[str, bool]:
        """모든 프로바이더 상태 반환"""
        if not self._initialized:
            self.initialize()
        return {name: prov.is_available() for name, prov in self._providers.items()}

    def reset_conversation(self, provider: str | None = None) -> None:
        """대화 기록 초기화"""
        if provider:
            if provider in self._providers:
                self._providers[provider].reset()
        else:
            for prov in self._providers.values():
                prov.reset()
        logger.info("[Orchestrator] 대화 기록 초기화")

    def get_session_info(self) -> str:
        """현재 세션 정보 반환"""
        if self._session:
            return self._session.get_session_summary()
        return "세션 정보 없음"

    def shutdown(self) -> None:
        """Jarvis 종료 처리"""
        if self._session:
            session = self._session.end_session()
            if session and self._memory:
                self._memory.append_to_memory_md(
                    f"세션 {session.session_id} 종료",
                    f"메시지: {session.message_count}개, 토큰: {session.total_tokens:,}",
                )
        logger.info("[Orchestrator] Jarvis 종료")
