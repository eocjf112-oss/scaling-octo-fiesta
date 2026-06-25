"""
Jarvis AI — CLI 인터페이스

Rich 라이브러리를 사용한 아름다운 터미널 UI입니다.
Windows Terminal, PowerShell, cmd, macOS/Linux Terminal을 모두 지원합니다.

특수 명령어:
  /help             — 도움말 표시
  /status           — 프로바이더 상태
  /switch <name>    — 프로바이더 전환 (claude, openai, interpreter)
  /memory           — 메모리 요약 표시
  /session          — 현재 세션 정보
  /reset            — 대화 기록 초기화
  /clear            — 화면 지우기
  /exit, /quit      — 종료
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from loguru import logger

from orchestrator import Orchestrator
from config import get_config

if TYPE_CHECKING:
    pass

console = Console()

# ─────────────────────────────────────────────
# 색상 팔레트
# ─────────────────────────────────────────────
COLOR_JARVIS = "bold cyan"
COLOR_USER = "bold green"
COLOR_SYSTEM = "bold yellow"
COLOR_ERROR = "bold red"
COLOR_SUCCESS = "bold green"
COLOR_INFO = "dim white"

PROVIDER_COLORS = {
    "claude": "bold magenta",
    "openai": "bold green",
    "interpreter": "bold cyan",
}

PROVIDER_ICONS = {
    "claude": "C",
    "openai": "G",
    "interpreter": "I",
}


def print_banner() -> None:
    """Jarvis 시작 배너 출력"""
    banner = Text()
    banner.append("\n")
    banner.append("  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗\n", style="bold cyan")
    banner.append("  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝\n", style="bold cyan")
    banner.append("  ██║███████║██████╔╝██║   ██║██║███████╗\n", style="bold cyan")
    banner.append("  ██ ║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║\n", style="bold cyan")
    banner.append("  ╚██╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║\n", style="bold cyan")
    banner.append("   ╚═╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝\n", style="bold cyan")
    banner.append("\n")
    banner.append("  AI Assistant v1.0  — ChatGPT + Claude + Open Interpreter\n", style="dim white")
    banner.append("  '/help' 를 입력하면 명령어 목록을 확인할 수 있습니다.\n", style="dim white")

    console.print(banner)


def print_help() -> None:
    """도움말 패널 출력"""
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("명령어", style="bold white", width=24)
    table.add_column("설명", style="dim white")

    commands = [
        ("/help", "이 도움말 표시"),
        ("/status", "AI 프로바이더 연결 상태 확인"),
        ("/switch claude", "Claude (Anthropic) 로 전환"),
        ("/switch openai", "ChatGPT (OpenAI) 로 전환"),
        ("/switch interpreter", "Open Interpreter 로 전환 (코드 실행)"),
        ("/memory", "현재 장기 기억 요약 표시"),
        ("/session", "현재 세션 통계 표시"),
        ("/reset", "대화 기록 초기화"),
        ("/clear", "화면 지우기"),
        ("/exit 또는 /quit", "Jarvis 종료"),
        ("", ""),
        ("[메시지]", "기본 모드: 메시지를 AI에게 전달"),
        ("@claude [메시지]", "명시적으로 Claude 사용"),
        ("@openai [메시지]", "명시적으로 ChatGPT 사용"),
        ("@run [메시지]", "Open Interpreter로 코드 실행"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(Panel(table, title="[bold cyan]Jarvis 명령어 목록[/bold cyan]", border_style="cyan"))


def print_status(orchestrator: Orchestrator) -> None:
    """프로바이더 상태 테이블 출력"""
    status = orchestrator.get_provider_status()
    config = get_config()

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("프로바이더", style="bold white", width=20)
    table.add_column("상태", width=10)
    table.add_column("모델", style="dim white", width=24)
    table.add_column("현재 선택", width=10)

    provider_models = {
        "claude": config.anthropic.model,
        "openai": config.openai.model,
        "interpreter": config.interpreter.model + " (실행)",
    }

    current = config.get_best_provider()

    for name, available in status.items():
        icon = PROVIDER_ICONS.get(name, "?")
        color = PROVIDER_COLORS.get(name, "white")
        status_text = Text("● 연결됨", style="bold green") if available else Text("○ 미설정", style="dim red")
        is_current = "✓ 기본값" if name == current else ""
        model = provider_models.get(name, "-")
        table.add_row(f"[{color}]{icon} {name.capitalize()}[/{color}]", status_text, model, is_current)

    console.print(Panel(table, title="[bold cyan]AI 프로바이더 상태[/bold cyan]", border_style="cyan"))


def stream_response(orchestrator: Orchestrator, message: str, provider: str | None = None) -> None:
    """스트리밍으로 AI 응답 출력"""
    selected_provider, gen = orchestrator.stream(message, provider)
    icon = PROVIDER_ICONS.get(selected_provider, "J")
    color = PROVIDER_COLORS.get(selected_provider, "cyan")

    console.print(f"\n[{color}][{icon}] Jarvis ({selected_provider})[/{color}]", end="")
    console.print()

    full_response = ""
    try:
        for chunk in gen:
            console.print(chunk, end="", markup=False)
            full_response += chunk
        console.print()
    except KeyboardInterrupt:
        console.print("\n[dim]⚠ 응답이 중단되었습니다.[/dim]")
        return

    if full_response.strip():
        console.print()


def parse_explicit_provider(message: str) -> tuple[str | None, str]:
    """@prefix 형식으로 명시적 프로바이더 파싱"""
    if message.startswith("@claude "):
        return "claude", message[8:].strip()
    elif message.startswith("@openai "):
        return "openai", message[8:].strip()
    elif message.startswith("@run ") or message.startswith("@interpreter "):
        prefix_len = 5 if message.startswith("@run ") else 13
        return "interpreter", message[prefix_len:].strip()
    return None, message


def handle_command(command: str, orchestrator: Orchestrator) -> bool:
    """
    특수 명령 처리.
    True = 계속 실행, False = 종료
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in ("/exit", "/quit", "/종료"):
        return False

    elif cmd == "/help" or cmd == "/도움말":
        print_help()

    elif cmd == "/status" or cmd == "/상태":
        print_status(orchestrator)

    elif cmd == "/switch" or cmd == "/전환":
        if not arg:
            console.print("[yellow]사용법: /switch <claude|openai|interpreter>[/yellow]")
        elif orchestrator.switch_provider(arg):
            console.print(f"[green]✓ 프로바이더를 '{arg}'(으)로 변경했습니다.[/green]")
        else:
            console.print(f"[red]'{arg}' 프로바이더를 찾을 수 없습니다.[/red]")

    elif cmd == "/memory" or cmd == "/메모리":
        if orchestrator._memory:
            summary = orchestrator._memory.get_context_summary()
            console.print(Panel(summary, title="[bold cyan]Jarvis 장기 기억[/bold cyan]", border_style="cyan"))
        else:
            console.print("[dim]메모리 시스템이 초기화되지 않았습니다.[/dim]")

    elif cmd == "/session" or cmd == "/세션":
        info = orchestrator.get_session_info()
        console.print(Panel(info, title="[bold cyan]현재 세션 정보[/bold cyan]", border_style="cyan"))

    elif cmd == "/reset" or cmd == "/초기화":
        orchestrator.reset_conversation()
        console.print("[green]✓ 대화 기록이 초기화되었습니다.[/green]")

    elif cmd == "/clear" or cmd == "/지우기":
        console.clear()
        print_banner()

    else:
        console.print(f"[dim]알 수 없는 명령어: {cmd}. '/help'를 입력하세요.[/dim]")

    return True


