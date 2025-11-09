# 설치와 로컬 실행 (Docker)

> 한 줄 요약: Docker로 ETModel, ETEngine, ETSource, MyETM을 동시에 구동해 빠르게 시나리오를 테스트할 수 있습니다.

## 무엇을 할 수 있나
- Docker Compose를 사용해 ETModel 스택을 손쉽게 설치·실행
- 로컬 ETEngine과 연동해 시나리오 계산 및 UI 테스트

## 언제/왜 쓰나
- 신규 팀원이 로컬 개발 환경을 신속히 구성해야 할 때
- 운영 전 검증용으로 독립적인 테스트 환경이 필요할 때

## 사용 방법 (Step-by-step)
1. etmodel, etengine, etsource 레포지토리를 동일 상위 폴더에 클론합니다.
2. Docker Compose 또는 각 프로젝트의 Dockerfile로 서비스를 빌드하고 기동합니다.
3. ETModel 환경변수에서 API 엔드포인트를 로컬 ETEngine 주소로 지정한 뒤 브라우저에서 확인합니다.

## 결과 해석 (주요 지표/차트)
- 컨테이너 로그, 헬스체크, API 응답 시간으로 서비스 상태와 연동 여부를 모니터링합니다.

## 주의사항
- 포트 충돌이 발생하면 Docker 포트 매핑을 조정하고, 네트워크 브리지 설정을 확인합니다.
- API 4xx/5xx 오류가 발생하면 ETEngine 로그와 ETSource 마운트 경로를 검증합니다.

## 연결되는 페이지
- [[시스템 구성 (아키텍처)]]
- [[입력과 제약 가이드]]

## 스크린샷/이미지 자리표시자
- ![Docker 실행 화면](./images/docker-setup-01.png)

## 버전/호환성 메모
- ETModel: vX
- ETEngine: vY
- 데이터셋: 국가/지역, 기준연도
