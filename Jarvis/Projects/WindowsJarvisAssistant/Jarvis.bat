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
if /I "%~1"=="selftest" goto self_test
if /I "%~1"=="providers" goto list_providers
if /I "%~1"=="voice" goto voice_status
if /I "%~1"=="listen" goto voice_listen
if /I "%~1"=="tray" goto tray_start
if /I "%~1"=="gui" goto gui_start
if /I "%~1"=="jarvis" goto gui_start
if "%~1"=="자비스" goto gui_start
if /I "%~1"=="settings" goto settings_start
if /I "%~1"=="memory" goto memory_status
if /I "%~1"=="startup" goto startup
if /I "%~1"=="windows" goto windows_automation
if /I "%~1"=="oi" goto open_interpreter
if /I "%~1"=="excel" goto action_excel
if /I "%~1"=="word" goto action_word
if /I "%~1"=="pdf" goto action_pdf
if /I "%~1"=="search" goto action_search
if /I "%~1"=="organize" goto action_organize
if /I "%~1"=="calc" goto action_calc
if /I "%~1"=="calculator" goto action_calc
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
if errorlevel 1 exit /b %ERRORLEVEL%
echo Jarvis 로컬/자동화 Provider 상태를 테스트합니다.
%JARVIS_PYTHON% -m jarvis_assistant --test-providers
if errorlevel 1 call :print_failure "Provider 상태 테스트 실패" "Python 패키지 설치 또는 Memory DB 초기화 문제" "python -m pip install -e . 를 실행한 뒤 다시 시도하세요."
exit /b %ERRORLEVEL%

:self_test
call :require_powershell
if errorlevel 1 exit /b %ERRORLEVEL%
powershell -NoProfile -ExecutionPolicy Bypass -File "%JARVIS_DIR%scripts\windows\test-jarvis.ps1"
if errorlevel 1 call :print_failure "Windows 실행 테스트 실패" "위 단계 중 하나가 실패했습니다." "출력된 단계별 원인과 해결 방법을 확인하세요."
exit /b %ERRORLEVEL%

:list_providers
call :python_cmd
if errorlevel 1 exit /b %ERRORLEVEL%
%JARVIS_PYTHON% -m jarvis_assistant --list-providers
exit /b %ERRORLEVEL%

:voice_status
call :python_cmd
if errorlevel 1 exit /b %ERRORLEVEL%
%JARVIS_PYTHON% -m jarvis_assistant --voice-status
exit /b %ERRORLEVEL%

:voice_listen
call :require_powershell
if errorlevel 1 exit /b %ERRORLEVEL%
powershell -NoProfile -ExecutionPolicy Bypass -File "%JARVIS_DIR%scripts\windows\jarvis-voice.ps1"
exit /b %ERRORLEVEL%

:tray_start
call :require_powershell
if errorlevel 1 exit /b %ERRORLEVEL%
call :python_cmd
if errorlevel 1 (
    pause
    exit /b %ERRORLEVEL%
)
powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%JARVIS_DIR%scripts\windows\jarvis-tray.ps1"
exit /b %ERRORLEVEL%

:gui_start
call :require_powershell
if errorlevel 1 exit /b %ERRORLEVEL%
powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%JARVIS_DIR%scripts\windows\jarvis-gui.ps1"
exit /b %ERRORLEVEL%

:settings_start
call :require_powershell
if errorlevel 1 exit /b %ERRORLEVEL%
powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%JARVIS_DIR%scripts\windows\jarvis-gui.ps1" -Settings
exit /b %ERRORLEVEL%

:memory_status
call :python_cmd
if errorlevel 1 exit /b %ERRORLEVEL%
%JARVIS_PYTHON% -m jarvis_assistant --memory-status
exit /b %ERRORLEVEL%

:startup
call :require_powershell
if errorlevel 1 exit /b %ERRORLEVEL%
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
if errorlevel 1 exit /b %ERRORLEVEL%
shift
if "%~1"=="" (
    %JARVIS_PYTHON% -m jarvis_assistant --provider windows_automation "상태 점검"
) else (
    %JARVIS_PYTHON% -m jarvis_assistant --provider windows_automation %*
)
exit /b %ERRORLEVEL%

:open_interpreter
call :python_cmd
if errorlevel 1 exit /b %ERRORLEVEL%
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

:action_calc
call :run_windows_action calc %*
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
echo   Jarvis.bat selftest
echo     메모장, PDF 생성, 다운로드 정리, 인터넷 검색, 장기 기억을 단계별로 테스트합니다.
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
echo   Jarvis.bat gui
echo     클릭형 Jarvis 제어판을 엽니다.
echo.
echo   Jarvis.bat 자비스
echo     클릭형 Jarvis 제어판을 엽니다.
echo.
echo   Jarvis.bat settings
echo     Memory DB, 다운로드 폴더, 프로젝트 폴더 설정창을 엽니다.
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
echo   Jarvis.bat calc
echo     계산기를 실행합니다.
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
%JARVIS_PYTHON% --version >nul 2>nul
if errorlevel 1 (
    call :print_failure "Python 실행 실패" "Python이 설치되어 있지 않거나 PATH에 없습니다." "Python 3.11 이상을 설치한 뒤 WindowsJarvisAssistant 폴더에서 python -m pip install -e . 를 실행하세요."
    exit /b 1
)
%JARVIS_PYTHON% -c "import jarvis_assistant" >nul 2>nul
if errorlevel 1 (
    echo Jarvis Python 패키지를 찾지 못했습니다. 자동 복구를 시작합니다...
    %JARVIS_PYTHON% -m pip install -e .
    if errorlevel 1 (
        call :print_failure "Jarvis 패키지 자동 설치 실패" "pip 설치가 실패했거나 인터넷/권한 문제가 있습니다." "WindowsJarvisAssistant 폴더에서 python -m pip install -e . 를 직접 실행하세요."
        exit /b 1
    )
)
exit /b 0

:run_windows_action
call :python_cmd
if errorlevel 1 exit /b %ERRORLEVEL%
set "JARVIS_ACTION=%~1"
shift
%JARVIS_PYTHON% -m jarvis_assistant --provider windows_automation "%JARVIS_ACTION% %*"
if errorlevel 1 call :print_failure "Windows 자동화 명령 실패" "명령 실행 중 오류가 발생했습니다." "Jarvis.bat selftest를 실행해 어느 단계가 실패하는지 확인하세요."
exit /b %ERRORLEVEL%

:require_powershell
where powershell >nul 2>nul
if errorlevel 1 (
    call :print_failure "PowerShell 실행 실패" "PowerShell을 찾을 수 없습니다." "Windows PowerShell을 활성화하거나 PowerShell 5 이상을 설치하세요."
    exit /b 1
)
exit /b 0

:print_failure
echo.
echo [Jarvis 오류]
echo - 실패 단계: %~1
echo - 원인 후보: %~2
echo - 해결 방법: %~3
echo.
exit /b 1
