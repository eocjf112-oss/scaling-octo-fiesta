#!/usr/bin/env bash
# Jarvis AI Assistant — Linux/macOS 런처

set -euo pipefail

if [ ! -d "venv" ]; then
    echo "[오류] 가상환경이 없습니다. setup.sh를 먼저 실행하세요."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "[오류] .env 파일이 없습니다. setup.sh를 먼저 실행하세요."
    exit 1
fi

source venv/bin/activate
python jarvis.py "$@"
