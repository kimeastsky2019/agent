#!/bin/bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent

# Git 리포지토리 초기화 (이미 있으면 스킵)
if [ ! -d .git ]; then
    git init
fi

# 원격 저장소 설정
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/kimeastsky2019/AI_Agent.git

# .gitignore 파일 생성 (필요한 경우)
if [ ! -f .gitignore ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Node
node_modules/
dist/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
*.tar.gz
*.zip
*.backup
*.db

# Temporary
*.tmp
*.temp
EOF
fi

# 모든 파일 추가
git add .

# 커밋
git commit -m "feat: initial commit - AI Agent services and infrastructure" || echo "No changes to commit"

# 푸시
git branch -M main
git push -u origin main --force

echo "Git push completed!"

