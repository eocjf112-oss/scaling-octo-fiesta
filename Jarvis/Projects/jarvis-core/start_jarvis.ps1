# Jarvis AI Assistant — PowerShell 런처
# Windows Terminal에서 최상의 경험을 제공합니다.

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  Jarvis AI Assistant 시작 중..." -ForegroundColor Cyan

# 가상환경 확인
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[오류] 가상환경이 없습니다. setup.bat을 먼저 실행하세요." -ForegroundColor Red
    Read-Host "계속하려면 Enter 키를 누르세요"
    exit 1
}

# .env 파일 확인
if (-not (Test-Path ".env")) {
    Write-Host "[오류] .env 파일이 없습니다. setup.bat을 먼저 실행하세요." -ForegroundColor Red
    Read-Host "계속하려면 Enter 키를 누르세요"
    exit 1
}

# 가상환경 활성화
& ".\venv\Scripts\Activate.ps1"

# Jarvis 실행
try {
    python jarvis.py @args
} catch {
    Write-Host ""
    Write-Host "[오류] Jarvis 실행 중 오류가 발생했습니다: $_" -ForegroundColor Red
    Read-Host "계속하려면 Enter 키를 누르세요"
    exit 1
}
