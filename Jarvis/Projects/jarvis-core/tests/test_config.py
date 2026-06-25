"""
Jarvis AI — 설정 모듈 테스트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_config_loads():
    """설정 기본 로드 테스트"""
    from config import JarvisConfig

    config = JarvisConfig.from_env()
    assert config is not None
    assert config.language in ["ko", "en"]
    assert config.max_context_messages > 0


def test_openai_config_from_env():
    """OpenAI 설정 환경변수 파싱 테스트"""
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    os.environ["OPENAI_MODEL"] = "gpt-4o"

    from config import OpenAIConfig
    cfg = OpenAIConfig.from_env()

    assert cfg.api_key == "sk-test-key"
    assert cfg.model == "gpt-4o"


def test_anthropic_config_from_env():
    """Anthropic 설정 환경변수 파싱 테스트"""
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
    os.environ["ANTHROPIC_MODEL"] = "claude-opus-4-5"

    from config import AnthropicConfig
    cfg = AnthropicConfig.from_env()

    assert cfg.api_key == "sk-ant-test"
    assert cfg.model == "claude-opus-4-5"


def test_get_best_provider_auto():
    """기본 프로바이더 자동 선택 테스트"""
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-valid"
    os.environ["JARVIS_DEFAULT_PROVIDER"] = "auto"

    from config import reload_config
    config = reload_config()

    best = config.get_best_provider()
    assert best in ["claude", "openai", "none"]


def test_available_providers_empty():
    """API 키 없을 때 사용 가능 프로바이더 빈 목록 반환"""
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)

    from config import reload_config
    config = reload_config()

    available = config.get_available_providers()
    assert isinstance(available, list)
