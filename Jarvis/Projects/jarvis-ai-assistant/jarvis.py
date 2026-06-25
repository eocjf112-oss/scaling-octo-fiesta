"""
Jarvis AI Assistant — 메인 진입점

실행 방법:
    python jarvis.py              # 대화형 모드
    python jarvis.py "질문"       # 단일 질문 모드
    python jarvis.py --status     # 연결 상태 확인
    python jarvis.py --help       # 도움말
"""
import sys
import click


@click.command()
@click.argument("message", nargs=-1, required=False)
@click.option("--ai", "-a", default=None,
              help="사용할 AI 지정: chatgpt | claude | interpreter | auto")
@click.option("--status", is_flag=True, default=False,
              help="AI 연결 상태를 확인합니다")
@click.option("--reset", is_flag=True, default=False,
              help="대화 히스토리를 초기화합니다")
@click.option("--version", is_flag=True, default=False,
              help="버전 정보를 출력합니다")
def main(message, ai, status, reset, version):
    """
    🤖 Jarvis AI Assistant
    
    ChatGPT + Claude + Open Interpreter 통합 AI 시스템
    """
    if version:
        click.echo("Jarvis AI Assistant v1.0.0")
        click.echo("ChatGPT + Claude + Open Interpreter")
        return

    # 지연 임포트: 빠른 --help, --version 응답을 위해
    from core.logger import setup_logger
    setup_logger()

    if status:
        _show_status()
        return

    if reset:
        from core.router import JarvisRouter
        router = JarvisRouter()
        router.reset_all()
        click.echo("✅ 대화 히스토리가 초기화되었습니다.")
        return

    # 단일 질문 모드
    if message:
        _single_query(" ".join(message), ai)
        return

    # 대화형 모드
    _interactive_mode(ai)


def _interactive_mode(default_ai: str = None) -> None:
    """대화형 CLI 모드를 시작합니다."""
    from cli.main import JarvisCLI
    from core.router import JarvisRouter

    cli = JarvisCLI()
    if default_ai:
        cli.router.set_active_ai(default_ai)
    cli.run()


def _single_query(message: str, ai: str = None) -> None:
    """단일 질문에 답하고 종료합니다."""
    from rich.console import Console
    from core.router import JarvisRouter
    from core.logger import setup_logger

    console = Console()
    router = JarvisRouter()

    if ai:
        ai_name, stream = router.chat(message, force_ai=ai)
    else:
        ai_name, stream = router.chat(message)

    for chunk in stream:
        console.print(chunk, end="", markup=False)
    console.print()


def _show_status() -> None:
    """AI 연결 상태를 출력합니다."""
    from rich.console import Console
    from rich.table import Table
    from core.router import JarvisRouter
    from core.config import config

    console = Console()
    router = JarvisRouter()
    status = router.status()

    table = Table(title="🔌 Jarvis AI 연결 상태", border_style="cyan")
    table.add_column("AI", style="bold")
    table.add_column("상태")
    table.add_column("모델")

    models = {
        "chatgpt": config.openai_model,
        "claude": config.anthropic_model,
        "interpreter": config.interpreter_model,
    }

    for ai_name in ["chatgpt", "claude", "interpreter"]:
        available = status[ai_name]
        icon = "✅ 사용 가능" if available else "❌ API 키 없음"
        table.add_row(ai_name, icon, models.get(ai_name, "-"))

    console.print(table)
    console.print(f"\n  현재 기본 AI: [cyan]{status['active']}[/cyan]")
    console.print(f"  워크스페이스: [dim]{config.workspace}[/dim]")


if __name__ == "__main__":
    main()
