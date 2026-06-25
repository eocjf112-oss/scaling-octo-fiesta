# Windows Jarvis AI Assistant

Windows Jarvis AI Assistant는 API 키 없이도 동작하는 로컬 AI 비서 시스템입니다.
현재 기본 목표는 Open Interpreter, Windows 자동화, 음성 입출력 준비를 하나의 Jarvis 실행 파일로 연결하는 것입니다.
ChatGPT와 Claude는 추후 API 키를 넣으면 같은 구조에서 쉽게 활성화할 수 있는 선택 기능으로 유지합니다.

## 목표

- **Local Jarvis**: API 없이 기본 안내와 라우팅 제공
- **Windows Automation**: Windows 상태 점검과 자동화 명령 라우팅 준비
- **Open Interpreter**: Windows 로컬 파일, 명령, 자동화 작업 실행
- **Voice I/O**: 음성 입력/출력 엔진을 연결할 수 있는 구조 준비
- **Startup**: Windows 시작 시 Jarvis 음성 리스너 자동 실행
- **Local Documents**: API 없이 엑셀, 워드, PDF 파일 생성
- **File Tools**: 파일 검색 및 Downloads 폴더 정리
- **Web Tools**: 기본 브라우저를 이용한 인터넷 검색
- **Memory DB**: SQLite 기반 장기 기억으로 사용자 정보, 프로젝트 상태, 작업 기록 저장
- **ChatGPT**: 추후 OpenAI API 키 입력 시 활성화
- **Claude**: 추후 Anthropic API 키 입력 시 활성화
- **Jarvis Router**: 사용자 요청을 적절한 Provider로 라우팅하고 같은 인터페이스로 응답 반환

## 현재 구현 범위

첫 번째 단계로 Provider 통합 코어를 구현했습니다.

```text
WindowsJarvisAssistant/
├── CHECKLIST.md
├── Jarvis.bat
├── README.md
├── pyproject.toml
├── .env.example
├── docs/open_interpreter_integration.md
├── scripts/windows/
│   ├── install-startup.ps1
│   ├── jarvis-voice.ps1
│   └── run-jarvis.ps1
├── src/jarvis_assistant/
│   ├── cli.py
│   ├── config.py
│   ├── diagnostics.py
│   ├── memory.py
│   ├── models.py
│   ├── router.py
│   ├── voice.py
│   ├── windows_actions.py
│   └── providers/
│       ├── local_provider.py
│       ├── anthropic_provider.py
│       ├── open_interpreter_provider.py
│       ├── openai_provider.py
│       ├── windows_automation_provider.py
│       └── registry.py
└── tests/
```

## 빠른 시작

### 1. Python 환경 준비

```powershell
cd Jarvis\Projects\WindowsJarvisAssistant
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Open Interpreter 연동이 필요하면 다음 선택 의존성을 설치합니다.

```powershell
python -m pip install -e ".[interpreter]"
```

> Open Interpreter 0.4.3은 `pkg_resources`를 사용하므로 현재는 `setuptools<81` 호환 설정이 필요합니다. `interpreter` extra에 이 제약을 포함했습니다.

### 2. API 없이 실행

Windows에서는 먼저 다음 명령을 사용할 수 있습니다.

```bat
Jarvis.bat
Jarvis.bat test
Jarvis.bat providers
Jarvis.bat voice
Jarvis.bat memory
Jarvis.bat windows status
Jarvis.bat startup install
Jarvis.bat listen
```

일반 요청:

```bat
Jarvis.bat "Jarvis 현재 상태를 알려줘"
```

`Jarvis.bat`을 인자 없이 실행하거나 더블클릭하면 시스템 트레이 대기 상태로 들어갑니다.
트레이 상태에서는 음성 리스너가 함께 실행되어 "자비스" 또는 "Jarvis" 호출어를 기다립니다.

Open Interpreter 요청:

```bat
Jarvis.bat oi "현재 폴더 구조를 요약해줘"
```

Windows 로컬 자동화:

```bat
Jarvis.bat excel "월간 계획"
Jarvis.bat word "회의록"
Jarvis.bat pdf "보고서"
Jarvis.bat search "계획"
Jarvis.bat organize
Jarvis.bat run notepad
Jarvis.bat web "오늘 날씨"
```

Windows 시작 시 자동 실행:

```bat
Jarvis.bat startup install
Jarvis.bat startup status
Jarvis.bat startup remove
```

음성 호출:

```bat
Jarvis.bat listen
```

`Jarvis.bat listen`은 Windows 음성 인식으로 "자비스" 또는 "Jarvis" 호출어를 기다린 뒤, 다음 음성 명령을 Jarvis에 전달합니다.

지원하는 기본 음성 명령 예시:

```text
자비스
메모장 열어줘

자비스
엑셀 만들어

자비스
PDF 만들어

자비스
다운로드 정리해

자비스
인터넷 검색해
```

### 3. 환경 설정

`.env.example`을 참고해 `.env`를 생성합니다. `Jarvis.bat`은 `.env`가 없으면 자동으로 생성합니다.

API 키는 지금 비워 두어도 됩니다.

```bat
Jarvis.bat env
```

기본값:

```env
JARVIS_DEFAULT_PROVIDER=local
JARVIS_PROVIDER_PRIORITY=windows_automation,open_interpreter,local,chatgpt,claude
JARVIS_MEMORY_DB_PATH=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

운영체제 환경 변수가 이미 설정되어 있으면 `.env`보다 우선합니다.

### 4. 추후 OpenAI/Claude API 연결

나중에 ChatGPT/Claude가 필요하면 선택 의존성을 설치하고 `.env`에 키를 넣으면 됩니다.

```powershell
python -m pip install -e ".[ai]"
```

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

