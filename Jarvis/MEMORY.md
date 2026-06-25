# 🧠 MEMORY.md — Jarvis 장기 기억 저장소

> **이 파일은 Jarvis AI의 장기 기억입니다.**
> 중요한 컨텍스트, 사용자 선호도, 진행 중인 작업, 학습된 패턴이 기록됩니다.
> 새로운 대화를 시작할 때 이 파일을 참조하여 연속성을 유지합니다.

---

## 📅 마지막 업데이트

**날짜:** 2026년 6월 25일  
**세션 ID:** JARVIS-INIT-001  
**상태:** 초기화 완료 ✅

---

## 👤 사용자 프로필 (User Profile)

```yaml
이름: [사용자 이름 - 업데이트 필요]
언어 선호: 한국어 (Korean)
시간대: [시간대 - 업데이트 필요]
직업: [직업 - 업데이트 필요]
주요 관심사: AI, 자동화, 개발, 생산성
커뮤니케이션 스타일: 직접적이고 효율적
```

---

## 🏗️ 현재 워크스페이스 상태 (Workspace Status)

### 초기화 완료 항목
- [x] 워크스페이스 폴더 구조 생성
- [x] README.md 작성
- [x] MASTER_PROMPT.md 작성
- [x] MEMORY.md 초기화 (이 파일)
- [x] 폴더 생성: Projects, Memory, Prompts, Automation, Documents, Logs, Temp

### 진행 중인 작업
- [ ] 사용자 프로필 완성
- [x] 첫 번째 프로젝트 시작: Windows Jarvis AI Assistant
- [ ] 자동화 스크립트 설정

---

## 📂 프로젝트 현황 (Project Status)

| 프로젝트 이름 | 상태 | 우선순위 | 마지막 업데이트 |
|--------------|------|---------|----------------|
| Jarvis 워크스페이스 설정 | ✅ 완료 | 높음 | 2026-06-25 |
| Windows Jarvis AI Assistant | 진행 중 | 높음 | 2026-06-25 |

---

## 💡 학습된 선호도 (Learned Preferences)

### 코딩 스타일
```
- 언어: Python, JavaScript/TypeScript 선호
- 들여쓰기: 4 스페이스 (Python), 2 스페이스 (JS/TS)
- 주석: 한국어로 작성
- 문서화: README.md 필수
```

### 작업 방식
```
- 큰 작업은 작은 단위로 분할
- 각 단계마다 확인 및 피드백 선호
- 코드보다 결과물에 집중
- 자동화 가능한 작업은 최대한 자동화
```

### 커뮤니케이션
```
- 기본 언어: 한국어
- 기술 용어: 영문 병기 선호 (예: 머신러닝(Machine Learning))
- 응답 형식: 구조화된 마크다운
- 길이: 필요한 만큼만, 불필요한 내용 제외
```

---

## 🔑 중요 컨텍스트 (Important Context)

### 환경 정보
```yaml
운영체제: Linux (Ubuntu)
쉘: Bash
워크스페이스: /workspace/Jarvis
Git 브랜치: cursor/jarvis-workspace-setup-b80e
```

### 중요 경로
```
워크스페이스 루트: /workspace/Jarvis/
프로젝트: /workspace/Jarvis/Projects/
기억 저장소: /workspace/Jarvis/Memory/
프롬프트: /workspace/Jarvis/Prompts/
자동화: /workspace/Jarvis/Automation/
문서: /workspace/Jarvis/Documents/
로그: /workspace/Jarvis/Logs/
임시: /workspace/Jarvis/Temp/
```

---

## 🗓️ 세션 기록 (Session History)

### 세션 001 — 2026년 6월 25일
**목표:** Jarvis 워크스페이스 초기 설정  
**완료 작업:**
- 워크스페이스 구조 설계 및 생성
- 핵심 문서 3개 작성 (README.md, MASTER_PROMPT.md, MEMORY.md)
- 7개 폴더 생성 (Projects, Memory, Prompts, Automation, Documents, Logs, Temp)
- Git 브랜치 생성 및 초기 커밋

**학습 내용:**
- 사용자는 한국어 설명을 선호
- 체계적인 폴더 구조와 문서화를 중요하게 생각
- Jarvis를 개인 AI 엔지니어로 활용하고자 함

**다음 세션 목표:**
- 사용자 프로필 업데이트
- 첫 번째 실제 프로젝트 착수

### 세션 002 — 2026년 6월 25일
**목표:** Windows용 Jarvis AI Assistant 시작

**완료 작업:**
- `Jarvis/Projects/WindowsJarvisAssistant` 프로젝트 생성
- ChatGPT, Claude, Open Interpreter를 공통 Provider 인터페이스로 연결하는 코어 스캐폴드 구현
- 환경 변수 기반 설정, Provider Registry, 자동 Router, CLI 진입점 추가
- Windows PowerShell 실행 스크립트와 기본 단위 테스트 추가
- 단계별 실행 체크리스트 작성