class JarvisCLI:
    """Jarvis 메인 CLI 애플리케이션"""

    def __init__(self) -> None:
        self.config = get_config()
        self.orchestrator = Orchestrator(self.config)

    def run(self) -> None:
        """메인 인터랙티브 루프 실행"""
        # 로깅 설정
        logger.remove()
        if self.config.debug_mode:
            logger.add(sys.stderr, level="DEBUG", format="[{time:HH:mm:ss}] {level} {message}")
        else:
            log_file = self.config.log_path / "jarvis_{time:YYYY-MM-DD}.log"
            logger.add(str(log_file), level="INFO", rotation="1 day", retention="30 days")

        print_banner()

        # 초기화
        try:
            with console.status("[cyan]Jarvis 시스템 초기화 중...[/cyan]"):
                self.orchestrator.initialize()
        except Exception as e:
            console.print(f"[red]초기화 오류: {e}[/red]")
            console.print("[yellow].env 파일에 API 키가 설정되어 있는지 확인하세요.[/yellow]")
            return

        available = self.orchestrator.config.get_available_providers()
        if not available:
            console.print(
                Panel(
                    "[yellow].env 파일에 OPENAI_API_KEY 또는 ANTHROPIC_API_KEY를 설정하세요.\n"
                    ".env.example 파일을 참고하여 .env 파일을 만드세요.[/yellow]",
                    title="[bold red]API 키 미설정[/bold red]",
                    border_style="red",
                )
            )

        print_status(self.orchestrator)
        console.print()

        # 메인 대화 루프
        while True:
            try:
                user_input = Prompt.ask(
                    f"[bold green]You[/bold green]",
                    console=console,
                ).strip()

                if not user_input:
                    continue

                # 특수 명령 처리
                if user_input.startswith("/"):
                    should_continue = handle_command(user_input, self.orchestrator)
                    if not should_continue:
                        break
                    continue

                # @prefix 명시적 프로바이더 파싱
                explicit_provider, cleaned_message = parse_explicit_provider(user_input)

                if not cleaned_message:
                    continue

                # AI 응답 스트리밍
                stream_response(self.orchestrator, cleaned_message, explicit_provider)

            except KeyboardInterrupt:
                console.print("\n[dim](Ctrl+C를 한 번 더 누르거나 /exit를 입력하면 종료됩니다)[/dim]")
                try:
                    user_input = Prompt.ask("[dim]계속하려면 Enter, 종료하려면 /exit[/dim]", console=console)
                    if user_input.strip().lower() in ("/exit", "/quit", "exit", "quit"):
                        break
                except KeyboardInterrupt:
                    break

            except EOFError:
                break

        # 종료 처리
        self.orchestrator.shutdown()
        console.print("\n[bold cyan]Jarvis를 종료합니다. 안녕히 계세요! 👋[/bold cyan]\n")


def main() -> None:
    app = JarvisCLI()
    app.run()


if __name__ == "__main__":
    main()
