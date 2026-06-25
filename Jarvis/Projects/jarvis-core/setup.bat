@echo off
chcp 65001 > nul
title Jarvis AI — 초기 설정

echo.
echo  ===============================================
echo   Jarvis AI Assistant — Windows 초기 설정
echo  ===============================================
echo.

:: Python 설치 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되지 않았습니다.
    echo  Python 3.10 이상을 설치하세요: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/5] Python 버전 확인...
python --version
echo.

:: pip 업그레이드
echo [2/5] pip 업그레이드 중...
python -m pip install --upgrade pip --quiet
echo  완료!
echo.

:: 가상환경 생성
echo [3/5] 가상환경 생성 중 (venv)...
if not exist "venv" (
    python -m venv venv
    echo  가상환경 생성 완료!
) else (
    echo  기존 가상환경을 사용합니다.
)
echo.

:: 가상환경 활성화 및 의존성 설치
echo [4/5] 의존성 설치 중...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [경고] 일부 패키지 설치에 실패했습니다. requirements.txt를 확인하세요.
) else (
    echo  모든 패키지 설치 완료!
)
echo.

:: .env 파일 설정
echo [5/5] 환경 설정 파일 확인...
if not exist ".env" (
    copy .env.example .env > nul
    echo  .env 파일이 생성되었습니다.
    echo.
    echo  [중요] .env 파일을 열어 API 키를 입력하세요:
    echo   - OPENAI_API_KEY   : OpenAI API 키 (ChatGPT)
    echo   - ANTHROPIC_API_KEY: Anthropic API 키 (Claude)
    echo.
    echo  API 키 발급:
    echo   OpenAI  : https://platform.openai.com/api-keys
    echo   Anthropic: https://console.anthropic.com/settings/keys
    echo.
    notepad .env
) else (
    echo  .env 파일이 이미 존재합니다.
)
echo.

echo  ===============================================
echo   설정 완료! 'start_jarvis.bat'를 실행하세요.
echo  ===============================================
echo.
pause
