#!/bin/bash
# Markdown → PDF (pandoc + xelatex)
# 사용: ./md_to_pdf.sh path/to/report.md

set -e

if [ -z "$1" ]; then
    echo "사용법: $0 <input.md>"
    exit 1
fi

INPUT="$1"
BASENAME="${INPUT%.md}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/report_template.tex"

if [ ! -f "$TEMPLATE" ]; then
    echo "❌ 템플릿 없음: $TEMPLATE"
    exit 1
fi

# pandoc 존재 확인
if ! command -v pandoc &> /dev/null; then
    echo "❌ pandoc 미설치. brew install pandoc 필요"
    exit 1
fi

# 변환
pandoc "$INPUT" \
    --template="$TEMPLATE" \
    --pdf-engine=xelatex \
    -o "${BASENAME}.pdf" 2>&1

if [ -f "${BASENAME}.pdf" ]; then
    echo "✅ 생성: ${BASENAME}.pdf"
    open "${BASENAME}.pdf" 2>/dev/null || true
else
    echo "❌ PDF 생성 실패"
    exit 1
fi
