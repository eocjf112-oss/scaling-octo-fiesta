@echo off
chcp 65001 >nul
setlocal

set "JARVIS_DIR=%~dp0"
cd /d "%JARVIS_DIR%"

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    )
)

if /I "%~1"=="env" goto open_env
if /I "%~1"=="test" goto test_providers
if /I "%~1"=="providers" goto list_providers
if /I "%~1"=="help" goto help
if "%~1"=="" goto help

call :python_cmd
%JARVIS_PYTHON% -m jarvis_assistant %*
exit /b %ERRORLEVEL%

:open_env
echo .env 파일을 엽니다. OPENAI_API_KEY와 ANTHROPIC_API_KEY 값을 입력한 뒤 저장하세요.
notepad ".env"
exit /b 0

:test_providers
call :python_cmd
echo Jarvis Provider 연결 테스트를 실행합니다.
%JARVIS_PYTHON% -m jarvis_assistant --test-providers
exit /b %ERRORLEVEL%

:list_providers
call :python_cmd
%JARVIS_PYTHON% -m jarvis_assistant --list-providers
exit /b %ERRORLEVEL%

:help
echo.
echo Windows Jarvis AI Assistant
echo.
echo 사용법:
echo   Jarvis.bat env
echo     .env 파일을 메모장으로 열어 API 키를 입력합니다.
echo.
echo   Jarvis.bat test
echo     ChatGPT, Claude, Open Interpreter 연결 상태를 테스트합니다.
echo.
echo   Jarvis.bat providers
echo     현재 사용 가능한 Provider 목록을 출력합니다.
echo.
echo   Jarvis.bat "요청 내용"
echo     Jarvis 자동 라우터로 요청을 실행합니다.
echo.
exit /b 0

:python_cmd
if exist ".venv\Scripts\python.exe" (
    set "JARVIS_PYTHON=.venv\Scripts\python.exe"
) else (
    set "JARVIS_PYTHON=python"
)
exit /b 0
