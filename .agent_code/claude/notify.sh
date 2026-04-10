#!/bin/bash
INPUT=$(cat 2>/dev/null || echo "{}")
EVENT=$(echo "$INPUT" | python -c 'import json, sys; d=json.load(sys.stdin) if not sys.stdin.isatty() else {}; print(d.get("hook_event_name", ""))' 2>/dev/null)

if [ "$EVENT" = "Stop" ]; then
  BODY="Task completed."
else
  BODY="Needs your attention."
fi

if command -v notify-send >/dev/null 2>&1; then
  if command -v paplay >/dev/null 2>&1 && [ -f /usr/share/sounds/freedesktop/stereo/message.oga ]; then
    paplay /usr/share/sounds/freedesktop/stereo/message.oga >/dev/null 2>&1 || true
  elif command -v canberra-gtk-play >/dev/null 2>&1; then
    canberra-gtk-play -i message >/dev/null 2>&1 || true
  else
    printf '\a'
  fi
  notify-send "Claude Code" "$BODY"
elif command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$HOME/.claude/notify.ps1" -EventName "$EVENT"
fi