**다음 세션 목표:**
- CLI 대화형 모드 추가
- Open Interpreter 안전 승인 레이어 설계
- 대화 메모리 저장소 최소 구현

### 세션 003 — 2026년 6월 25일
**목표:** Open Interpreter 안전 연동 시작

**완료 작업:**
- Python 가상환경 생성 및 Open Interpreter 0.4.3 설치
- `python3.12-venv` 시스템 패키지 필요 확인 및 설치
- Open Interpreter CLI 옵션 확인: `--stdin`, `--safe_mode ask`, `--disable_telemetry`, `--plain`
- `setuptools 82.0.1`에서 `pkg_resources`가 제거되어 Open Interpreter 0.4.3 CLI가 실패하는 호환성 이슈 확인
- 현재 호환을 위해 `setuptools<81` 제약 필요 확인
- Jarvis Open Interpreter 안전 정책 구현: 위험 요청 차단, 로컬 실행 확인 플래그, Jarvis 워크스페이스 내부 작업 폴더 제한
- Open Interpreter 안전 연동 가이드 문서 작성

**다음 세션 목표:**
- Open Interpreter 실행 로그 Sanitizer 구현
- 실행 전 명령 Preview 및 승인 UI 설계
- Open Interpreter 실패/타임아웃 복구 정책 추가

### 세션 004 — 2026년 6월 25일
**목표:** OpenAI, Anthropic, Open Interpreter 통합 환경 설정 준비

**완료 작업:**
- `.env.example`을 한국어 설명 중심으로 정리
- OpenAI API 키와 Anthropic API 키 입력 위치를 빈 값으로 표시
- 로컬 `.env` 파일 생성: 실제 키는 비워둠
- 보안을 위해 `.env`는 Git 제외 상태 유지
- Jarvis CLI가 프로젝트 `.env`를 자동 로딩하도록 설정 로더 개선
- `JARVIS_PROVIDER_PRIORITY`를 추가해 ChatGPT, Claude, Open Interpreter가 하나의 Jarvis Router에서 함께 동작할 준비 완료

**다음 세션 목표:**
- 실제 API 키가 설정된 환경에서 ChatGPT/Claude Provider smoke test
- Provider별 실패 fallback 정책 강화
- 통합 대화 모드에서 세 Provider를 선택/전환하는 UX 추가

### 세션 005 — 2026년 6월 25일
**목표:** API 키 입력 및 Jarvis.bat 기반 Provider 테스트 준비

**완료 작업:**
- OpenAI/Anthropic SDK 설치 상태 확인
- 현재 `.env`의 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`가 비어 있음을 확인
- Windows용 `Jarvis.bat` 추가
- `Jarvis.bat env`로 `.env`를 메모장으로 열 수 있게 구성
- `Jarvis.bat test`로 ChatGPT, Claude, Open Interpreter 연결 상태를 한 번에 점검하도록 구성
- `python -m jarvis_assistant --test-providers` 진단 명령 추가
- API 키가 비어 있으면 실제 호출 없이 `건너뜀`으로 보고하고, 키가 있으면 실제 API 호출을 수행하는 구조 준비

**다음 세션 목표:**
- 사용자가 실제 API 키를 `.env`에 입력한 뒤 `Jarvis.bat test` 실행
- ChatGPT/Claude 실제 응답 확인
- Provider 실패 시 자동 fallback 정책 강화

---

## 📝 메모 및 아이디어 (Notes & Ideas)

### 개선 아이디어
- [ ] 자동 로그 정리 스크립트 (`Automation/cleanup_logs.py`)
- [ ] 프로젝트 템플릿 생성 (`Prompts/project_template.md`)
- [ ] 주간 리포트 자동 생성 (`Automation/weekly_report.py`)
- [ ] Memory 자동 백업 시스템

### 기술 스택 후보
- **백엔드:** FastAPI + Python
- **프론트엔드:** Next.js + TypeScript
- **데이터베이스:** PostgreSQL + Redis
- **AI:** OpenAI GPT-4 / Anthropic Claude
- **배포:** Docker + AWS/GCP

---

## ⚠️ 주의 사항 (Cautions)

```
1. 이 파일은 AI가 읽고 쓰는 핵심 기억 파일입니다.
2. 중요한 변경 사항은 반드시 날짜와 함께 기록하세요.
3. 민감한 정보(비밀번호, API 키 등)는 이 파일에 저장하지 마세요.
4. 정기적으로 이 파일을 검토하고 오래된 내용을 정리하세요.
5. 기억이 너무 길어지면 Archives/MEMORY_YYYY_MM.md로 분리하세요.
```

---

## 🔄 업데이트 방법

새로운 정보를 기억에 추가할 때는 다음 형식을 사용하세요:

```markdown
### [날짜] — [주제]
**내용:** [기억할 내용]
**태그:** #프로젝트 #기술 #결정사항
```

---

*이 파일은 Jarvis AI 시스템의 핵심입니다. 지속적으로 업데이트하여 AI의 컨텍스트를 풍부하게 유지하세요.*

**버전:** v1.0  
**초기화:** 2026년 6월 25일
