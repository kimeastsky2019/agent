# GitHub에 푸시하기

다음 명령어를 순서대로 실행하세요:

## 1. Git 리포지토리 초기화 (아직 안 했다면)

```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent
git init
```

## 2. 원격 저장소 설정

```bash
git remote add origin https://github.com/kimeastsky2019/AI_Agent.git
# 또는 이미 있다면
git remote set-url origin https://github.com/kimeastsky2019/AI_Agent.git
```

## 3. 모든 파일 추가

```bash
git add .
```

## 4. 커밋

```bash
git commit -m "feat: initial commit - AI Agent services and infrastructure"
```

## 5. 브랜치 설정 및 푸시

```bash
git branch -M main
git push -u origin main
```

## 또는 한 번에 실행

```bash
cd /Users/donghokim/Documents/myworkspace/AI_Agent
chmod +x setup_git.sh
./setup_git.sh
```

## 주의사항

- 큰 파일(backup_*.tar.gz 등)은 .gitignore에 포함되어 있습니다
- 이미 원격 저장소에 내용이 있다면 `--force` 옵션을 사용하지 마세요
- 필요시 `git push -u origin main --force`로 강제 푸시할 수 있습니다 (주의!)

