# 배포 가이드

## 배포 스크립트 준비 완료

다음 스크립트들이 준비되었습니다:

1. **deploy-full.sh** - 전체 배포 (애플리케이션 + 도메인 설정)
2. **deploy-to-server.sh** - 애플리케이션만 배포
3. **setup-domain.sh** - 도메인 설정만 실행

## 서버 정보

- **IP**: 34.64.248.144
- **사용자**: metal
- **도메인**: agent.gngmeta.com
- **SSH 키**: energy-orchestrator-platform.pem

## 배포 실행

### 전체 배포 (권장)

```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent/Disaster/energy-orchestrator-platform

# 키 파일 경로 지정
./deploy-full.sh /path/to/energy-orchestrator-platform.pem

# 또는 키 파일이 프로젝트 디렉토리에 있는 경우
./deploy-full.sh
```

### 단계별 배포

```bash
# 1. 애플리케이션 배포
./deploy-to-server.sh /path/to/energy-orchestrator-platform.pem

# 2. 도메인 설정 (애플리케이션 배포 후)
./setup-domain.sh /path/to/energy-orchestrator-platform.pem
```

## 사전 준비사항

1. **DNS 설정 확인**: `agent.gngmeta.com`이 `34.64.248.144`로 설정되어 있어야 합니다.
2. **SSH 키 파일**: `energy-orchestrator-platform.pem` 파일이 필요합니다.
3. **서버 접근**: 서버에 SSH 접근이 가능해야 합니다.

## 배포 후 확인

배포가 완료되면 다음 URL로 접속할 수 있습니다:

- Frontend: https://agent.gngmeta.com
- Backend API: https://agent.gngmeta.com/api
- API Docs: https://agent.gngmeta.com/docs

## 문제 해결

### SSH 키 파일 찾기

```bash
# 현재 디렉토리에서 찾기
ls -la energy-orchestrator-platform.pem

# 홈 디렉토리에서 찾기
ls -la ~/energy-orchestrator-platform.pem
ls -la ~/.ssh/energy-orchestrator-platform.pem
```

### 키 파일 권한 설정

```bash
chmod 600 energy-orchestrator-platform.pem
```

### 서버 상태 확인

```bash
ssh -i energy-orchestrator-platform.pem metal@34.64.248.144 \
  'cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml ps'
```

### 로그 확인

```bash
ssh -i energy-orchestrator-platform.pem metal@34.64.248.144 \
  'cd /opt/energy-orchestrator && docker-compose -f docker-compose.prod.yml logs -f'
```

