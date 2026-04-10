#!/bin/bash
input=$(cat)

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
else
  echo "Python is required for the Claude Code status line."
  exit 0
fi

parsed=$(
printf '%s' "$input" | "$PYTHON_BIN" -c 'import json, sys

def to_number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def format_cost(value):
    number = to_number(value, 0)
    if number == 0:
        return "0.0000"
    return f"{number:.4f}"

def format_ctx_size(value):
    number = int(to_number(value, 0))
    if number >= 1000000:
        return f"{number // 1000000}M"
    if number >= 1000:
        return f"{number // 1000}K"
    return str(number)

def shorten_path(value):
    if not value:
        return ""
    normalized = value.replace("\\", "/").rstrip("/")
    if not normalized:
        return value
    parts = [part for part in normalized.split("/") if part]
    prefix = ""
    if normalized.startswith("/"):
        prefix = "/"
    if len(parts) <= 2:
        return prefix + "/".join(parts)
    return f".../{parts[-2]}/{parts[-1]}"

data = json.load(sys.stdin)
model = (data.get("model") or {}).get("display_name") or "Unknown"
session_id = (data.get("session_id") or "")[:8]
cost = format_cost((data.get("cost") or {}).get("total_cost_usd"))
context = data.get("context_window") or {}
used_pct = int(to_number(context.get("used_percentage"), 0))
ctx_size = format_ctx_size(context.get("context_window_size"))
dir_value = ((data.get("workspace") or {}).get("current_dir") or data.get("cwd") or "")
short_dir = shorten_path(dir_value)
print("\t".join([model, session_id, cost, str(used_pct), ctx_size, dir_value, short_dir]))')

IFS=$'\t' read -r MODEL SESSION_ID COST PCT CTX_DISPLAY DIR SHORT_DIR <<EOF
$parsed
EOF

[ -z "$DIR" ] && DIR=$(pwd)
[ -z "$SHORT_DIR" ] && SHORT_DIR="$DIR"

PCT=${PCT:-0}

if [ "$PCT" -ge 90 ]; then
  COLOR="\033[31m"
elif [ "$PCT" -ge 70 ]; then
  COLOR="\033[33m"
else
  COLOR="\033[32m"
fi

PATH_COLOR="\033[94m"
MUTED_COLOR="\033[90m"
BRANCH_COLOR="\033[96m"
RESET="\033[0m"

CACHE_KEY=${SESSION_ID:-default}
CACHE_FILE="${TMPDIR:-/tmp}/claude-statusline-git-$CACHE_KEY"
NOW=$(date +%s)
BRANCH=""

cache_mtime() {
  if [ -f "$1" ]; then
    stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0
  else
    echo 0
  fi
}

if [ ! -f "$CACHE_FILE" ] || [ $((NOW - $(cache_mtime "$CACHE_FILE"))) -gt 3 ]; then
  if git -C "$DIR" rev-parse --git-dir >/dev/null 2>&1; then
    GIT_BRANCH=$(git -C "$DIR" branch --show-current 2>/dev/null)
    if [ -z "$GIT_BRANCH" ]; then
      GIT_BRANCH=$(git -C "$DIR" rev-parse --short HEAD 2>/dev/null)
      [ -n "$GIT_BRANCH" ] && GIT_BRANCH="detached@$GIT_BRANCH"
    fi
    if [ -n "$GIT_BRANCH" ]; then
      printf '%s' "$GIT_BRANCH" > "$CACHE_FILE"
    else
      printf '%s' "NO_GIT" > "$CACHE_FILE"
    fi
  else
    printf '%s' "NO_GIT" > "$CACHE_FILE"
  fi
fi

CACHE_CONTENT=$(cat "$CACHE_FILE" 2>/dev/null)
if [ "$CACHE_CONTENT" != "NO_GIT" ] && [ -n "$CACHE_CONTENT" ]; then
  BRANCH=" ${MUTED_COLOR}|${RESET} 🌿 ${BRANCH_COLOR}$CACHE_CONTENT${RESET}"
fi

echo -e "📁 ${PATH_COLOR}$SHORT_DIR${RESET}$BRANCH"
echo -e "🤖 $MODEL ${MUTED_COLOR}|${RESET} Context ${COLOR}$PCT%${RESET} ${MUTED_COLOR}of${RESET} $CTX_DISPLAY"
echo -e "💬 ${MUTED_COLOR}${SESSION_ID:-none}${RESET} ${MUTED_COLOR}|${RESET} 💰 \$$COST"
