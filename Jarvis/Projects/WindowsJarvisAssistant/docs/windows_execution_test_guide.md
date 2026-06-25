# Windows 실제 실행 테스트 가이드

이 문서는 Windows PC에서 Jarvis를 직접 실행하고 핵심 기능을 확인하는 절차입니다. 모든 기능은 OpenAI/Anthropic API 키 없이 먼저 동작하도록 구성되어 있습니다.

## 1. 실행 위치

명령 프롬프트 또는 PowerShell에서 아래 폴더로 이동합니다.

```bat
cd Jarvis\Projects\WindowsJarvisAssistant
```

## 2. 최초 준비

Python 패키지를 설치합니다.

```bat
python -m pip install -e .
```

Open Interpreter까지 사용할 경우:

```bat
python -m pip install -e ".[interpreter]"
```

> API 키는 필요하지 않습니다. `.env`의 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`는 비워 두어도 됩니다.

## 3. Jarvis.bat 실행 방법

### 트레이 대기 상태로 실행

```bat
Jarvis.bat
```

성공 기준:

- Windows 시스템 트레이에 Jarvis 아이콘이 표시됩니다.
- 음성 리스너가 함께 실행되어 "자비스" 호출어를 기다립니다.

실패 시:

- 원인 후보: PowerShell 실행 정책, Python 미설치, 경로 문제
- 해결:

```bat
Jarvis.bat selftest
python --version
python -m pip install -e .
```

## 4. 전체 자동 테스트

```bat
Jarvis.bat selftest
```

테스트 항목:

1. 메모장 열기
2. PDF 생성
3. 다운로드 폴더 정리
4. 인터넷 검색
5. 장기 기억 저장/불러오기

성공 기준:

```text
모든 Windows 실행 테스트가 통과했습니다.
```

## 5. 메모장 열기 테스트

```bat
Jarvis.bat run notepad
```

또는 음성:

```text
자비스
메모장 열어줘
```

성공 기준:

- Windows 메모장이 열립니다.

실패 시:

- 원인 후보: Windows 기본 앱 실행 차단, PATH 문제
- 해결:

```bat
notepad
Jarvis.bat selftest
```

## 6. PDF 생성 테스트

```bat
Jarvis.bat pdf "Windows 실행 테스트"
```

성공 기준:

- 아래 폴더에 PDF가 생성됩니다.

```text
Jarvis\Documents\Generated
```

실패 시:

- 원인 후보: 폴더 쓰기 권한 부족
- 해결:
  - `Jarvis\Documents\Generated` 폴더를 직접 만들어 봅니다.
  - 프로젝트 폴더가 읽기 전용인지 확인합니다.

## 7. 다운로드 폴더 정리 테스트

```bat
Jarvis.bat organize
```

성공 기준:

- `Jarvis\Downloads` 폴더가 생성되거나, 내부 파일이 확장자 기준으로 분류됩니다.

실패 시:

- 원인 후보: 파일 이동 권한 부족, 파일이 다른 프로그램에서 열려 있음
- 해결:
  - 열려 있는 파일을 닫습니다.
  - `Jarvis\Downloads` 폴더 권한을 확인합니다.

## 8. 인터넷 검색 테스트

```bat
Jarvis.bat web "오늘 날씨"
```

또는 음성:

```text
자비스
인터넷 검색해
```

성공 기준:

- 기본 브라우저가 열리고 Google 검색 페이지가 표시됩니다.

실패 시:

- 원인 후보: 기본 브라우저 미설정, URL 실행 차단
- 해결:

```bat
start https://www.google.com
```

Windows 설정에서 기본 브라우저를 지정합니다.

## 9. 장기 기억 저장/불러오기 테스트

```bat
Jarvis.bat memory
Jarvis.bat "장기 기억 테스트"
Jarvis.bat memory
```

성공 기준:

- `작업 기록` 개수가 증가합니다.
- 컴퓨터를 껐다 켜도 아래 DB 파일이 유지됩니다.

```text
Jarvis\Memory\jarvis_memory.sqlite3
```

실패 시:

- 원인 후보: SQLite DB 파일 생성 권한 부족, DB 파일 잠김
- 해결:
  - 실행 중인 Jarvis를 종료합니다.
  - `Jarvis\Memory` 폴더 권한을 확인합니다.
  - 다시 `Jarvis.bat memory`를 실행합니다.

## 10. Windows 시작 시 자동 실행

등록:

```bat
Jarvis.bat startup install
```

상태 확인:

```bat
Jarvis.bat startup status
```

제거:

```bat
Jarvis.bat startup remove
```

성공 기준:

- 다음 부팅 후 Jarvis가 시스템 트레이에 상주합니다.

## 11. 음성 호출 테스트

```bat
Jarvis.bat listen
```

말하기:

```text
자비스
메모장 열어줘
```

성공 기준:

- 호출어 인식 후 명령이 실행됩니다.

실패 시:

- 원인 후보: 마이크 권한, Windows 음성 인식 언어 설정, 입력 장치 문제
- 해결:
  - Windows 설정에서 마이크 권한을 허용합니다.
  - 기본 입력 장치를 확인합니다.
  - Windows 음성 인식 언어에 한국어 또는 영어 인식이 가능한지 확인합니다.
