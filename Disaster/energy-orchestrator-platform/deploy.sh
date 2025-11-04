#!/bin/bash

# Energy Orchestrator Platform - 배포 스크립트
# 프로덕션 환경 배포를 위한 스크립트

set -e  # 에러 발생 시 중단

echo "🚀 Energy Orchestrator Platform 배포 시작"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 환경 확인
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다.${NC}"
    echo "   .env.example을 복사하여 .env 파일을 생성하세요."
    echo ""
    read -p ".env 파일을 지금 생성하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
            echo -e "${YELLOW}⚠️  .env 파일을 편집하여 프로덕션 설정을 입력하세요.${NC}"
            echo ""
        else
            echo -e "${RED}❌ .env.example 파일이 없습니다.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ .env 파일이 필요합니다.${NC}"
        exit 1
    fi
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 및 Docker Compose 확인 완료${NC}"
echo ""

# 가상 데이터 생성
echo "📦 가상 데이터 생성 중..."
cd backend
if [ -f "scripts/generate_mock_data.py" ]; then
    python3 scripts/generate_mock_data.py || echo -e "${YELLOW}⚠️  가상 데이터 생성 실패 (계속 진행)${NC}"
    echo ""
fi
cd ..

# Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose -f docker-compose.prod.yml build --no-cache

# 기존 컨테이너 중지 및 제거
echo ""
echo "🛑 기존 컨테이너 중지 중..."
docker-compose -f docker-compose.prod.yml down

# 볼륨 확인
echo ""
read -p "데이터베이스 볼륨을 초기화하시겠습니까? (주의: 모든 데이터가 삭제됩니다) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  볼륨 삭제 중..."
    docker-compose -f docker-compose.prod.yml down -v
fi

# 서비스 시작
echo ""
echo "🚀 서비스 시작 중..."
docker-compose -f docker-compose.prod.yml up -d

# 서비스 상태 확인
echo ""
echo "⏳ 서비스 시작 대기 중..."
sleep 10

# Health check
echo ""
echo "🏥 Health Check 중..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend 서비스 정상 작동${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend 서비스 시작 실패${NC}"
        docker-compose -f docker-compose.prod.yml logs backend
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
printf '=%.0s' {1..50}
echo ""
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo ""
echo "📍 서비스 접속 정보:"
echo "   • Frontend: http://localhost:${FRONTEND_PORT:-3000}"
echo "   • Backend API: http://localhost:${BACKEND_PORT:-8000}"
echo "   • API Docs: http://localhost:${BACKEND_PORT:-8000}/docs"
echo ""
echo "📊 로그 확인:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 서비스 중지:"
echo "   docker-compose -f docker-compose.prod.yml down"
printf '=%.0s' {1..50}
echo ""

