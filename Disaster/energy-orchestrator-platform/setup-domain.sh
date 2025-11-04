#!/bin/bash

# Energy Orchestrator Platform - 도메인 설정 스크립트
# 사용법: ./setup-domain.sh [KEY_FILE_PATH]

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
    exit 1
fi

chmod 600 "$KEY_FILE"

echo "🔑 키 파일: $KEY_FILE"
echo "🌐 서버: $SERVER_USER@$SERVER_IP"
echo "🌍 도메인: $DOMAIN"
echo ""

SSH_OPTS="-F /dev/null -i $KEY_FILE -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# 서버에서 Nginx 및 도메인 설정
echo "🚀 도메인 설정 중..."
ssh $SSH_OPTS $SERVER_USER@$SERVER_IP << ENDSSH
set -e

cd $SERVER_DIR

# Nginx 설치 확인 및 설치
if ! command -v nginx &> /dev/null; then
    echo "📦 Nginx 설치 중..."
    sudo apt-get update
    sudo apt-get install -y nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
fi

# Nginx 설정 파일 생성
echo "📝 Nginx 설정 파일 생성 중..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << NGINXCONF
# HTTP -> HTTPS 리다이렉트
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Let's Encrypt 인증을 위한 경로
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # HTTPS로 리다이렉트 (SSL 설정 후)
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS 서버 설정
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL 인증서 경로 (Let's Encrypt로 생성)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 보안 헤더
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # Frontend (React 앱)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # 타임아웃 설정
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # 타임아웃 설정
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket 타임아웃 설정
        proxy_read_timeout 86400;
    }

    # API 문서
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 정적 파일 캐싱
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://localhost:3000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINXCONF

# Nginx 사이트 활성화
echo "🔗 Nginx 사이트 활성화 중..."
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# 기본 사이트 비활성화 (선택사항)
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Nginx 설정 테스트
echo "🧪 Nginx 설정 테스트 중..."
sudo nginx -t

# Certbot 설치 및 SSL 인증서 발급
if ! command -v certbot &> /dev/null; then
    echo "📦 Certbot 설치 중..."
    sudo apt-get install -y certbot python3-certbot-nginx
fi

echo "🔒 SSL 인증서 발급 중..."
echo "⚠️  DNS가 $DOMAIN을 $SERVER_IP로 가리키도록 설정되어 있어야 합니다."
echo ""

# Certbot으로 SSL 인증서 발급
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect || {
    echo "⚠️  SSL 인증서 발급 실패. HTTP로 먼저 설정합니다."
    # SSL 없이 HTTP만 설정
    sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << NGINXHTTP
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # Frontend (React 앱)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # API 문서
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINXHTTP
    sudo nginx -t
}

# Nginx 재시작
echo "🔄 Nginx 재시작 중..."
sudo systemctl reload nginx || sudo systemctl restart nginx

# 방화벽 설정
echo "🔥 방화벽 설정 중..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 22/tcp
    sudo ufw --force enable || true
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
fi

echo ""
echo "=========================================="
echo "✅ 도메인 설정 완료!"
echo ""
echo "📍 접속 정보:"
echo "   • Frontend: http://$DOMAIN (또는 https://$DOMAIN)"
echo "   • Backend API: http://$DOMAIN/api"
echo "   • API Docs: http://$DOMAIN/docs"
echo ""
echo "⚠️  DNS 설정 확인:"
echo "   $DOMAIN -> $SERVER_IP"
echo "   www.$DOMAIN -> $SERVER_IP"
echo ""
echo "📝 SSL 인증서 재발급 (필요시):"
echo "   sudo certbot renew"
echo "=========================================="
ENDSSH

echo ""
echo "✅ 도메인 설정 완료!"