키가 비어 있으면 Jarvis는 오류를 내지 않고 해당 Provider를 선택 기능으로 표시합니다.

### 5. Python CLI

```powershell
python -m jarvis_assistant "Jarvis 현재 상태를 알려줘"
python -m jarvis_assistant --test-providers
python -m jarvis_assistant --voice-status
python -m jarvis_assistant --memory-status
python -m jarvis_assistant --provider windows_automation "상태 점검"
python -m jarvis_assistant --provider open_interpreter --confirm-local-execution "현재 폴더의 파일 목록을 요약해줘"
```

Windows PowerShell 래퍼:

```powershell
.\scripts\windows\run-jarvis.ps1 -Prompt "내 PC 상태를 점검해줘" -Provider auto -ConfirmLocalExecution
```

Windows Batch 래퍼:

```bat
Jarvis.bat "오늘 할 일을 정리해줘"
Jarvis.bat providers
Jarvis.bat test
Jarvis.bat voice
Jarvis.bat memory
Jarvis.bat startup install
Jarvis.bat windows status
Jarvis.bat excel "월간 계획"
Jarvis.bat word "회의록"
Jarvis.bat pdf "보고서"
Jarvis.bat search "계획"
Jarvis.bat organize
Jarvis.bat run notepad
Jarvis.bat web "Windows 자동화"
Jarvis.bat oi "현재 폴더를 요약해줘"
```

Open Interpreter의 자세한 안전 정책은 `docs/open_interpreter_integration.md`를 참고하세요.

## Provider 선택 규칙

`--provider auto`는 다음 순서로 Provider를 선택합니다.

1. Windows 자동화 상태/자동화 성격이면 Windows Automation
2. 로컬 파일/명령 실행 성격이면 Open Interpreter
3. 기본 Provider(`JARVIS_DEFAULT_PROVIDER`)가 사용 가능하면 기본 Provider
4. 설정된 `JARVIS_PROVIDER_PRIORITY` 순서로 fallback
5. 마지막에는 항상 Local Jarvis Provider로 안전 응답

## 테스트

```powershell
python -m unittest discover -s tests
```

## 장기 기억 시스템

Jarvis는 실행 시 SQLite Memory DB를 자동으로 초기화하고 불러옵니다.

기본 DB 위치:

```text
Jarvis/Memory/jarvis_memory.sqlite3
```

저장되는 정보:

- 사용자 정보: 언어 선호, 커뮤니케이션 스타일, 워크스페이스 경로, OS 정보
- 프로젝트 진행 상황: Windows Jarvis AI Assistant 상태와 최근 실행 요약
- 작업 기록: 실행 명령, 선택 Provider, 응답 미리보기, 성공/실패 상태
- 메모리 이벤트: 향후 자동 학습/요약에 사용할 이벤트 기록

상태 확인:

```bat
Jarvis.bat memory
```

또는:

```powershell
python -m jarvis_assistant --memory-status
```

Memory DB는 개인 장기 기억이므로 Git에 커밋하지 않습니다.

## Windows 실사용 기능

### 시작 시 자동 실행

```bat
Jarvis.bat startup install
```

이 명령은 Windows 시작프로그램 폴더에 `JarvisStartup.bat`을 생성합니다.
다음 부팅부터 Jarvis가 시스템 트레이에 상주하고, 음성 리스너가 "자비스" 호출어를 기다립니다.

제거:

```bat
Jarvis.bat startup remove
```

### 음성으로 "자비스" 호출

```bat
Jarvis.bat listen
```

음성 리스너는 Windows `System.Speech`를 사용합니다.

흐름:

1. "자비스" 또는 "Jarvis"라고 말합니다.
2. Jarvis가 다음 명령을 기다립니다.
3. 음성 명령이 `Jarvis.bat`으로 전달됩니다.

시스템 트레이 상주 모드:

```bat
Jarvis.bat
```

트레이 아이콘 메뉴에서 다음 작업을 할 수 있습니다.

- Jarvis 상태 보기
- Memory 상태 보기
- 음성 리스너 시작/중지
- 시작 자동 실행 등록/제거
- Jarvis 종료

### 엑셀, 워드, PDF 생성

```bat
Jarvis.bat excel "월간 계획"
Jarvis.bat word "회의록"
Jarvis.bat pdf "보고서"
```

생성 위치:

```text
Jarvis/Documents/Generated
```

### 파일 검색 및 정리

```bat
Jarvis.bat search "계획"
Jarvis.bat organize
```

`organize`는 `Jarvis/Downloads` 폴더를 확장자 기준으로 분류합니다.

### 프로그램 실행

```bat
Jarvis.bat run notepad
Jarvis.bat run calc
```

### 인터넷 검색

```bat
Jarvis.bat web "오늘 날씨"
```

기본 브라우저로 Google 검색을 엽니다. 별도 API 키가 필요하지 않습니다.

## 보안 메모

- API 키는 선택 사항이며 코드나 문서에 저장하지 않습니다.
- API 키가 없어도 Jarvis는 Local/Windows Automation/Open Interpreter 준비 경로로 동작합니다.
- SQLite Memory DB는 개인 데이터이므로 Git에서 제외합니다.
- Open Interpreter는 로컬 명령을 실행할 수 있으므로 신뢰 가능한 프롬프트에만 사용합니다.
- Jarvis는 Open Interpreter 실행 전 위험 요청을 차단하고, 로컬 실행 요청에는 `--confirm-local-execution` 확인을 요구합니다.
- Open Interpreter 작업 디렉터리는 `JARVIS_WORKSPACE_ROOT` 내부로 제한됩니다.
- 로그에는 민감한 정보가 남지 않도록 별도 Sanitizer를 다음 단계에서 추가합니다.
