"""
Jarvis 대화형 CLI 인터페이스
Rich 라이브러리를 사용한 아름다운 터미널 UI를 제공합니다.
prompt_toolkit으로 히스토리와 자동완성을 지원합니다.
"""
import sys
from datetime import datetime
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from core.config import config
from core.logger import setup_logger, get_logger
from core.memory import memory_manager
from core.router import JarvisRouter

logger = get_logger("cli")
console = Console()

# ── CLI 스타일 ────────────────────────────────────────────────
PROMPT_STYLE = Style.from_dict({
    "prompt": "ansicyan bold",
    "": "ansiwhite",
})

AI_COLORS = {
    "chatgpt": "green",
    "claude": "yellow",
    "interpreter": "blue",
    "error": "red",
}

HELP_TEXT = """
[bold cyan]📖 Jarvis 명령어 도움말[/bold cyan]

[bold]AI 전환 명령어:[/bold]
  /chatgpt [메시지]    → ChatGPT로 대화
  /claude [메시지]     → Claude로 대화
  /interpreter [작업]  → Open Interpreter로 코드 실행
  /gpt [메시지]        → ChatGPT 단축키
  /auto                → 자동 AI 선택 모드
  
[bold]시스템 명령어:[/bold]
  /status              → 각 AI 연결 상태 확인
  /reset               → 대화 히스토리 초기화
  /memory              → 현재 메모리 요약 보기
  /save                → 현재 세션을 MEMORY.md에 저장
  /ai [이름]           → 기본 AI 변경 (chatgpt/claude/interpreter/auto)
  /help                → 이 도움말
  /exit, /quit, exit   → Jarvis 종료

[bold]슬래시 명령어 예시:[/bold]
  /claude 이 코드를 리뷰해줘
  /interpreter 현재 디렉토리의 파일 목록을 보여줘
  /gpt 오늘 할 일 목록 작성해줘
"""


