FROM python:3.10-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY app.py .
COPY dashboard.html .
COPY generate_demo_data.py .
COPY test_system.py .

# 데이터 디렉토리 생성
RUN mkdir -p data logs

# 포트 노출
EXPOSE 5001

# 애플리케이션 실행
CMD ["python", "app.py"]

