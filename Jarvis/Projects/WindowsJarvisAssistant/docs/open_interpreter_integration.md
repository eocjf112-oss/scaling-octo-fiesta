# Open Interpreter 안전 연동 가이드

## 목적

Jarvis는 Open Interpreter를 Windows 로컬 자동화 엔진으로 사용합니다. 다만 Open Interpreter는 파일 수정, 명령 실행, 패키지 설치처럼 실제 시스템에 영향을 줄 수 있으므로 Jarvis가 먼저 안전 정책을 적용한 뒤 실행합니다.

## 실행 구조

```text
사용자 요청
  -> Jarvis CLI
  -> ChatRequest(metadata.confirm_local_execution)
  -> OpenInterpreterSafetyPolicy
  -> OpenInterpreterProvider
  -> Open Interpreter CLI(stdin, safe_mode ask)
  -> Jarvis 전용 작업 폴더
```

## 기본 안전 정책

| 단계 | 동작 |
|------|------|
| 위험 요청 차단 | 디스크 포맷, 시스템 초기화, System32 삭제 등은 즉시 차단 |
| 로컬 실행 확인 | 파일/폴더/명령/설치/삭제/수정 요청은 확인 플래그 필요 |
| 작업 폴더 제한 | `JARVIS_OPEN_INTERPRETER_WORKDIR`는 `JARVIS_WORKSPACE_ROOT` 내부여야 함 |
| Open Interpreter 안전 모드 | CLI 실행 시 `--safe_mode ask` 사용 |
| Telemetry 비활성화 | CLI 실행 시 `--disable_telemetry` 사용 |

## Python 환경 설정

Ubuntu/Cloud Agent 환경:

```bash
sudo apt-get update
sudo apt-get install -y python3.12-venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[interpreter]"
.venv/bin/python -m pip install "setuptools<81"
```

Windows PowerShell 환경:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[interpreter]"
python -m pip install "setuptools<81"
```

> Open Interpreter 0.4.3은 `pkg_resources`를 사용합니다. 최신 `setuptools`에서는 이 모듈이 제거되어 있으므로 현재는 `setuptools<81` 호환 설정이 필요합니다.

## 환경 변수

```powershell
$env:JARVIS_WORKSPACE_ROOT = "C:\Users\you\Jarvis"
$env:JARVIS_OPEN_INTERPRETER_COMMAND = ".\.venv\Scripts\interpreter.exe"
$env:JARVIS_OPEN_INTERPRETER_WORKDIR = "C:\Users\you\Jarvis\Temp\OpenInterpreter"
$env:JARVIS_OPEN_INTERPRETER_REQUIRE_CONFIRMATION = "true"
$env:JARVIS_OPEN_INTERPRETER_AUTO_YES = "false"
```

## 실행 예시

확인 없이 로컬 작업을 요청하면 Jarvis가 차단합니다.

```powershell
python -m jarvis_assistant --provider open_interpreter "파일 목록을 확인해줘"
```

명시적으로 허용하려면 다음처럼 실행합니다.

```powershell
python -m jarvis_assistant --provider open_interpreter --confirm-local-execution "파일 목록을 확인해줘"
```

PowerShell 래퍼:

```powershell
.\scripts\windows\run-jarvis.ps1 -Provider open_interpreter -ConfirmLocalExecution -Prompt "파일 목록을 확인해줘"
```
