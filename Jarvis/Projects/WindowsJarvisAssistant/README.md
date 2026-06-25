# Windows Jarvis AI Assistant

Windows Jarvis AI Assistant는 Open Interpreter, ChatGPT, Claude를 하나의 로컬 AI 비서 시스템으로 연결하기 위한 프로젝트입니다.

## 목표

- **ChatGPT**: 일반 대화, 문서 작성, 코드 설명, 빠른 질의응답
- **Claude**: 긴 문맥 분석, 설계 검토, 문서/코드 리뷰
- **Open Interpreter**: Windows 로컬 파일, 명령, 자동화 작업 실행
- **Jarvis Router**: 사용자 요청을 적절한 Provider로 라우팅하고 같은 인터페이스로 응답 반환

## 현재 구현 범위

첫 번째 단계로 Provider 통합 코어를 구현했습니다.

```text
WindowsJarvisAssistant/
├── CHECKLIST.md
├── README.md
├── pyproject.toml
├── .env.example
├── docs/open_interpreter_integration.md
├── scripts/windows/run-jarvis.ps1
├── src/jarvis_assistant/
│   ├── cli.py
│   ├── config.py
│   ├── models.py
│   ├── router.py
│   └── providers/
│       ├── anthropic_provider.py
│       ├── open_interpreter_provider.py
│       ├── openai_provider.py
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

실제 ChatGPT/Claude SDK 연동이 필요하면 다음 선택 의존성을 설치합니다.

```powershell
python -m pip install -e ".[ai]"
```

Open Interpreter 연동이 필요하면 다음 선택 의존성을 설치합니다.

```powershell
python -m pip install -e ".[interpreter]"
```

> Open Interpreter 0.4.3은 `pkg_resources`를 사용하므로 현재는 `setuptools<81` 호환 설정이 필요합니다. `interpreter` extra에 이 제약을 포함했습니다.

### 2. 환경 변수 설정

`.env.example`을 참고해 `.env`를 생성합니다. Jarvis CLI는 프로젝트 루트의 `.env`를 자동으로 읽습니다.

```powershell
Copy-Item .env.example .env
```

`.env`에서 아래 위치에 실제 키를 입력합니다. 현재 저장소의 예시 파일과 로컬 `.env`는 모두 빈 값으로 유지합니다.

```powershell
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
JARVIS_DEFAULT_PROVIDER=chatgpt
JARVIS_PROVIDER_PRIORITY=chatgpt,claude,open_interpreter
JARVIS_WORKSPACE_ROOT=C:\Users\you\Jarvis
```

Open Interpreter CLI를 사용할 경우:

```powershell
python -m pip install -e ".[interpreter]"
JARVIS_OPEN_INTERPRETER_COMMAND=.\.venv\Scripts\interpreter.exe
JARVIS_OPEN_INTERPRETER_WORKDIR=C:\Users\you\Jarvis\Temp\OpenInterpreter
JARVIS_OPEN_INTERPRETER_REQUIRE_CONFIRMATION=true
```

운영체제 환경 변수가 이미 설정되어 있으면 `.env`보다 우선합니다.

### 3. 실행

```powershell
python -m jarvis_assistant "오늘 할 일을 정리해줘"
python -m jarvis_assistant --provider claude "이 설계를 검토해줘"
python -m jarvis_assistant --provider open_interpreter --confirm-local-execution "현재 폴더의 파일 목록을 요약해줘"
```

Windows PowerShell 래퍼:

```powershell
.\scripts\windows\run-jarvis.ps1 -Prompt "내 PC 상태를 점검해줘" -Provider auto -ConfirmLocalExecution
```

Open Interpreter의 자세한 안전 정책은 `docs/open_interpreter_integration.md`를 참고하세요.

## Provider 선택 규칙

`--provider auto`는 다음 순서로 Provider를 선택합니다.

1. 로컬 파일/명령/Windows 자동화 성격이면 Open Interpreter
2. 기본 Provider(`JARVIS_DEFAULT_PROVIDER`)가 사용 가능하면 기본 Provider
3. 사용 가능한 Provider 중 ChatGPT, Claude, Open Interpreter 순서로 선택

## 테스트

```powershell
python -m unittest discover -s tests
```

## 보안 메모

- API 키는 코드나 문서에 저장하지 않습니다.
- Open Interpreter는 로컬 명령을 실행할 수 있으므로 신뢰 가능한 프롬프트에만 사용합니다.
- Jarvis는 Open Interpreter 실행 전 위험 요청을 차단하고, 로컬 실행 요청에는 `--confirm-local-execution` 확인을 요구합니다.
- Open Interpreter 작업 디렉터리는 `JARVIS_WORKSPACE_ROOT` 내부로 제한됩니다.
- 로그에는 민감한 정보가 남지 않도록 별도 Sanitizer를 다음 단계에서 추가합니다.
