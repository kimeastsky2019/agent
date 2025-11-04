#!/bin/bash

# Energy Orchestrator Platform - 서버 배포 스크립트
# 사용법: ./deploy-to-server.sh [KEY_FILE_PATH]

set -e

# 서버 정보
SERVER_IP="34.64.248.144"
SERVER_USER="metal"
SERVER_DIR="/opt/energy-orchestrator"
DOMAIN="agent.gngmeta.com"

# 키 파일 경로
if [ -n "$1" ]; then
    KEY_FILE="$1"
else
    # 기본 경로들 시도
    KEY_FILE=""
    for path in \
        "./energy-orchestrator-platform.pem" \
        "~/energy-orchestrator-platform.pem" \
        "~/.ssh/energy-orchestrator-platform.pem" \
        "/Users/donghokim/energy-orchestrator-platform.pem"
    do
        expanded_path=$(eval echo "$path")
        if [ -f "$expanded_path" ]; then
            KEY_FILE="$expanded_path"
            break
        fi
    done
fi

if [ -z "$KEY_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "❌ 키 파일을 찾을 수 없습니다."
    echo ""
    echo "사용법: $0 [KEY_FILE_PATH]"
    echo ""
    echo "예시:"
    echo "  $0 ./energy-orchestrator-platform.pem"
    echo "  $0 ~/.ssh/energy-orchestrator-platform.pem"
    exit 1
fi

# 키 파일 권한 확인
chmod 600 "$KEY_FILE"

echo "🔑 키 파일: $KEY_FILE"
echo "🌐 서버: $SERVER_USER@$SERVER_IP"
echo "📁 배포 경로: $SERVER_DIR"
echo ""

# SSH 옵션
SSH_OPTS="-F /dev/null -i $KEY_FILE -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# 서버 접속 테스트
echo "🔍 서버 접속 테스트 중..."
if ! ssh $SSH_OPTS $SERVER_USER@$SERVER_IP "echo 'Connection OK'" > /dev/null 2>&1; then
    echo "❌ 서버 접속 실패"
    exit 1
fi
echo "✅ 서버 접속 성공"
echo ""

# 서버 정보 확인
echo "📊 서버 정보 확인 중..."
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP "uname -a && docker --version 2>/dev/null || echo 'Docker not installed' && docker-compose --version 2>/dev/null || echo 'Docker Compose not installed'"
echo ""

# 프로젝트 디렉토리 확인
echo "📦 프로젝트 디렉토리 준비 중..."
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP "sudo mkdir -p $SERVER_DIR && sudo chown $SERVER_USER:$SERVER_USER $SERVER_DIR || mkdir -p $SERVER_DIR"
echo "✅ 디렉토리 준비 완료"
echo ""

# 파일 업로드 (tar + scp 사용)
echo "📤 프로젝트 파일 업로드 중..."
echo "   tar + scp 사용 중..."

# 임시 tar 파일 생성
TAR_FILE="/tmp/energy-orchestrator-$(date +%s).tar.gz"
echo "   압축 파일 생성 중..."

cd "$(dirname "$0")"
tar -czf "$TAR_FILE" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='.DS_Store' \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='*.tar.gz' \
    --exclude='*.log' \
    . > /dev/null 2>&1

echo "   서버에 업로드 중..."
# 서버에 업로드
scp $SSH_OPTS "$TAR_FILE" $SERVER_USER@$SERVER_IP:/tmp/energy-orchestrator.tar.gz

# 서버에서 압축 해제
echo "   서버에서 압축 해제 중..."
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP "mkdir -p $SERVER_DIR && cd $SERVER_DIR && tar -xzf /tmp/energy-orchestrator.tar.gz && rm -f /tmp/energy-orchestrator.tar.gz"

# 로컬 임시 파일 삭제
rm -f "$TAR_FILE"

echo "✅ 파일 업로드 완료"
echo ""

# 서버에서 배포 실행
echo "🚀 서버에서 배포 실행 중..."
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP "DOMAIN='$DOMAIN' SERVER_DIR='$SERVER_DIR' bash -s" << 'ENDSSH'
cd $SERVER_DIR

# 환경 변수 파일 확인 및 설정
if [ ! -f ".env" ]; then
    echo "📝 .env 파일 생성 중..."
    if [ -f "env.example" ]; then
        cp env.example .env
        # 도메인 정보로 환경 변수 업데이트
        sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN|g" .env
        sed -i "s|VITE_API_URL=.*|VITE_API_URL=https://$DOMAIN/api|g" .env
        sed -i "s|VITE_WS_URL=.*|VITE_WS_URL=wss://$DOMAIN/ws|g" .env
        sed -i "s|KAFKA_EXTERNAL_HOST=.*|KAFKA_EXTERNAL_HOST=$DOMAIN|g" .env
        echo "✅ .env 파일 생성 및 도메인 설정 완료"
        echo "⚠️  보안을 위해 비밀번호를 반드시 변경하세요!"
    else
        echo "❌ env.example 파일이 없습니다."
        exit 1
    fi
else
    # 기존 .env 파일의 도메인 정보 업데이트
    echo "📝 기존 .env 파일 업데이트 중..."
    sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN|g" .env || true
    sed -i "s|VITE_API_URL=.*|VITE_API_URL=https://$DOMAIN/api|g" .env || true
    sed -i "s|VITE_WS_URL=.*|VITE_WS_URL=wss://$DOMAIN/ws|g" .env || true
    sed -i "s|KAFKA_EXTERNAL_HOST=.*|KAFKA_EXTERNAL_HOST=$DOMAIN|g" .env || true
    echo "✅ .env 파일 업데이트 완료"
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "📦 Docker 설치 중..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Docker Compose 설치 중..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 가상 데이터 생성
echo "📊 가상 데이터 생성 중..."
cd backend
if [ -f "scripts/generate_mock_data.py" ]; then
    python3 scripts/generate_mock_data.py || echo "⚠️  가상 데이터 생성 실패 (계속 진행)"
fi
cd ..

# Docker 이미지 빌드 및 시작
echo "🔨 Docker 이미지 빌드 중..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🛑 기존 서비스 중지 중..."
docker-compose -f docker-compose.prod.yml down || true

echo "🚀 서비스 시작 중..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ 서비스 시작 대기 중..."
sleep 15

# Health check
echo "🏥 Health Check 중..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend 서비스 정상 작동"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend 서비스 시작 실패"
        docker-compose -f docker-compose.prod.yml logs backend | tail -50
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "=========================================="
echo "✅ 배포 완료!"
echo ""
echo "📍 서비스 접속 정보:"
echo "   • Frontend: http://agent.gngmeta.com (또는 http://34.64.248.144)"
echo "   • Backend API: http://agent.gngmeta.com/api (또는 http://34.64.248.144:8000)"
echo "   • API Docs: http://agent.gngmeta.com/api/docs"
echo ""
echo "📊 로그 확인:"
echo "   ssh -i $KEY_FILE $SERVER_USER@$SERVER_IP 'cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml logs -f'"
echo "=========================================="
ENDSSH

echo ""
echo "✅ 배포 완료!"
echo ""
echo "다음 명령어로 서버에 접속할 수 있습니다:"
echo "  ssh -i $KEY_FILE $SERVER_USER@$SERVER_IP"


