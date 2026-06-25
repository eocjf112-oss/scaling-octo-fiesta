# Jarvis AI Assistant — jarvis-core

> ChatGPT + Claude + Open Interpreter 통합 AI 어시스턴트

---

## 개요

`jarvis-core`는 세 가지 AI 시스템을 하나의 인터페이스로 통합한 Jarvis의 핵심 엔진입니다.

| 시스템 | 역할 |
|--------|------|
| **Claude (Anthropic)** | 복잡한 분석, 장문 작성, 기본 대화 |
| **ChatGPT (OpenAI)** | 일반 질문, 코드 설명, 창의적 작업 |
| **Open Interpreter** | 로컬 코드 실행, 파일 조작, 시스템 명령 |

---

## 빠른 시작 (Windows)

### 1. 초기 설정

```bat
setup.bat
```

`.env` 파일이 자동으로 열립니다. API 키를 입력하세요:

```
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Jarvis 실행

```bat
start_jarvis.bat
```

---

## 빠른 시작 (Linux/macOS)

```bash
./setup.sh
./start_jarvis.sh
```

---

## 사용법

### 대화형 모드

```
You> 파이썬으로 피보나치 수열을 계산하는 함수를 작성해줘
```

### 명시적 AI 선택

```
You> @claude 이 코드를 리뷰해줘 [코드 붙여넣기]
You> @openai GPT-4의 최신 기능을 설명해줘
You> @run 현재 폴더의 모든 .py 파일 목록을 보여줘
```

### 명령어

| 명령어 | 설명 |
|--------|------|
| `/help` | 도움말 |
| `/status` | AI 연결 상태 확인 |
| `/switch claude` | Claude로 전환 |
| `/switch openai` | ChatGPT로 전환 |
| `/switch interpreter` | Open Interpreter로 전환 |
| `/memory` | 장기 기억 보기 |
| `/session` | 세션 통계 |
| `/reset` | 대화 초기화 |
| `/exit` | 종료 |

---

## 자동 라우팅

별도 지정 없이 메시지를 보내면 Jarvis가 내용에 따라 자동으로 최적의 AI를 선택합니다:

- "파일 만들어줘", "실행해", "터미널" → **Open Interpreter**
- 일반 질문/분석 → 설정된 기본 AI (기본값: Claude)

---

## 프로젝트 구조

```
jarvis-core/
├── jarvis.py              # 메인 진입점 (CLI 엔트리포인트)
├── cli.py                 # Rich 기반 터미널 UI
├── orchestrator.py        # AI 통합 오케스트레이터
├── config.py              # 설정 관리 (Pydantic)
│
├── providers/
│   ├── base_provider.py       # 추상 기본 클래스
│   ├── openai_provider.py     # ChatGPT 연동
│   ├── claude_provider.py     # Claude 연동
│   └── interpreter_provider.py # Open Interpreter 연동
│
├── memory/
│   ├── memory_manager.py      # 장기 기억 (JSON + MEMORY.md)
│   └── session_manager.py     # 세션 생명주기 관리
│
├── tests/                 # 단위 테스트
│
├── .env.example           # 환경변수 템플릿
├── requirements.txt       # Python 의존성
├── setup.bat              # Windows 초기 설정
├── start_jarvis.bat       # Windows 런처
├── start_jarvis.ps1       # PowerShell 런처
├── setup.sh               # Linux/macOS 설정
└── start_jarvis.sh        # Linux/macOS 런처
```

---

## API 키 발급

- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

---

## 요구사항

- Python 3.10 이상
- Windows 10/11, macOS 12+, Ubuntu 20.04+

---

*버전: v1.0 | 2026년 6월 25일*
