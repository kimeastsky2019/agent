#!/bin/bash

# Energy Orchestrator Platform - 전체 배포 스크립트 (배포 + 도메인 설정)
# 사용법: ./deploy-full.sh [KEY_FILE_PATH]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 키 파일 경로
KEY_FILE=""
if [ -n "$1" ]; then
    KEY_FILE="$1"
else
    for path in \
        "./energy-orchestrator-platform.pem" \
        "~/energy-orchestrator-platform.pem" \
        "~/.ssh/energy-orchestrator-platform.pem" \
        "/Users/donghokim/energy-orchestrator-platform.pem" \
        "/Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/energy-orchestrator-platform.pem"
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

echo "=========================================="
echo "🚀 Energy Orchestrator Platform 배포"
echo "=========================================="
echo ""

# 1단계: 애플리케이션 배포
echo "📦 1단계: 애플리케이션 배포 중..."
chmod +x deploy-to-server.sh
./deploy-to-server.sh "$KEY_FILE"

if [ $? -ne 0 ]; then
    echo "❌ 애플리케이션 배포 실패"
    exit 1
fi

echo ""
echo "✅ 애플리케이션 배포 완료"
echo ""

# 잠시 대기 (서비스 시작 대기)
echo "⏳ 서비스 시작 대기 중..."
sleep 10

# 2단계: 도메인 설정
echo ""
echo "🌍 2단계: 도메인 설정 중..."
chmod +x setup-domain.sh
./setup-domain.sh "$KEY_FILE"

if [ $? -ne 0 ]; then
    echo "⚠️  도메인 설정 중 오류 발생 (계속 진행)"
fi

echo ""
echo "=========================================="
echo "✅ 전체 배포 완료!"
echo "=========================================="
echo ""
echo "📍 접속 정보:"
echo "   • Frontend: https://agent.gngmeta.com"
echo "   • Backend API: https://agent.gngmeta.com/api"
echo "   • API Docs: https://agent.gngmeta.com/docs"
echo ""
echo "📊 서비스 상태 확인:"
echo "   ssh -i $KEY_FILE metal@34.64.248.144 'cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml ps'"
echo ""
echo "📋 로그 확인:"
echo "   ssh -i $KEY_FILE metal@34.64.248.144 'cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml logs -f'"
echo ""
echo "⚠️  중요:"
echo "   1. DNS 설정 확인: agent.gngmeta.com -> 34.64.248.144"
echo "   2. .env 파일의 비밀번호를 강력한 값으로 변경하세요"
echo "   3. SSL 인증서가 자동으로 발급되었는지 확인하세요"
echo "=========================================="

