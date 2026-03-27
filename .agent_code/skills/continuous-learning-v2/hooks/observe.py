#!/usr/bin/env python3
"""
Continuous Learning v2 - Portable observation hook.

Captures tool-use hook payloads from supported agents and appends normalized
events to observations.jsonl under CONTINUOUS_LEARNING_HOME.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_HOME = Path.home() / ".claude" / "homunculus"
MAX_FILE_SIZE_MB = 10


def resolve_runtime_home(payload: dict) -> Path:
    raw_home = os.environ.get("CONTINUOUS_LEARNING_HOME")
    if raw_home:
        home = Path(raw_home).expanduser()
        if not home.is_absolute():
            base_dir = Path(payload.get("cwd") or os.getcwd())
            home = (base_dir / home).resolve()
        return home
    return DEFAULT_HOME


def compact_json(value, limit=5000):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=True)
    else:
        text = str(value)
    return text[:limit]


def parse_event(payload: dict) -> dict:
    hook_name = (
        payload.get("hookEventName")
        or payload.get("hook_event_name")
        or payload.get("hook_type")
        or "unknown"
    )
    hook_name_lower = str(hook_name).lower()

    tool_name = (
        payload.get("toolName")
        or payload.get("tool_name")
        or payload.get("tool")
        or "unknown"
    )

    tool_input = (
        payload.get("toolInput")
        or payload.get("tool_input")
        or payload.get("input")
    )
    tool_output = (
        payload.get("toolOutput")
        or payload.get("tool_output")
        or payload.get("output")
    )
    session_id = (
        payload.get("sessionId")
        or payload.get("session_id")
        or payload.get("conversationId")
        or "unknown"
    )

    if "pretooluse" in hook_name_lower or "pre_tool_use" in hook_name_lower:
        event_name = "tool_start"
    elif "posttooluse" in hook_name_lower or "post_tool_use" in hook_name_lower:
        event_name = "tool_complete"
    else:
        event_name = hook_name_lower or "unknown"

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": event_name,
        "tool": tool_name,
        "session": session_id,
    }

    input_text = compact_json(tool_input)
    output_text = compact_json(tool_output)

    if input_text and event_name == "tool_start":
        event["input"] = input_text
    if output_text and event_name == "tool_complete":
        event["output"] = output_text

    return event


def archive_if_needed(target_file: Path):
    if not target_file.exists():
        return
    size_mb = target_file.stat().st_size / (1024 * 1024)
    if size_mb < MAX_FILE_SIZE_MB:
        return

    archive_dir = target_file.parent / "observations.archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    shutil.move(str(target_file), str(archive_dir / f"observations-{timestamp}.jsonl"))


def main():
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        print(json.dumps({"continue": True}))
        return 0

    try:
        payload = json.loads(raw_input)
    except Exception:
        payload = {"raw": raw_input}

    runtime_home = resolve_runtime_home(payload)
    runtime_home.mkdir(parents=True, exist_ok=True)

    if (runtime_home / "disabled").exists():
        print(json.dumps({"continue": True}))
        return 0

    observations_file = runtime_home / "observations.jsonl"
    archive_if_needed(observations_file)

    event = parse_event(payload)
    with observations_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True) + "\n")

    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
