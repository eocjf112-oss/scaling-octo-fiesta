param(
    [ValidateSet("install", "remove", "status")]
    [string]$Action = "install"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$StartupFolder = [Environment]::GetFolderPath("Startup")
$StartupFile = Join-Path $StartupFolder "JarvisStartup.bat"
$TrayScript = Join-Path $PSScriptRoot "jarvis-tray.ps1"

if ($Action -eq "install") {
    $content = @"
@echo off
cd /d "$ProjectRoot"
powershell -NoProfile -ExecutionPolicy Bypass -STA -File "$TrayScript"
"@
    Set-Content -Path $StartupFile -Value $content -Encoding ASCII
    Write-Host "Jarvis 시작 자동 실행을 등록했습니다: $StartupFile"
    exit 0
}

if ($Action -eq "remove") {
    if (Test-Path $StartupFile) {
        Remove-Item $StartupFile -Force
        Write-Host "Jarvis 시작 자동 실행을 제거했습니다."
    } else {
        Write-Host "등록된 Jarvis 시작 파일이 없습니다."
    }
    exit 0
}

if (Test-Path $StartupFile) {
    Write-Host "Jarvis 시작 자동 실행 상태: 등록됨"
    Write-Host $StartupFile
} else {
    Write-Host "Jarvis 시작 자동 실행 상태: 등록되지 않음"
}
