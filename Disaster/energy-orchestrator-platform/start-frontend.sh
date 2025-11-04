#!/bin/bash

# 프론트엔드 시작 스크립트

echo "🚀 Energy Orchestrator Platform - Frontend 시작"
echo ""

# Node.js 확인
if ! command -v node &> /dev/null; then
    echo "❌ Node.js가 설치되어 있지 않습니다."
    echo ""
    echo "설치 방법:"
    echo "1. Homebrew: brew install node"
    echo "2. 또는 https://nodejs.org/ 에서 다운로드"
    exit 1
fi

echo "✅ Node.js 버전: $(node --version)"
echo "✅ npm 버전: $(npm --version)"
echo ""

# 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ frontend 디렉토리를 찾을 수 없습니다."
    exit 1
fi

cd "$FRONTEND_DIR"

# node_modules 확인
if [ ! -d "node_modules" ]; then
    echo "📦 의존성 설치 중..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 의존성 설치 실패"
        exit 1
    fi
    echo "✅ 의존성 설치 완료"
    echo ""
fi

# 포트 확인
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  포트 3000이 이미 사용 중입니다."
    echo "다른 포트를 사용하거나 기존 프로세스를 종료하세요."
    lsof -i :3000
    exit 1
fi

echo "🌐 프론트엔드 서버 시작..."
echo "📍 접속 URL: http://localhost:3000"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# 개발 서버 실행
npm run dev




