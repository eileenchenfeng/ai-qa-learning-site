#!/usr/bin/env bash
set -euo pipefail

# 说明：这个脚本只做“本地预览/落盘”，不发消息。
# 真实发送请用：python3 scripts/feishu_daily_cards.py --date YYYY-MM-DD --chat-id oc_xxx --send

DATE="${1:-}"
if [[ -z "$DATE" ]]; then
  echo "Usage: bash scripts/feishu_card_preview.sh YYYY-MM-DD" >&2
  exit 2
fi

mkdir -p temp
python3 scripts/feishu_daily_cards.py \
  --date "$DATE" \
  --out "temp/daily_ai_content_card_${DATE}.json"

echo "\nPreview JSON saved to: temp/daily_ai_content_card_${DATE}.json"