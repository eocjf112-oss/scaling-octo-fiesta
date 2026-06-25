"""
Jarvis 로깅 모듈
loguru 기반의 파일 + 콘솔 동시 로깅
"""
import sys
from pathlib import Path

from loguru import logger as _logger

from core.config import config


def setup_logger() -> None:
    """로거를 초기화합니다. 애플리케이션 시작 시 한 번 호출합니다."""
    _logger.remove()

    # 콘솔 출력 (INFO 이상)
    _logger.add(
        sys.stderr,
        level=config.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        colorize=True,
    )

    # 파일 출력 (전체 로그)
    log_dir: Path = config.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    _logger.add(
        log_dir / "jarvis_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} | {message}",
        rotation="00:00",       # 자정마다 로테이션
        retention="30 days",
        encoding="utf-8",
        enqueue=True,           # 비동기 쓰기
    )

    # AI 대화 전용 로그
    _logger.add(
        log_dir / "conversations_{time:YYYY-MM}.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda r: "CONVERSATION" in r["extra"],
        rotation="1 month",
        retention="1 year",
        encoding="utf-8",
    )


def get_logger(name: str = "jarvis"):
    """이름이 붙은 로거를 반환합니다."""
    return _logger.bind(module=name)


def log_conversation(role: str, content: str, ai: str = "") -> None:
    """대화 내용을 전용 로그 파일에 기록합니다."""
    label = f"[{ai.upper()}]" if ai else ""
    _logger.bind(CONVERSATION=True).info(f"{role.upper()} {label}: {content[:200]}")


logger = _logger
