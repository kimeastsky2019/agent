#!/bin/bash

# 백엔드 시작 스크립트

echo "🚀 Energy Orchestrator Platform - Backend 시작"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    echo ""
    echo "설치 방법:"
    echo "1. Homebrew: brew install python3"
    echo "2. 또는 https://www.python.org/ 에서 다운로드"
    exit 1
fi

echo "✅ Python 버전: $(python3 --version)"
echo ""

# 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ backend 디렉토리를 찾을 수 없습니다."
    exit 1
fi

cd "$BACKEND_DIR"

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
    echo "✅ 가상환경 생성 완료"
    echo ""
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화..."
source venv/bin/activate

# 의존성 설치
if [ ! -f "venv/.installed" ]; then
    echo "📦 의존성 설치 중..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 의존성 설치 실패"
        exit 1
    fi
    touch venv/.installed
    echo "✅ 의존성 설치 완료"
    echo ""
fi

# 포트 확인
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  포트 8000이 이미 사용 중입니다."
    echo "다른 포트를 사용하거나 기존 프로세스를 종료하세요."
    lsof -i :8000
    exit 1
fi

echo "🌐 백엔드 서버 시작..."
echo "📍 API URL: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# 서버 실행
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000




