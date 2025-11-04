#!/bin/bash

echo "🛡️ PREACT 지능형 안전 관제 시스템"
echo "=================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python 버전 확인
echo -e "${BLUE}[1/4]${NC} Python 버전 확인..."
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 확인 완료${NC}"
echo ""

# 패키지 설치
echo -e "${BLUE}[2/4]${NC} 필요한 패키지 설치 중..."
cd backend
pip install -r requirements.txt --break-system-packages --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 패키지 설치 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 패키지 설치 완료${NC}"
echo ""

# 디렉토리 생성
echo -e "${BLUE}[3/4]${NC} 데이터 디렉토리 확인..."
mkdir -p ../data ../logs
echo -e "${GREEN}✓ 디렉토리 준비 완료${NC}"
echo ""

# 서버 시작
echo -e "${BLUE}[4/4]${NC} 백엔드 서버 시작..."
echo ""
echo "=================================="
echo -e "${GREEN}시스템이 시작되었습니다!${NC}"
echo "=================================="
echo ""
echo "📍 백엔드 API: http://localhost:5000"
echo "📍 대시보드: frontend/dashboard.html 파일을 브라우저에서 열어주세요"
echo ""
echo "⚠️  서버를 종료하려면 Ctrl+C를 누르세요"
echo ""

python app.py
