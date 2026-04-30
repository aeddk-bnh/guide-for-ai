import sys
import json
import re

def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)
        input_data = json.loads(raw_input)
    except Exception:
        sys.exit(0)
        
    event_name = input_data.get("hook_event_name")
    
    if event_name == "PreCompact":
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreCompact",
                "custom_instructions": "Keep the summary extremely concise to save tokens. Focus only on the core problem and solution. Omit file paths, minor details, and long code blocks."
            }
        }))
        sys.exit(0)
        
    elif event_name == "PreToolUse":
        tool_name = input_data.get("tool_name")
        if tool_name == "Bash":
            command = input_data.get("tool_input", {}).get("command", "")
            
            # Simple heuristic: block potentially massive outputs
            block_reasons = []
            if re.search(r'\bcat\s+(?:[^|>]+)(?:\.json|\.log|\.csv|\.md)\b', command, re.IGNORECASE) and '|' not in command and 'head' not in command and 'grep' not in command:
                block_reasons.append("Use 'head' or 'grep' instead of 'cat' on potentially large files to save tokens.")
            elif re.search(r'\bls\s+-[lA]*R[lA]*\b', command):
                block_reasons.append("Recursive 'ls' output is too large. Use 'find' with -maxdepth or target a specific directory.")
            elif re.search(r'\btree\b', command) and '-L' not in command:
                block_reasons.append("Use 'tree -L 1' or similar to limit depth and save tokens.")
            elif re.search(r'\b(npm|yarn|pnpm|pip)\s+(install|add|update)\b', command) and not re.search(r'(-q|--quiet|> /dev/null)', command):
                block_reasons.append("Package manager installations generate too much log output. Please append '-q', '--quiet' or redirect to '/dev/null'.")
            elif re.search(r'\bcurl\b', command) and not re.search(r'(-s|--silent|>|-o)', command):
                block_reasons.append("Use 'curl -s' or redirect output to a file. Raw curl output can consume too many tokens.")
                
            if block_reasons:
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": " ".join(block_reasons)
                    }
                }))
                sys.exit(0)
                
        elif tool_name == "GlobTool":
            pattern = input_data.get("tool_input", {}).get("pattern", "")
            if pattern in ["*", "**/*", ".*", "**/.*"]:
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Unrestricted glob patterns return too many files. Please use a more specific pattern to save tokens."
                    }
                }))
                sys.exit(0)
                
        elif tool_name == "FileRead":
            file_path = input_data.get("tool_input", {}).get("file_path", "")
            if file_path.endswith((".log", ".csv", ".min.js", ".map")):
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Reading large raw data/log files directly is token-expensive. Use 'GrepTool' or 'Bash' with 'head'/'grep' instead."
                    }
                }))
                sys.exit(0)
                
    # If no intervention, exit 0 with empty/no output or continue
    sys.exit(0)

if __name__ == "__main__":
    main()
