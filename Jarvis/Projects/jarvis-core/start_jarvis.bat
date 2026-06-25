@echo off
chcp 65001 > nul
title Jarvis AI Assistant

:: 가상환경 확인
if not exist "venv\Scripts\activate.bat" (
    echo [오류] 가상환경이 없습니다. setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

:: .env 파일 확인
if not exist ".env" (
    echo [오류] .env 파일이 없습니다. setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

:: 가상환경 활성화 및 Jarvis 실행
call venv\Scripts\activate.bat
python jarvis.py %*

:: 비정상 종료 시 오류 표시
if %errorlevel% neq 0 (
    echo.
    echo [오류] Jarvis가 비정상 종료되었습니다. (오류 코드: %errorlevel%)
    echo  로그 파일을 확인하세요: ..\..\Logs\
    pause
)
