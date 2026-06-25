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
if /I "%~1"=="listen" goto voice_listen
if /I "%~1"=="tray" goto tray_start
if /I "%~1"=="memory" goto memory_status
if /I "%~1"=="startup" goto startup
if /I "%~1"=="windows" goto windows_automation
if /I "%~1"=="oi" goto open_interpreter
if /I "%~1"=="excel" goto action_excel
if /I "%~1"=="word" goto action_word
if /I "%~1"=="pdf" goto action_pdf
if /I "%~1"=="search" goto action_search
if /I "%~1"=="organize" goto action_organize
if /I "%~1"=="run" goto action_run
if /I "%~1"=="web" goto action_web
if /I "%~1"=="help" goto help
if "%~1"=="" goto tray_start

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

:voice_listen
powershell -NoProfile -ExecutionPolicy Bypass -File "%JARVIS_DIR%scripts\windows\jarvis-voice.ps1"
exit /b %ERRORLEVEL%

:tray_start
powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%JARVIS_DIR%scripts\windows\jarvis-tray.ps1"
exit /b %ERRORLEVEL%

:memory_status
call :python_cmd
%JARVIS_PYTHON% -m jarvis_assistant --memory-status
exit /b %ERRORLEVEL%

:startup
if /I "%~2"=="install" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%JARVIS_DIR%scripts\windows\install-startup.ps1" -Action install
    exit /b %ERRORLEVEL%
)
if /I "%~2"=="remove" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%JARVIS_DIR%scripts\windows\install-startup.ps1" -Action remove
    exit /b %ERRORLEVEL%
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%JARVIS_DIR%scripts\windows\install-startup.ps1" -Action status
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

:action_excel
call :run_windows_action excel %*
exit /b %ERRORLEVEL%

:action_word
call :run_windows_action word %*
exit /b %ERRORLEVEL%

:action_pdf
call :run_windows_action pdf %*
exit /b %ERRORLEVEL%

:action_search
call :run_windows_action search %*
exit /b %ERRORLEVEL%

:action_organize
call :run_windows_action organize %*
exit /b %ERRORLEVEL%

:action_run
call :run_windows_action run %*
exit /b %ERRORLEVEL%

:action_web
call :run_windows_action web %*
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
echo   Jarvis.bat listen
echo     "자비스" 호출어를 기다리는 음성 리스너를 실행합니다.
echo.
echo   Jarvis.bat tray
echo     시스템 트레이에 Jarvis를 상주시킵니다. 인자 없이 Jarvis.bat을 실행해도 이 모드로 시작합니다.
echo.
echo   Jarvis.bat memory
echo     SQLite 장기 기억 상태를 출력합니다.
echo.
echo   Jarvis.bat startup install
echo     Windows 시작 시 Jarvis 트레이/음성 대기 상태가 자동 실행되도록 등록합니다.
echo.
echo   Jarvis.bat startup remove
echo     Windows 시작 자동 실행 등록을 제거합니다.
echo.
echo   Jarvis.bat windows status
echo     Windows 자동화 Provider 상태를 출력합니다.
echo.
echo   Jarvis.bat excel "월간 계획"
echo     엑셀 파일을 생성합니다.
echo.
echo   Jarvis.bat word "회의록"
echo     워드 파일을 생성합니다.
echo.
echo   Jarvis.bat pdf "보고서"
echo     PDF 파일을 생성합니다.
echo.
echo   Jarvis.bat search "계획"
echo     Jarvis 워크스페이스에서 파일을 검색합니다.
echo.
echo   Jarvis.bat organize
echo     Downloads 폴더 파일을 확장자 기준으로 정리합니다.
echo.
echo   Jarvis.bat run notepad
echo     프로그램을 실행합니다.
echo.
echo   Jarvis.bat web "검색어"
echo     기본 브라우저로 인터넷 검색을 실행합니다.
echo.
echo   Jarvis.bat oi "요청 내용"
echo     Open Interpreter로 로컬 자동화 요청을 실행합니다.
echo.
echo   Jarvis.bat "요청 내용"
echo     Jarvis 자동 라우터로 요청을 실행합니다.
echo.
echo   Jarvis.bat
echo     시스템 트레이 대기 상태로 바로 진입합니다.
echo.
exit /b 0

:python_cmd
if exist ".venv\Scripts\python.exe" (
    set "JARVIS_PYTHON=.venv\Scripts\python.exe"
) else (
    set "JARVIS_PYTHON=python"
)
exit /b 0

:run_windows_action
call :python_cmd
set "JARVIS_ACTION=%~1"
shift
%JARVIS_PYTHON% -m jarvis_assistant --provider windows_automation "%JARVIS_ACTION% %*"
exit /b %ERRORLEVEL%
