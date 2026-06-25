from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceCapability:
    name: str
    status: str
    message: str


def get_voice_capabilities() -> list[VoiceCapability]:
    system = platform.system().lower()
    capabilities = [
        VoiceCapability(
            name="tts",
            status="준비됨" if system == "windows" else "준비 필요",
            message=(
                "Windows SAPI 기반 음성 출력 연결 지점이 준비되어 있습니다."
                if system == "windows"
                else "Windows에서 SAPI를 사용하거나 pyttsx3 같은 로컬 TTS 엔진을 연결할 수 있습니다."
            ),
        ),
        VoiceCapability(
            name="stt",
            status="준비 필요",
            message="오프라인 STT 엔진(Vosk/Whisper local 등)을 추후 연결할 인터페이스가 준비되어 있습니다.",
        ),
    ]

    if shutil.which("powershell") or shutil.which("pwsh"):
        capabilities.append(
            VoiceCapability(
                name="powershell",
                status="준비됨",
                message="PowerShell을 통한 Windows 음성/자동화 브리지를 사용할 수 있습니다.",
            )
        )
    return capabilities


def format_voice_status(capabilities: list[VoiceCapability]) -> str:
    lines = ["Jarvis 음성 입출력 준비 상태"]
    for capability in capabilities:
        lines.append(f"- {capability.name}: {capability.status} - {capability.message}")
    return "\n".join(lines)
