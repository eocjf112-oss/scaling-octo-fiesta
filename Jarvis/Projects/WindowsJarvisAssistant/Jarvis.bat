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
if /I "%~1"=="voice" goto voice_status
if /I "%~1"=="memory" goto memory_status
if /I "%~1"=="windows" goto windows_automation
if /I "%~1"=="oi" goto open_interpreter
if /I "%~1"=="help" goto help
if "%~1"=="" goto help

call :python_cmd
%JARVIS_PYTHON% -m jarvis_assistant %*
exit /b %ERRORLEVEL%

:open_env
echo .env 파일을 엽니다. API 키는 비워 두어도 Jarvis는 로컬 모드로 동작합니다.
notepad ".env"
exit /b 0

:test_providers
call :python_cmd
echo Jarvis 로컬/자동화 Provider 상태를 테스트합니다.
%JARVIS_PYTHON% -m jarvis_assistant --test-providers
exit /b %ERRORLEVEL%

:list_providers
call :python_cmd
%JARVIS_PYTHON% -m jarvis_assistant --list-providers
exit /b %ERRORLEVEL%

:voice_status
call :python_cmd
%JARVIS_PYTHON% -m jarvis_assistant --voice-status
exit /b %ERRORLEVEL%

:memory_status
call :python_cmd
%JARVIS_PYTHON% -m jarvis_assistant --memory-status
exit /b %ERRORLEVEL%

:windows_automation
call :python_cmd
shift
if "%~1"=="" (
    %JARVIS_PYTHON% -m jarvis_assistant --provider windows_automation "상태 점검"
) else (
    %JARVIS_PYTHON% -m jarvis_assistant --provider windows_automation %*
)
exit /b %ERRORLEVEL%

:open_interpreter
call :python_cmd
shift
if "%~1"=="" (
    echo Open Interpreter에 전달할 요청을 입력하세요.
    exit /b 1
)
%JARVIS_PYTHON% -m jarvis_assistant --provider open_interpreter --confirm-local-execution %*
exit /b %ERRORLEVEL%

:help
echo.
echo Windows Jarvis AI Assistant
echo.
echo 사용법:
echo   Jarvis.bat env
echo     .env 파일을 메모장으로 엽니다. API 키는 선택 사항입니다.
echo.
echo   Jarvis.bat test
echo     로컬, Windows 자동화, Open Interpreter, 선택 API Provider 상태를 테스트합니다.
echo.
echo   Jarvis.bat providers
echo     현재 사용 가능한 Provider 목록을 출력합니다.
echo.
echo   Jarvis.bat voice
echo     음성 입출력 준비 상태를 출력합니다.
echo.
echo   Jarvis.bat memory
echo     SQLite 장기 기억 상태를 출력합니다.
echo.
echo   Jarvis.bat windows status
echo     Windows 자동화 Provider 상태를 출력합니다.
echo.
echo   Jarvis.bat oi "요청 내용"
echo     Open Interpreter로 로컬 자동화 요청을 실행합니다.
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