class JarvisCLI:
    """Jarvis 대화형 CLI"""

    def __init__(self):
        self.router = JarvisRouter()
        self.history_file = config.workspace / ".jarvis_history"
        self._session_start = datetime.now()

    def run(self) -> None:
        """메인 대화 루프를 시작합니다."""
        setup_logger()
        self._print_banner()
        self._check_api_keys()

        session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            style=PROMPT_STYLE,
        )

        logger.info(f"Jarvis CLI 시작 (세션: {memory_manager.session_id})")

        try:
            while True:
                try:
                    ai_indicator = self._get_ai_indicator()
                    user_input = session.prompt(
                        f"\n👤 You [{ai_indicator}] > ",
                        style=PROMPT_STYLE,
                    ).strip()
                except KeyboardInterrupt:
                    console.print("\n[yellow]💡 종료하려면 /exit 를 입력하세요.[/yellow]")
                    continue
                except EOFError:
                    break

                if not user_input:
                    continue

                if self._handle_command(user_input):
                    continue

                self._process_message(user_input)

        finally:
            self._on_exit()

    # ── 메시지 처리 ──────────────────────────────────────────

    def _process_message(self, user_input: str) -> None:
        """사용자 메시지를 AI로 전달하고 응답을 출력합니다."""
        ai_name, response_stream = self.router.chat(user_input)
        color = AI_COLORS.get(ai_name, "white")
        label = self._get_agent_label(ai_name)

        console.print(f"\n{label} ", end="")

        full_response = ""
        try:
            for chunk in response_stream:
                console.print(chunk, end="", markup=False)
                full_response += chunk
            console.print()  # 줄바꿈
        except Exception as e:
            console.print(f"\n[red]❌ 오류: {e}[/red]")
            return

        memory_manager.add_message("assistant", full_response, ai_name)

        # 마크다운 렌더링 여부 확인 (코드 블록 포함 시)
        if "```" in full_response and len(full_response) > 100:
            console.print()
            console.print(Panel(
                Markdown(full_response),
                title=f"[{color}]{label} 응답[/{color}]",
                border_style=color,
                padding=(1, 2),
            ))

    # ── 명령어 핸들러 ─────────────────────────────────────────

    def _handle_command(self, user_input: str) -> bool:
        """
        슬래시 명령어를 처리합니다.
        Returns: True이면 명령어 처리 완료 (메시지 전송 불필요)
        """
        cmd = user_input.lower().strip()

        if cmd in ("/exit", "/quit", "exit", "quit", "종료"):
            self._on_exit()
            sys.exit(0)

        if cmd == "/help":
            console.print(HELP_TEXT)
            return True

        if cmd == "/status":
            self._print_status()
            return True

        if cmd == "/reset":
            self.router.reset_all()
            console.print("[green]✅ 모든 대화 히스토리가 초기화되었습니다.[/green]")
            return True

        if cmd == "/memory":
            self._print_memory_summary()
            return True

        if cmd == "/save":
            memory_manager.save_session()
            console.print("[green]✅ 현재 세션이 MEMORY.md에 저장되었습니다.[/green]")
            return True

        if cmd.startswith("/ai "):
            ai_name = cmd[4:].strip()
            if self.router.set_active_ai(ai_name):
                console.print(f"[green]✅ 기본 AI가 '{ai_name}'으로 변경되었습니다.[/green]")
            else:
                console.print(f"[red]❌ 알 수 없는 AI: '{ai_name}'. chatgpt/claude/interpreter/auto 중 선택하세요.[/red]")
            return True

        if cmd == "/auto":
            self.router.set_active_ai("auto")
            console.print("[green]✅ 자동 AI 선택 모드로 전환되었습니다.[/green]")
            return True

        return False

    # ── UI 출력 ──────────────────────────────────────────────

    def _print_banner(self) -> None:
        banner = Text()
        banner.append("  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗\n", style="bold cyan")
        banner.append("  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝\n", style="bold cyan")
        banner.append("  ██║███████║██████╔╝██║   ██║██║███████╗\n", style="bold cyan")
        banner.append("  ██ ██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║\n", style="bold cyan")
        banner.append("  ██████╔╝██║  ██║██║  ██╗ ╚████╔╝ ██║███████║\n", style="bold cyan")
        banner.append("  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝\n", style="bold cyan")

        console.print(Panel(
            banner,
            subtitle="[dim]당신의 개인 AI 엔지니어 | ChatGPT + Claude + Open Interpreter[/dim]",
            border_style="cyan",
            padding=(0, 4),
        ))

        console.print(f"[dim]  버전: 1.0.0  |  세션: {memory_manager.session_id}  |  /help 로 도움말[/dim]\n")

    def _print_status(self) -> None:
        status = self.router.status()
        console.print("\n[bold]🔌 AI 연결 상태[/bold]")
        for ai, available in status.items():
            if ai == "active":
                continue
            icon = "✅" if available else "❌"
            label = {"chatgpt": "ChatGPT  (OpenAI)", "claude": "Claude   (Anthropic)", "interpreter": "Interpreter (코드 실행)"}.get(ai, ai)
            console.print(f"  {icon}  {label}")
        console.print(f"\n  현재 기본 AI: [cyan]{status['active']}[/cyan]")

    def _print_memory_summary(self) -> None:
        summary = memory_manager.get_context_summary()
        if summary:
            console.print(Panel(
                Markdown(summary),
                title="[cyan]🧠 Jarvis 기억 요약[/cyan]",
                border_style="cyan",
            ))
        else:
            console.print("[yellow]기억된 컨텍스트가 없습니다.[/yellow]")

    def _get_ai_indicator(self) -> str:
        active = self.router.get_active_ai()
        colors = {"chatgpt": "green", "claude": "yellow", "interpreter": "blue", "auto": "cyan"}
        color = colors.get(active, "white")
        return f"[{color}]{active}[/{color}]"

    def _get_agent_label(self, ai_name: str) -> str:
        labels = {
            "chatgpt": "[bold green]🟢 ChatGPT[/bold green]",
            "claude": "[bold yellow]🟠 Claude[/bold yellow]",
            "interpreter": "[bold blue]🔵 Interpreter[/bold blue]",
            "error": "[bold red]❌ Error[/bold red]",
        }
        return labels.get(ai_name, f"[bold]{ai_name}[/bold]")

    def _check_api_keys(self) -> None:
        warnings = config.validate()
        if warnings:
            console.print("[yellow]⚠️  경고:[/yellow]")
            for w in warnings:
                console.print(f"   [yellow]• {w}[/yellow]")
            console.print(f"   [dim].env 파일에 API 키를 설정하세요: {config.workspace / '.env'}[/dim]\n")

    def _on_exit(self) -> None:
        elapsed = datetime.now() - self._session_start
        minutes = int(elapsed.total_seconds() / 60)
        console.print(f"\n[cyan]👋 Jarvis 종료 (세션 시간: {minutes}분)[/cyan]")
        if config.memory_auto_save:
            memory_manager.save_session()
            console.print("[dim]  세션이 MEMORY.md에 저장되었습니다.[/dim]")
