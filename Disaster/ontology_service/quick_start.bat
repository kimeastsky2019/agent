@echo off
echo ======================================
echo 온톨로지 구축 서비스 - 빠른 시작
echo ======================================
echo.

REM 가상환경 생성
echo 1. Python 가상환경 생성 중...
python -m venv venv

REM 가상환경 활성화
echo 2. 가상환경 활성화...
call venv\Scripts\activate.bat

REM 패키지 설치
echo 3. 필요한 패키지 설치 중...
pip install -r requirements.txt

REM 디렉토리 생성
echo 4. 필요한 디렉토리 생성...
if not exist "uploads" mkdir uploads
if not exist "ontologies" mkdir ontologies

echo.
echo ======================================
echo 설치 완료!
echo ======================================
echo.
echo 서버 실행 방법:
echo   python app.py
echo.
echo 웹 인터페이스 접속:
echo   브라우저에서 frontend.html 파일을 열거나
echo   python -m http.server 8080
echo   그 다음 http://localhost:8080/frontend.html 접속
echo.
echo API 테스트:
echo   python test_api.py
echo.
pause
