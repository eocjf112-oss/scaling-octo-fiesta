# 🤖 Jarvis AI Assistant for Windows

> **ChatGPT + Claude + Open Interpreter 통합 AI 시스템**

---

## 📌 프로젝트 개요

Jarvis AI Assistant는 OpenAI의 ChatGPT, Anthropic의 Claude, Open Interpreter를 하나의 시스템으로 연결하는 Windows용 개인 AI 어시스턴트입니다.

단일 인터페이스에서 세 가지 AI를 자유롭게 전환하며 사용하고, 대화 내용은 자동으로 `MEMORY.md`에 저장되어 연속성을 유지합니다.

---

## ⚡ 빠른 시작

### 1. 설치
```bat
install.bat
```

### 2. API 키 설정
`.env` 파일을 열고 API 키를 입력합니다:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. 실행
```bat
jarvis.bat
```

또는 터미널에서:
```bash
python jarvis.py
```

---

## 🗂️ 프로젝트 구조

```
jarvis-ai-assistant/
│
├── jarvis.py               # 메인 진입점
├── jarvis.bat              # Windows 실행 스크립트
├── install.bat             # Windows 설치 스크립트
├── requirements.txt        # Python 의존성
├── config.yaml             # 시스템 설정
├── .env.example            # 환경변수 템플릿
│
├── core/                   # 핵심 모듈
│   ├── config.py           # 설정 관리
│   ├── logger.py           # 로깅 시스템
│   ├── memory.py           # 장기 기억 (MEMORY.md)
│   └── router.py           # AI 라우터 & 오케스트레이터
│
├── agents/                 # AI 에이전트
│   ├── openai_agent.py     # ChatGPT (GPT-4o)
│   ├── claude_agent.py     # Claude (claude-3-5-sonnet)
│   └── interpreter_agent.py # Open Interpreter
│
├── cli/                    # 인터페이스
│   └── main.py             # 대화형 CLI
│
└── prompts/                # 프롬프트 라이브러리
    └── system_prompts.py   # AI별 시스템 프롬프트
```

---

## 🎮 사용법

### 대화형 모드

```
python jarvis.py
```

### 슬래시 명령어로 AI 전환

| 명령어 | 설명 |
|--------|------|
| `/chatgpt [메시지]` | ChatGPT로 대화 |
| `/claude [메시지]` | Claude로 대화 |
| `/interpreter [작업]` | Open Interpreter로 코드 실행 |
| `/gpt [메시지]` | ChatGPT 단축키 |
| `/auto` | 자동 AI 선택 모드 |
| `/ai chatgpt` | 기본 AI 변경 |
| `/status` | 연결 상태 확인 |
| `/reset` | 대화 히스토리 초기화 |
| `/memory` | 기억 요약 보기 |
| `/save` | 세션 저장 |
| `/help` | 도움말 |
| `/exit` | 종료 |

### 단일 질문 모드

```bash
python jarvis.py "오늘 할 일 목록 작성해줘"
python jarvis.py --ai claude "이 코드를 리뷰해줘"
python jarvis.py --status
```

---

## 🔀 AI 자동 선택 규칙

`auto` 모드에서 Jarvis는 메시지를 분석하여 최적의 AI를 선택합니다:

| 키워드 | 선택되는 AI |
|--------|------------|
| 코드 실행, 파일 만들어, 자동화 | Open Interpreter |
| 분석, 검토, 리뷰, 긴 글 | Claude |
| 아이디어, 창의, 추천 | ChatGPT |
| 그 외 | ChatGPT (기본값) |

`config.yaml`의 `router.rules`를 수정하여 커스터마이징 가능합니다.

---

## 🧠 메모리 시스템

- 세션 종료 시 자동으로 `C:\Jarvis\MEMORY.md`에 저장
- 다음 세션 시작 시 이전 컨텍스트를 자동으로 불러옴
- 사용자 선호도, 프로젝트 현황, 학습 내용 누적

---

## ⚙️ 설정

### 환경변수 (`.env`)

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | 필수 |
| `ANTHROPIC_API_KEY` | Anthropic API 키 | 필수 |
| `JARVIS_DEFAULT_AI` | 기본 AI | `auto` |
| `JARVIS_LANGUAGE` | 응답 언어 | `ko` |
| `JARVIS_WORKSPACE` | 워크스페이스 경로 | `C:\Jarvis` |

### 모델 설정 (`config.yaml`)

```yaml
ai:
  chatgpt:
    model: gpt-4o
    temperature: 0.7
  claude:
    model: claude-3-5-sonnet-20241022
    temperature: 0.7
  interpreter:
    auto_run: false    # 코드 자동 실행 (보안상 false 권장)
    safe_mode: ask
```

---

## 📋 요구사항

- **Windows** 10/11
- **Python** 3.11 이상
- **API 키**: OpenAI, Anthropic (각각 선택적)

---

## 🔐 보안 주의사항

- `.env` 파일은 절대 GitHub에 업로드하지 마세요
- Open Interpreter의 `auto_run: false` 설정 유지를 권장합니다
- API 키는 환경변수로만 관리하세요

---

**버전:** 1.0.0  
**언어:** 한국어 기본  
**라이선스:** MIT
