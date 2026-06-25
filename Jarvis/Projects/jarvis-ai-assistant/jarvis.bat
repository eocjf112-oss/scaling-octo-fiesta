@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ════════════════════════════════════════════════════════════
::  Jarvis AI Assistant — Windows 실행 스크립트
::  더블클릭 또는 터미널에서 실행하세요
:: ════════════════════════════════════════════════════════════

title Jarvis AI Assistant

:: 스크립트 위치를 기준으로 경로 설정
set "JARVIS_DIR=%~dp0"
set "VENV_DIR=%JARVIS_DIR%.venv"
set "PYTHON_CMD=python"

echo.
echo  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
echo  ██ ██╔══██╗██╔══██╗╚██╗ ██╔╝██║╚════██║
echo  ██████╔╝██║  ██║██║  ██╗ ╚████╔╝ ██║███████║
echo  ╚═════╝                  AI Assistant v1.0
echo.
echo  ChatGPT + Claude + Open Interpreter
echo  ─────────────────────────────────────────────
echo.

:: 가상환경 확인 및 활성화
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo  [+] 가상환경 활성화 중...
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo  [!] 가상환경이 없습니다. install.bat을 먼저 실행하세요.
    echo.
    set /p "CONTINUE=그냥 계속 진행할까요? (y/n): "
    if /i "!CONTINUE!" neq "y" (
        pause
        exit /b 1
    )
)

:: .env 파일 확인
if not exist "%JARVIS_DIR%.env" (
    echo  [!] .env 파일이 없습니다.
    echo      .env.example을 복사하여 .env를 만들고 API 키를 입력하세요.
    echo.
    if exist "%JARVIS_DIR%.env.example" (
        copy "%JARVIS_DIR%.env.example" "%JARVIS_DIR%.env" >nul
        echo  [+] .env.example을 .env로 복사했습니다. API 키를 입력해주세요:
        echo      %JARVIS_DIR%.env
        notepad "%JARVIS_DIR%.env"
        pause
        exit /b 0
    )
)

:: 인수가 있으면 단일 질문 모드로 실행
if not "%~1"=="" (
    cd /d "%JARVIS_DIR%"
    %PYTHON_CMD% jarvis.py %*
    goto :end
)

:: 대화형 모드 실행
cd /d "%JARVIS_DIR%"
%PYTHON_CMD% jarvis.py

:end
echo.
echo  Jarvis가 종료되었습니다.
if "%~1"=="" pause
