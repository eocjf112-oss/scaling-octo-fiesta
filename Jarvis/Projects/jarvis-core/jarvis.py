"""
Jarvis AI Assistant — 메인 진입점

사용법:
  python jarvis.py              # 대화형 CLI 시작
  python jarvis.py --help       # 도움말
  python jarvis.py --status     # 프로바이더 상태 확인
  python jarvis.py "안녕하세요" # 단일 메시지 처리 후 종료
"""

from __future__ import annotations

import sys

import click
from rich.console import Console

console = Console()


@click.command()
@click.option("--status", is_flag=True, help="AI 프로바이더 상태 확인 후 종료")
@click.option("--provider", "-p", default=None, help="사용할 프로바이더 지정 (claude/openai/interpreter)")
@click.option("--debug", is_flag=True, help="디버그 모드 활성화")
@click.option("--version", is_flag=True, help="버전 정보 출력")
@click.argument("message", nargs=-1, required=False)
def main(
    status: bool,
    provider: str | None,
    debug: bool,
    version: bool,
    message: tuple[str, ...],
) -> None:
    """
    Jarvis AI Assistant — ChatGPT + Claude + Open Interpreter 통합 시스템

    대화형 모드: python jarvis.py
    단일 메시지: python jarvis.py "질문이나 명령을 입력하세요"
    """
    if version:
        console.print("[bold cyan]Jarvis AI Assistant v1.0[/bold cyan]")
        console.print("ChatGPT (OpenAI) + Claude (Anthropic) + Open Interpreter")
        return

    if debug:
        import os
        os.environ["DEBUG_MODE"] = "true"

    from config import get_config, reload_config

    if debug:
        reload_config()

    config = get_config()

    if status:
        from orchestrator import Orchestrator
        from cli import print_status

        orch = Orchestrator(config)
        orch.initialize()
        print_status(orch)
        return

    if message:
        # 단일 메시지 처리 모드 (비대화형)
        full_message = " ".join(message)
        _run_single_message(full_message, provider)
        return

    # 대화형 CLI 시작
    from cli import JarvisCLI
    app = JarvisCLI()
    app.run()


def _run_single_message(message: str, provider: str | None = None) -> None:
    """단일 메시지 처리 (스크립트/자동화 용도)"""
    from orchestrator import Orchestrator
    from config import get_config

    orch = Orchestrator(get_config())
    orch.initialize()

    selected, gen = orch.stream(message, provider)
    console.print(f"[dim][{selected}][/dim] ", end="")

    for chunk in gen:
        console.print(chunk, end="", markup=False)

    console.print()
    orch.shutdown()


if __name__ == "__main__":
    main()
