@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ════════════════════════════════════════════════════════════
::  Jarvis AI Assistant — Windows 설치 스크립트
::  처음 한 번만 실행하면 됩니다
:: ════════════════════════════════════════════════════════════

title Jarvis 설치 중...

set "JARVIS_DIR=%~dp0"
set "VENV_DIR=%JARVIS_DIR%.venv"

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║    Jarvis AI Assistant 설치 프로그램         ║
echo  ║    ChatGPT + Claude + Open Interpreter       ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: ── Step 1: Python 확인 ──────────────────────────────────
echo  [1/5] Python 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [오류] Python이 설치되지 않았습니다.
    echo         https://www.python.org/downloads/ 에서 Python 3.11 이상을 설치하세요.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo         Python %PY_VER% 확인됨 ✓

:: ── Step 2: 가상환경 생성 ────────────────────────────────
echo.
echo  [2/5] 가상환경 생성 중...
if exist "%VENV_DIR%" (
    echo         기존 가상환경이 있습니다. 재생성합니다...
    rmdir /s /q "%VENV_DIR%"
)
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo  [오류] 가상환경 생성에 실패했습니다.
    pause
    exit /b 1
)
echo         가상환경 생성 완료 ✓

:: ── Step 3: 가상환경 활성화 ─────────────────────────────
echo.
echo  [3/5] 가상환경 활성화 중...
call "%VENV_DIR%\Scripts\activate.bat"
echo         활성화 완료 ✓

:: ── Step 4: 패키지 설치 ─────────────────────────────────
echo.
echo  [4/5] 패키지 설치 중... (시간이 걸릴 수 있습니다)
pip install --upgrade pip --quiet
pip install -r "%JARVIS_DIR%requirements.txt"
if errorlevel 1 (
    echo  [경고] 일부 패키지 설치에 실패했습니다.
    echo         open-interpreter는 별도 설치가 필요할 수 있습니다.
)
echo         패키지 설치 완료 ✓

:: ── Step 5: .env 설정 ───────────────────────────────────
echo.
echo  [5/5] 환경변수 설정...
if not exist "%JARVIS_DIR%.env" (
    copy "%JARVIS_DIR%.env.example" "%JARVIS_DIR%.env" >nul
    echo         .env 파일이 생성되었습니다.
    echo.
    echo  ════════════════════════════════════════════════
    echo  [중요] API 키를 설정해야 합니다!
    echo  ════════════════════════════════════════════════
    echo.
    echo  다음 파일을 열어서 API 키를 입력하세요:
    echo  %JARVIS_DIR%.env
    echo.
    echo  필요한 API 키:
    echo    - OPENAI_API_KEY   : https://platform.openai.com
    echo    - ANTHROPIC_API_KEY: https://console.anthropic.com
    echo.
    set /p "OPEN_ENV=지금 .env 파일을 열어서 편집할까요? (y/n): "
    if /i "!OPEN_ENV!"=="y" notepad "%JARVIS_DIR%.env"
) else (
    echo         .env 파일이 이미 존재합니다 ✓
)

:: ── 바탕화면 바로가기 생성 ───────────────────────────────
echo.
set /p "CREATE_SHORTCUT=바탕화면에 바로가기를 만들까요? (y/n): "
if /i "!CREATE_SHORTCUT!"=="y" (
    powershell -Command ^
        "$ws = New-Object -COM WScript.Shell; " ^
        "$s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Jarvis AI.lnk'); " ^
        "$s.TargetPath = '%JARVIS_DIR%jarvis.bat'; " ^
        "$s.WorkingDirectory = '%JARVIS_DIR%'; " ^
        "$s.Description = 'Jarvis AI Assistant'; " ^
        "$s.Save()"
    echo         바탕화면 바로가기 생성 완료 ✓
)

:: ── 설치 완료 ────────────────────────────────────────────
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║    ✅ Jarvis 설치가 완료되었습니다!          ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo  실행 방법:
echo    • jarvis.bat 더블클릭
echo    • 또는 터미널에서: python jarvis.py
echo.
echo  도움말: python jarvis.py --help
echo.

set /p "RUN_NOW=지금 바로 Jarvis를 실행할까요? (y/n): "
if /i "!RUN_NOW!"=="y" (
    call "%JARVIS_DIR%jarvis.bat"
) else (
    pause
)
