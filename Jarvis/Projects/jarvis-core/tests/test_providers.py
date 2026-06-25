"""
Jarvis AI — AI 프로바이더 테스트

실제 API 호출 없이 프로바이더 구조와 인터페이스를 검증합니다.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_message_creation():
    """Message 데이터 클래스 생성 테스트"""
    from providers.base_provider import Message, MessageRole

    msg = Message.user("안녕하세요")
    assert msg.role == MessageRole.USER
    assert msg.content == "안녕하세요"

    system_msg = Message.system("시스템 메시지")
    assert system_msg.role == MessageRole.SYSTEM

    ai_msg = Message.assistant("응답입니다")
    assert ai_msg.role == MessageRole.ASSISTANT


def test_message_to_dict():
    """Message → dict 변환 테스트"""
    from providers.base_provider import Message

    msg = Message.user("테스트")
    d = msg.to_dict()
    assert d == {"role": "user", "content": "테스트"}


def test_provider_response():
    """ProviderResponse 토큰 합산 테스트"""
    from providers.base_provider import ProviderResponse

    resp = ProviderResponse(
        content="응답",
        provider="test",
        model="test-model",
        input_tokens=100,
        output_tokens=50,
    )
    assert resp.total_tokens == 150


def test_openai_provider_init():
    """OpenAI 프로바이더 초기화 테스트 (API 호출 없음)"""
    from providers.openai_provider import OpenAIProvider

    provider = OpenAIProvider(api_key="test-key", model="gpt-4o")
    assert provider.name == "openai"
    assert provider.model == "gpt-4o"


def test_claude_provider_init():
    """Claude 프로바이더 초기화 테스트 (API 호출 없음)"""
    from providers.claude_provider import ClaudeProvider

    provider = ClaudeProvider(api_key="test-key", model="claude-opus-4-5")
    assert provider.name == "claude"
    assert provider.model == "claude-opus-4-5"


def test_provider_history_management():
    """프로바이더 대화 기록 관리 테스트"""
    from providers.base_provider import Message
    from providers.openai_provider import OpenAIProvider

    provider = OpenAIProvider(api_key="test")
    provider.add_message(Message.user("질문"))
    provider.add_message(Message.assistant("답변"))

    assert len(provider.history) == 2

    provider.clear_history()
    assert len(provider.history) == 0


def test_provider_context_window():
    """컨텍스트 창 제한 테스트"""
    from providers.base_provider import Message
    from providers.openai_provider import OpenAIProvider

    provider = OpenAIProvider(api_key="test")
    for i in range(30):
        provider.add_message(Message.user(f"메시지 {i}"))

    context = provider.get_context_messages(max_messages=10)
    assert len(context) == 10


def test_interpreter_provider_init():
    """Open Interpreter 프로바이더 초기화 테스트"""
    from providers.interpreter_provider import InterpreterProvider

    provider = InterpreterProvider(llm_api_key="test", model="gpt-4o")
    assert provider.name == "interpreter"
    assert provider.safe_mode is False
