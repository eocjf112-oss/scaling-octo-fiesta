# Windows Jarvis AI Assistant 단계별 체크리스트

## 0. 현재 프로젝트 분석

- [x] 루트 워크스페이스 문서 확인: `README.md`, `MASTER_PROMPT.md`, `MEMORY.md`
- [x] 현재 구조 확인: Jarvis 워크스페이스 초기 문서와 기본 폴더만 존재
- [x] 새 실제 프로젝트 위치 결정: `Jarvis/Projects/WindowsJarvisAssistant`

## 1. Provider 통합 코어 구축

- [x] 공통 요청/응답 모델 정의
- [x] ChatGPT Provider 어댑터 추가
- [x] Claude Provider 어댑터 추가
- [x] Open Interpreter Provider 어댑터 추가
- [x] 환경 변수 기반 설정 로더 추가
- [x] `.env` 자동 로딩 추가
- [x] OpenAI/Anthropic API 키 입력 위치 문서화
- [x] ChatGPT, Claude, Open Interpreter Provider 우선순위 설정 추가
- [x] Provider Registry와 자동 Router 추가
- [x] CLI 진입점 추가
- [x] ChatGPT/Claude/Open Interpreter 통합 연결 테스트 명령 추가
- [x] Windows PowerShell 실행 스크립트 추가
- [x] Windows `Jarvis.bat` 실행 파일 추가
- [x] 기본 단위 테스트 추가

## 2. Windows 데스크톱 실행 기반

- [ ] Windows 시작 메뉴/트레이 실행 방식 결정
- [ ] 로컬 설정 파일 저장 위치 정의
- [ ] 음성 입력/출력(Voice I/O) 후보 라이브러리 비교
- [x] 안전한 로컬 명령 실행 정책 설계
- [ ] Windows 권한 상승이 필요한 작업 분리

## 3. 대화 메모리와 작업 컨텍스트

- [ ] 단기 대화 메모리 저장소 구현
- [ ] 장기 메모리 저장소 구현
- [ ] 사용자 선호/반복 작업 기록 스키마 설계
- [ ] 민감 정보 필터링 규칙 추가
- [ ] Memory 검색 및 요약 기능 추가

## 4. Open Interpreter 실행 안전장치

- [ ] 실행 전 명령 Preview 추가
- [x] 위험 명령 차단/승인 정책 추가
- [x] 작업별 샌드박스 디렉터리 분리
- [ ] 실행 로그 Sanitizer 추가
- [ ] 실패 복구 및 Rollback 가이드 추가

## 5. ChatGPT/Claude 고급 라우팅

- [ ] 요청 유형 분류기 추가
- [ ] 긴 문맥은 Claude 우선, 빠른 응답은 ChatGPT 우선 정책 추가
- [ ] Provider 실패 시 Fallback 정책 추가
- [ ] 비용/토큰 사용량 추적 추가
- [ ] 사용자별 기본 Provider 설정 추가

## 6. UI/UX

- [ ] CLI 대화형 모드 추가
- [ ] Windows 데스크톱 UI 후보 결정
- [ ] 대화 기록 화면 설계
- [ ] 작업 실행 승인 화면 설계
- [ ] 음성 명령 버튼/핫키 설계

## 7. 배포 및 운영

- [ ] Windows 설치 스크립트 고도화
- [ ] `.env`/설정 마이그레이션 도구 추가
- [ ] 자동 업데이트 전략 설계
- [ ] 오류 리포트 및 진단 로그 추가
- [ ] 릴리스 체크리스트 작성

## 다음 즉시 작업

1. 실제 API 키 입력 후 `Jarvis.bat test`로 ChatGPT/Claude 응답 확인
2. Open Interpreter 실행 로그 Sanitizer 추가
3. 실행 전 명령 Preview/승인 UI 설계
4. CLI 대화형 모드 추가
5. 대화 메모리 저장소의 최소 구현 추가
