#!/usr/bin/env bash
# Jarvis AI Assistant — Linux/macOS 초기 설정 스크립트

set -euo pipefail

echo ""
echo "================================================"
echo "  Jarvis AI Assistant — Linux/macOS 초기 설정"
echo "================================================"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "[오류] Python 3이 설치되지 않았습니다."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "[1/4] Python 버전 확인..."
python3 --version
echo ""

echo "[2/4] 가상환경 생성 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  가상환경 생성 완료!"
else
    echo "  기존 가상환경을 사용합니다."
fi
echo ""

echo "[3/4] 의존성 설치 중..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  설치 완료!"
echo ""

echo "[4/4] 환경 설정 파일 확인..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  .env 파일이 생성되었습니다."
    echo ""
    echo "  [중요] .env 파일을 편집하여 API 키를 입력하세요:"
    echo "    OPENAI_API_KEY   = OpenAI API 키"
    echo "    ANTHROPIC_API_KEY = Anthropic API 키"
    echo ""
    echo "  나노 편집기로 열기: nano .env"
    echo "  VS Code로 열기: code .env"
else
    echo "  .env 파일이 이미 존재합니다."
fi
echo ""

echo "================================================"
echo "  설정 완료! 아래 명령어로 Jarvis를 실행하세요:"
echo "    source venv/bin/activate && python jarvis.py"
echo "  또는: ./start_jarvis.sh"
echo "================================================"
echo ""
