#!/bin/bash
set -e

# 이슈 번호로 브랜치를 생성하고 Ruff fix GitHub Action을 실행하는 스크립트
# PR 생성은 GitHub Action에서 자동으로 처리됩니다.
# 사용법: ./ruff-fix-pr.sh <issue-number> [base-branch]
# 예시: ./ruff-fix-pr.sh 42
# 예시: ./ruff-fix-pr.sh 42 main

ISSUE_NUMBER=$1
BASE_BRANCH=${2:-dev}

if [[ -z "$ISSUE_NUMBER" ]]; then
    echo "사용법: $0 <issue-number> [base-branch]"
    echo "예시: $0 42"
    echo "예시: $0 42 main"
    exit 1
fi

# gh CLI 확인
if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI가 설치되어 있지 않습니다."
    echo "설치: https://cli.github.com/"
    exit 1
fi

# 인증 확인
if ! gh auth status &> /dev/null; then
    echo "Error: gh CLI 인증이 필요합니다."
    echo "실행: gh auth login"
    exit 1
fi

# 이슈 정보 가져오기
echo "📋 이슈 #${ISSUE_NUMBER} 정보 조회 중..."
ISSUE_TITLE=$(gh issue view "$ISSUE_NUMBER" --json title -q '.title' 2>/dev/null)

if [[ -z "$ISSUE_TITLE" ]]; then
    echo "Error: 이슈 #${ISSUE_NUMBER}를 찾을 수 없습니다."
    exit 1
fi

echo "   제목: $ISSUE_TITLE"

# 브랜치 이름 생성 (이슈 제목에서 특수문자 제거)
SAFE_TITLE=$(echo "$ISSUE_TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-50)
BRANCH_NAME="fix/${ISSUE_NUMBER}-${SAFE_TITLE}"

echo ""
echo "🌿 브랜치: $BRANCH_NAME"

# 최신 코드 가져오기
git fetch origin "$BASE_BRANCH"
git fetch origin "$BRANCH_NAME" 2>/dev/null || true

# 브랜치 존재 여부 확인
BRANCH_EXISTS=false
if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
    BRANCH_EXISTS=true
fi

if [[ "$BRANCH_EXISTS" == "true" ]]; then
    echo "⚠️  브랜치가 이미 존재합니다: $BRANCH_NAME"
    read -p "   기존 브랜치를 사용하시겠습니까? (y/n): " USE_EXISTING

    if [[ "$USE_EXISTING" =~ ^[Yy]$ ]]; then
        echo "   기존 브랜치를 사용합니다..."
    else
        echo "   작업을 취소합니다."
        exit 0
    fi
else
    echo "   새 브랜치를 생성합니다..."
    git checkout -b "$BRANCH_NAME" "origin/$BASE_BRANCH"
    git push -u origin "$BRANCH_NAME"
fi

echo ""
echo "🔧 Ruff Fix GitHub Action 실행 중..."

# GitHub Action workflow 실행
gh workflow run ruff.yml \
    -f branch="$BRANCH_NAME" \
    -f base_branch="$BASE_BRANCH" \
    -f issue_number="$ISSUE_NUMBER"

echo ""
echo "🎉 완료!"
echo "   브랜치: $BRANCH_NAME"
echo "   GitHub Actions에서 ruff 수정 및 PR 생성이 진행됩니다."
echo "   진행 상황: https://github.com/$(gh repo view --json nameWithOwner -q '.nameWithOwner')/actions"
