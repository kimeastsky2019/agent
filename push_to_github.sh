#!/bin/bash
set -e

cd /Users/donghokim/Documents/myworkspace/AI_Agent

echo "=== Git 리포지토리 초기화 ==="
if [ ! -d .git ]; then
    git init
    echo "Git 리포지토리 초기화 완료"
else
    echo "이미 Git 리포지토리가 있습니다"
fi

echo ""
echo "=== 원격 저장소 설정 ==="
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/kimeastsky2019/AI_Agent.git
echo "원격 저장소 설정 완료: https://github.com/kimeastsky2019/AI_Agent.git"

echo ""
echo "=== 파일 추가 ==="
git add .
echo "파일 추가 완료"

echo ""
echo "=== 커밋 ==="
git commit -m "feat: initial commit - AI Agent services and infrastructure" || echo "변경사항이 없거나 이미 커밋되었습니다"

echo ""
echo "=== 브랜치 설정 ==="
git branch -M main

echo ""
echo "=== GitHub에 푸시 ==="
echo "원격 저장소에 푸시합니다..."
git push -u origin main || {
    echo ""
    echo "푸시 실패. 이미 원격 저장소에 내용이 있을 수 있습니다."
    echo "강제 푸시를 원하시면 다음 명령어를 실행하세요:"
    echo "  git push -u origin main --force"
    exit 1
}

echo ""
echo "✅ GitHub 푸시 완료!"
echo "리포지토리: https://github.com/kimeastsky2019/AI_Agent.git"

