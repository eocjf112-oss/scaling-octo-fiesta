from __future__ import annotations

import argparse
import sys

from jarvis_assistant.config import JarvisConfig
from jarvis_assistant.diagnostics import format_provider_checks, run_provider_checks
from jarvis_assistant.memory import MemoryStore, format_memory_status
from jarvis_assistant.models import ChatRequest, ProviderError
from jarvis_assistant.router import JarvisRouter
from jarvis_assistant.voice import format_voice_status, get_voice_capabilities


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Windows Jarvis AI Assistant")
    parser.add_argument("prompt", nargs="*", help="Jarvis에 전달할 요청")
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "local", "windows_automation", "chatgpt", "claude", "open_interpreter"],
        help="사용할 Provider",
    )
    parser.add_argument("--system", dest="system_prompt", help="시스템 프롬프트")
    parser.add_argument("--temperature", type=float, help="모델 temperature")
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="현재 사용 가능한 Provider 목록 출력",
    )
    parser.add_argument(
        "--confirm-local-execution",
        action="store_true",
        help="Open Interpreter가 로컬 파일/명령 작업을 수행할 수 있음을 명시적으로 확인",
    )
    parser.add_argument(
        "--test-providers",
        action="store_true",
        help="ChatGPT, Claude, Open Interpreter 연결 상태를 점검",
    )
    parser.add_argument(
        "--voice-status",
        action="store_true",
        help="Jarvis 음성 입출력 준비 상태를 점검",
    )
    parser.add_argument(
        "--memory-status",
        action="store_true",
        help="Jarvis SQLite 장기 기억 상태를 출력",
    )
    parser.add_argument(
        "--test-prompt",
        default="Jarvis 연결 테스트입니다. 한국어로 연결 성공이라고 짧게 답하세요.",
        help="--test-providers에서 ChatGPT/Claude에 보낼 테스트 프롬프트",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = JarvisConfig.from_env()
    memory = MemoryStore.from_config(config)
    memory.initialize()
    memory.bootstrap_defaults(config)
    memory_context = memory.load_context()
    router = JarvisRouter(config)

    if args.list_providers:
        providers = router.available_providers()
        output = "\n".join(providers) if providers else "No providers available."
        print(output)
        memory.record_work("system", "list-providers", output, "success")
        return 0

    if args.test_providers:
        checks = run_provider_checks(config, args.test_prompt)
        output = format_provider_checks(checks)
        print(output)
        memory.record_work("system", "test-providers", output, "success")
        return 0

    if args.voice_status:
        output = format_voice_status(get_voice_capabilities())
        print(output)
        memory.record_work("system", "voice-status", output, "success")
        return 0

    if args.memory_status:
        output = format_memory_status(memory)
        print(output)
        memory.record_work("system", "memory-status", output, "success")
        return 0

    prompt = " ".join(args.prompt).strip()

    if not prompt:
        parser.error(
            "prompt is required unless --list-providers, --test-providers, --voice-status, "
            "or --memory-status is used."
        )

    request = ChatRequest(
        prompt=prompt,
        provider=args.provider,
        system_prompt=args.system_prompt,
        temperature=args.temperature,
        metadata={
            "confirm_local_execution": args.confirm_local_execution,
            "memory_context": memory_context,
        },
    )

    try:
        response = router.dispatch(request)
    except ProviderError as exc:
        print(f"Jarvis error: {exc}", file=sys.stderr)
        memory.record_work(args.provider, prompt, "", "failure", error=str(exc))
        return 1

    print(response.content)
    memory.record_work(
        response.provider,
        prompt,
        response.content,
        "success",
        metadata={"requested_provider": args.provider},
    )
    memory.record_project_progress(
        "Windows Jarvis AI Assistant",
        "진행 중",
        f"최근 실행 Provider: {response.provider}",
    )
    return 0
